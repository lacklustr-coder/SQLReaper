import glob
import json
import logging
import os
import queue
import re
import shlex
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional

from enhancements import autosave, tray
from flask import (  # pyright: ignore[reportMissingImports, reportUnknownVariableType]  # pyright: ignore[reportMissingImports], Response, send_file, session
    Flask,
    jsonify,
    render_template,
    request,
)
from init_features import initialize_all_features
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["RESULTS_FOLDER"] = "results"
app.config["PROFILES_FOLDER"] = "profiles"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

SQLMAP_PATH = os.environ.get("SQLMAP_PATH", "")

for folder in [
    app.config["UPLOAD_FOLDER"],
    app.config["RESULTS_FOLDER"],
    app.config["PROFILES_FOLDER"],
]:
    os.makedirs(folder, exist_ok=True)

# Initialize all new features
socketio = initialize_all_features(app)

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sqlmap_gui")

# Active scans
active_scans = {}
scan_lock = threading.Lock()

# History
HISTORY_FILE = os.path.join(app.config["RESULTS_FOLDER"], "scan_history.json")

# Credentials
CREDS_FILE = os.path.join(app.config["RESULTS_FOLDER"], "creds.json")
DEFAULT_CREDS = {
    "proxy_host": "",
    "proxy_port": "",
    "proxy_user": "",
    "proxy_pass": "",
    "auth_header": "",
}


def load_creds() -> Dict[str, str]:
    try:
        if os.path.exists(CREDS_FILE):
            with open(CREDS_FILE, "r") as f:
                return {**DEFAULT_CREDS, **json.load(f)}
    except Exception as e:
        logger.error(f"Cred load err: {e}")
    return DEFAULT_CREDS.copy()


def save_creds(creds: Dict[str, str]) -> bool:
    try:
        with open(CREDS_FILE, "w") as f:
            json.dump(
                {k: v for k, v in creds.items() if k in DEFAULT_CREDS}, f, indent=2
            )
        return True
    except Exception as e:
        logger.error(f"Cred save err: {e}")
        return False


def load_history() -> List[Dict[str, Any]]:
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"History load err: {e}")
    return []


def save_history(history: List[Dict[str, Any]]) -> None:
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"History save err: {e}")


@lru_cache(maxsize=32)
def get_cached_result(scan_id: str) -> Optional[str]:
    rf = os.path.join(app.config["RESULTS_FOLDER"], f"{scan_id}.txt")
    if os.path.exists(rf):
        with open(rf, "r") as f:
            return f.read()
    return None


def load_profiles() -> List[Dict[str, Any]]:
    profiles = []
    for f in glob.glob(os.path.join(app.config["PROFILES_FOLDER"], "*.json")):
        try:
            with open(f, "r") as fp:
                profiles.append(json.load(fp))
        except Exception as e:
            logger.error(f"Profile load err {f}: {e}")
    return sorted(profiles, key=lambda p: p.get("name", ""))


def options_to_argv(options: Any) -> List[str]:
    """Turn JSON list or shell-like string into argv tokens without breaking on spaces inside quoted values."""
    if options is None:
        return []
    if isinstance(options, list):
        return [str(x) for x in options if x is not None and str(x).strip() != ""]
    s = str(options).strip()
    if not s:
        return []
    try:
        return shlex.split(s, posix=True)
    except ValueError:
        return s.split()


def save_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    pid = data.get("id", str(uuid.uuid4()))
    data["id"] = pid
    data["created_at"] = data.get("created_at", datetime.now().isoformat())
    data["updated_at"] = datetime.now().isoformat()
    fp = os.path.join(app.config["PROFILES_FOLDER"], f"{pid}.json")
    with open(fp, "w") as f:
        json.dump(data, f, indent=2)
    return data


def parse_request_file(filepath: str) -> Dict[str, Any]:
    parsed = {"url": "", "method": "GET", "data": "", "headers": {}, "cookie": ""}
    try:
        with open(filepath, "r") as f:
            content = f.read()
        lines = content.split("\n")
        if not lines:
            return parsed
        req = lines[0].strip().split()
        if len(req) >= 2:
            parsed["method"] = req[0]
            if len(req) >= 3 and req[1].startswith("http"):
                parsed["url"] = req[1]
        i = 1
        while i < len(lines) and lines[i].strip():
            line = lines[i].strip()
            if ": " in line:
                k, v = line.split(": ", 1)
                parsed["headers"][k.lower()] = v
                if k.lower() == "cookie":
                    parsed["cookie"] = v
                elif k.lower() == "host" and not parsed["url"]:
                    parsed["url"] = f"http://{v}"
            i += 1
        if i < len(lines):
            parsed["data"] = "\n".join(lines[i + 1 :]).strip()
    except Exception as e:
        logger.error(f"Parse err: {e}")
    return parsed


def run_scan_process(cmd: List[str], scan_id: str, q: queue.Queue) -> None:
    try:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        out = []
        for line in p.stdout:
            line = line.rstrip()
            out.append(line)
            q.put({"type": "output", "data": line, "scan_id": scan_id})
        p.wait()
        status = "success" if p.returncode == 0 else "error"
        target = active_scans.get(scan_id, {}).get("target", "")
        autosave.save(scan_id, target, "\n".join(out), status, p.returncode)
        q.put(
            {
                "type": "complete",
                "scan_id": scan_id,
                "return_code": p.returncode,
                "output": "\n".join(out),
                "status": status,
            }
        )
        tray.set_status(status.title())
    except Exception as e:
        logger.error(f"Scan err: {e}")
        q.put({"type": "error", "scan_id": scan_id, "error": str(e)})
        tray.set_status("Error")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json or {}
    target = data.get("target") or request.form.get("target")
    if "options" in data:
        options = data["options"]
    else:
        options = request.form.get("options", "") if request.form else ""
    if not target:
        return jsonify({"error": "Target is required"}), 400
    ss = load_settings()
    sqlmap = ss.get("sqlmap_path", SQLMAP_PATH)
    cmd = ["python", sqlmap, "-u", target]
    cmd.extend(options_to_argv(options))
    if "--batch" not in cmd:
        cmd.append("--batch")
    tray.set_status("Running")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout or ""
        status = "success" if result.returncode == 0 else "error"
        scan_id = str(uuid.uuid4())
        result_file = os.path.join(app.config["RESULTS_FOLDER"], f"{scan_id}.txt")
        with open(result_file, "w") as f:
            f.write(output)
        autosave.save(scan_id, target, output, status, result.returncode)
        history = load_history()
        history.insert(
            0,
            {
                "id": scan_id,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "return_code": result.returncode,
                "result_file": result_file,
            },
        )
        history = history[:100]
        save_history(history)
        tray.set_status(status.title())
        return jsonify(
            {
                "output": output,
                "error": result.stderr or "",
                "return_code": result.returncode,
                "scan_id": scan_id,
                "status": status,
            }
        )
    except subprocess.TimeoutExpired:
        tray.set_status("Timeout")
        return jsonify({"error": "Scan timed out (5 min limit)"}), 408
    except FileNotFoundError:
        return jsonify(
            {"error": "sqlmap.py not found. Configure SQLMAP_PATH env var."}
        ), 500
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/api/scan/stream", methods=["POST"])
def scan_stream():
    data = request.json or {}
    target = data.get("target")
    options = data.get("options") if "options" in data else ""
    if not target:
        return jsonify({"error": "Target is required"}), 400
    ss = load_settings()
    sqlmap = ss.get("sqlmap_path", SQLMAP_PATH)
    cmd = ["python", sqlmap, "-u", target]
    cmd.extend(options_to_argv(options))
    if "--batch" not in cmd:
        cmd.append("--batch")
    scan_id = str(uuid.uuid4())
    rq = queue.Queue()
    with scan_lock:
        active_scans[scan_id] = {
            "target": target,
            "cmd": cmd,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "queue": rq,
        }
    t = threading.Thread(target=run_scan_process, args=(cmd, scan_id, rq))
    t.daemon = True
    t.start()
    tray.set_status("Running")
    return jsonify(
        {"scan_id": scan_id, "message": "Scan started", "command": " ".join(cmd)}
    )


@app.route("/api/scan/stop/<scan_id>", methods=["POST"])
def stop_scan(scan_id):
    with scan_lock:
        if scan_id in active_scans:
            active_scans[scan_id]["status"] = "stopping"
            return jsonify({"message": "Scan stop requested"})
    return jsonify({"error": "Scan not found"}), 404


@app.route("/api/scan/status/<scan_id>")
def scan_status(scan_id):
    with scan_lock:
        if scan_id in active_scans:
            s = active_scans[scan_id]
            return jsonify(
                {
                    "scan_id": scan_id,
                    "status": s["status"],
                    "target": s["target"],
                    "start_time": s["start_time"],
                }
            )
    return jsonify({"error": "Scan not found"}), 404


@app.route("/api/scan/<scan_id>/rerun", methods=["POST"])
def rerun_scan(scan_id):
    history = load_history()
    s = next((h for h in history if h.get("id") == scan_id), None)
    if not s:
        return jsonify({"error": "Not found"}), 404
    target = s.get("target", "")
    if target.startswith("Dork:") or target.startswith("Batch"):
        return jsonify({"error": "Cannot rerun"}), 400
    opts = options_to_argv(s.get("options")) if s.get("options") else []
    ss = load_settings()
    sqlmap = ss.get("sqlmap_path", SQLMAP_PATH)
    cmd = ["python", sqlmap, "-u", target] + opts
    if "--batch" not in cmd:
        cmd.append("--batch")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout or ""
        status = "success" if result.returncode == 0 else "error"
        sid = str(uuid.uuid4())
        rf = os.path.join(app.config["RESULTS_FOLDER"], f"{sid}.txt")
        with open(rf, "w") as f:
            f.write(output)
        autosave.save(sid, target, output, status, result.returncode)
        history.insert(
            0,
            {
                "id": sid,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "return_code": result.returncode,
            },
        )
        save_history(history)
        return jsonify({"output": output, "scan_id": sid, "status": status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/results/<scan_id>")
def get_result(scan_id):
    cached = get_cached_result(scan_id)
    if cached:
        return jsonify({"output": cached, "scan_id": scan_id})
    rf = os.path.join(app.config["RESULTS_FOLDER"], f"{scan_id}.txt")
    if os.path.exists(rf):
        with open(rf, "r") as f:
            return jsonify({"output": f.read(), "scan_id": scan_id})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/results/download/<scan_id>", methods=["GET"])
def download_result(scan_id):
    rf = os.path.join(app.config["RESULTS_FOLDER"], f"{scan_id}.txt")
    if os.path.exists(rf):
        return send_file(rf, as_attachment=True, download_name=f"sqlmap_{scan_id}.txt")
    return jsonify({"error": "Not found"}), 404


@app.route("/api/export", methods=["POST"])
def export_results():
    data = request.json or {}
    output_text = data.get("output", "")
    fmt = data.get("format", "txt")
    target = data.get("target", "unknown")
    if not output_text:
        return jsonify({"error": "No output"}), 400
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rdir = app.config["RESULTS_FOLDER"]
    if fmt == "txt":
        content = f"SQLMap Scan Results\n{'=' * 50}\nTarget: {target}\nDate: {datetime.now().isoformat()}\n{'=' * 50}\n\n{output_text}"
        fn = f"sqlmap_{ts}.txt"
    elif fmt == "md":
        content = f"# SQLMap Scan Results\n\n**Target:** {target}\n**Date:** {datetime.now().isoformat()}\n\n```\n{output_text}\n```"
        fn = f"sqlmap_{ts}.md"
    elif fmt == "html":
        content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>SQLMap Results</title><style>body{{font-family:monospace;background:#0a0a0a;color:#00ff44;padding:20px}}pre{{background:#000;padding:15px;border:1px solid #00ff44;border-radius:5px}}</style></head><body><h1>SQLMap</h1><p><strong>Target:</strong> {target} | <strong>Date:</strong> {datetime.now().isoformat()}</p><pre>{output_text}</pre></body></html>"""
        fn = f"sqlmap_{ts}.html"
    elif fmt == "json":
        content = json.dumps(
            {
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "tool": "sqlmap",
                "output": output_text,
            },
            indent=2,
        )
        fn = f"sqlmap_{ts}.json"
    else:
        fn = f"sqlmap_{ts}.txt"
        content = output_text
    fp = os.path.join(rdir, fn)
    with open(fp, "w") as f:
        f.write(content)
    return jsonify(
        {
            "message": "Exported",
            "filename": fn,
            "download_url": f"/api/export/download/{fn}",
        }
    )


@app.route("/api/export/download/<filename>")
def download_export(filename):
    fp = os.path.join(app.config["RESULTS_FOLDER"], filename)
    if os.path.exists(fp) and ".." not in filename:
        return send_file(fp, as_attachment=True)
    return jsonify({"error": "Not found"}), 404


@app.route("/api/history")
def get_history():
    h = load_history()
    return jsonify({"history": h[:50], "total": len(h)})


@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    save_history([])
    return jsonify({"message": "Cleared"})


@app.route("/api/history/<scan_id>", methods=["DELETE"])
def delete_history_item(scan_id):
    h = load_history()
    h = [x for x in h if x.get("id") != scan_id]
    save_history(h)
    return jsonify({"message": "Deleted"})


@app.route("/api/bookmarks", methods=["GET"])
def get_bookmarks():
    h = load_history()
    bm = [x for x in h if x.get("bookmarked")]
    return jsonify({"bookmarks": bm})


@app.route("/api/bookmarks/<scan_id>", methods=["POST"])
def bookmark_scan(scan_id):
    d = request.json or {}
    bk = d.get("bookmarked", True)
    h = load_history()
    for x in h:
        if x.get("id") == scan_id:
            x["bookmarked"] = bk
            break
    save_history(h)
    return jsonify({"message": "Updated"})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    allowed = {".txt", ".sql", ".req", ".http", ".log", ".json", ".xml"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({"error": f"Invalid type. Allowed: {', '.join(allowed)}"}), 400
    fn = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    fp = os.path.join(app.config["UPLOAD_FOLDER"], fn)
    file.save(fp)
    parsed = None
    if ext in (".req", ".http"):
        parsed = parse_request_file(fp)
    return jsonify(
        {"message": "Uploaded", "filepath": fp, "filename": fn, "parsed": parsed}
    )


@app.route("/api/upload/batch", methods=["POST"])
def batch_upload_urls():
    d = request.json or {}
    t = d.get("urls", "")
    if not t:
        return jsonify({"error": "URLs required"}), 400
    urls = [
        u.strip() for u in t.split("\n") if u.strip() and not u.strip().startswith("#")
    ]
    return jsonify(
        {"message": f"Parsed {len(urls)} URLs", "urls": urls, "count": len(urls)}
    )


@app.route("/api/scan/batch", methods=["POST"])
def batch_scan():
    d = request.json or {}
    urls = d.get("urls", [])
    opts = d.get("options", "")
    if not urls:
        return jsonify({"error": "No URLs"}), 400
    if len(urls) > 50:
        return jsonify({"error": "Max 50 URLs"}), 400
    ss = load_settings()
    sqlmap = ss.get("sqlmap_path", SQLMAP_PATH)
    results = []
    for url in urls:
        cmd = ["python", sqlmap, "-u", url]
        cmd.extend(options_to_argv(opts))
        if "--batch" not in cmd:
            cmd.append("--batch")
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            results.append(
                {
                    "url": url,
                    "status": "success" if r.returncode == 0 else "error",
                    "return_code": r.returncode,
                    "output": r.stdout[:2000],
                }
            )
        except subprocess.TimeoutExpired:
            results.append({"url": url, "status": "timeout", "output": "Timed out"})
        except Exception as e:
            results.append({"url": url, "status": "error", "output": str(e)})
    bid = str(uuid.uuid4())
    rf = os.path.join(app.config["RESULTS_FOLDER"], f"batch_{bid}.txt")
    with open(rf, "w") as f:
        for r in results:
            f.write(
                f"\n{'=' * 60}\nURL: {r['url']}\nStatus: {r['status']}\n{'=' * 60}\n{r['output']}\n"
            )
    history = load_history()
    history.insert(
        0,
        {
            "id": bid,
            "target": f"Batch ({len(urls)} URLs)",
            "timestamp": datetime.now().isoformat(),
            "status": "batch",
            "result_file": rf,
            "results": results,
        },
    )
    save_history(history)
    return jsonify({"batch_id": bid, "results": results, "total": len(results)})


@app.route("/api/google-dork", methods=["POST"])
def google_dork_scan():
    d = request.json or {}
    dork = d.get("dork", "")
    if not dork:
        return jsonify({"error": "Dork required"}), 400
    ss = load_settings()
    sqlmap = ss.get("sqlmap_path", SQLMAP_PATH)
    se = d.get("search_engine", "Google")
    if se != "Google":
        return jsonify(
            {
                "error": f'Sqlmap -g flag only works with Google search engine. "{se}" search is not supported for dorking.'
            }
        ), 400
    cmd = ["python", sqlmap, "-g", dork]
    if os.path.basename(os.path.dirname(sqlmap)) == "sqlmap" and os.path.exists(
        os.path.join(sqlmap, "sqlmap.py")
    ):
        cmd = ["python", os.path.join(sqlmap, "sqlmap.py"), "-g", dork]
    elif not os.path.exists(sqlmap) and os.path.exists(
        os.path.join(os.path.dirname(sqlmap), "sqlmap", "sqlmap.py")
    ):
        cmd = [
            "python",
            os.path.join(os.path.dirname(sqlmap), "sqlmap", "sqlmap.py"),
            "-g",
            dork,
        ]
    if d.get("results_limit", "10") != "10":
        cmd.append(f"--results={d['results_limit']}")
    if d.get("start_page", "1") != "1":
        cmd.append(f"--start={d['start_page']}")
    aopt = d.get("additional_options", "")
    cmd.extend(options_to_argv(aopt))
    if d.get("batch", True):
        cmd.append("--batch")
    cmd.append("--flush-session")
    tray.set_status("Running")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        output = result.stdout or ""
        status = "success" if result.returncode == 0 else "error"
        scan_id = str(uuid.uuid4())
        result_file = os.path.join(app.config["RESULTS_FOLDER"], f"{scan_id}.txt")
        with open(result_file, "w") as f:
            f.write(output)
        autosave.save(scan_id, f"Dork: {dork}", output, status, result.returncode)
        history = load_history()
        history.insert(
            0,
            {
                "id": scan_id,
                "target": f"Dork: {dork}",
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "return_code": result.returncode,
                "result_file": result_file,
            },
        )
        save_history(history)
        tray.set_status(status.title())
        return jsonify(
            {
                "output": output,
                "error": result.stderr or "",
                "return_code": result.returncode,
                "command": " ".join(cmd),
                "scan_id": scan_id,
                "status": status,
            }
        )
    except subprocess.TimeoutExpired:
        tray.set_status("Timeout")
        return jsonify(
            {"error": "Dork scan timed out (10 min limit). Try fewer results."}
        ), 408
    except FileNotFoundError:
        return jsonify(
            {"error": f"sqlmap not found at {sqlmap}. Set correct path in settings."}
        ), 500
    except Exception as e:
        tray.set_status("Error")
        return jsonify({"error": f"Error: {str(e)}"}), 500


@app.route("/api/google-dork-multi", methods=["POST"])
def google_dork_multi_scan():
    d = request.json or {}
    t = d.get("dorks", "")
    if not t:
        return jsonify({"error": "Dorks required"}), 400
    dl = [x.strip() for x in t.split("\n") if x.strip()]
    if not dl:
        return jsonify({"error": "No dorks"}), 400
    se = d.get("search_engine", "Google")
    if se != "Google":
        return jsonify(
            {"error": "Only Google search engine is supported for dorking."}
        ), 400
    ss = load_settings()
    sqlmap = ss.get("sqlmap_path", SQLMAP_PATH)
    rl = d.get("results_limit", "10")
    ao = d.get("additional_options", "")
    results = []
    for dork in dl:
        cmd = ["python", sqlmap, "-g", dork]
        if rl != "10":
            cmd.append(f"--results={rl}")
        cmd.extend(options_to_argv(ao))
        cmd.extend(["--batch", "--flush-session"])
        results.append({"dork": dork, "command": " ".join(cmd)})
    return jsonify({"scans": results, "total_dorks": len(dl)})


@app.route("/api/profiles", methods=["GET"])
def list_profiles():
    return jsonify({"profiles": load_profiles()})


@app.route("/api/profiles", methods=["POST"])
def create_profile():
    d = request.json or {}
    if not d.get("name"):
        return jsonify({"error": "Name required"}), 400
    p = save_profile(d)
    return jsonify({"message": "Saved", "profile": p}), 201


@app.route("/api/profiles/<pid>", methods=["DELETE"])
def delete_profile(pid):
    fp = os.path.join(app.config["PROFILES_FOLDER"], f"{pid}.json")
    if os.path.exists(fp) and ".." not in pid:
        os.remove(fp)
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/stats")
def get_stats():
    h = load_history()
    return jsonify(
        {
            "total": len(h),
            "successful": len([x for x in h if x.get("status") == "success"]),
            "errors": len([x for x in h if x.get("status") == "error"]),
            "batches": len([x for x in h if x.get("status") == "batch"]),
        }
    )


SETTINGS_FILE = os.path.join(app.config["RESULTS_FOLDER"], "settings.json")


def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Settings load err: {e}")
    return {}


def save_settings_file(s):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Settings save err: {e}")
        return False


@app.route("/api/settings", methods=["GET"])
def get_settings():
    ss = load_settings()
    return jsonify(
        {
            **load_creds(),
            "sqlmap_path": ss.get("sqlmap_path", SQLMAP_PATH),
            "max_file_size_mb": app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024),
            "max_batch_size": 50,
            "version": "2.1.0",
        }
    )


@app.route("/api/settings", methods=["POST"])
def save_settings():
    d = request.json or {}
    save_creds(
        {
            "proxy_host": d.get("proxy_host", ""),
            "proxy_port": d.get("proxy_port", ""),
            "proxy_user": d.get("proxy_user", ""),
            "proxy_pass": d.get("proxy_pass", ""),
            "auth_header": d.get("auth_header", ""),
        }
    )
    ss = load_settings()
    if d.get("sqlmap_path"):
        ss["sqlmap_path"] = d["sqlmap_path"]
    save_settings_file(ss)
    return jsonify({"message": "Saved"})


@app.route("/api/creds", methods=["GET"])
def get_creds():
    return jsonify(load_creds())


@app.route("/api/health")
def health_check():
    ss = load_settings()
    path = ss.get("sqlmap_path", SQLMAP_PATH)
    ok = os.path.exists(path)
    return jsonify(
        {
            "status": "healthy" if ok else "degraded",
            "sqlmap_found": ok,
            "sqlmap_path": path,
            "uptime": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  SQLReaper v2.1 - Advanced Penetration Testing")
    print("=" * 60)
    print(f"  http://0.0.0.0:5000  |  SQLMap: {SQLMAP_PATH}")
    print("  Features: WebSocket, Queue, Vulnerability Tracking, Templates")
    print("=" * 60 + "\n")
    tray.start()
    tray.register("show", lambda: None)
    try:
        socketio.run(
            app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True
        )
    finally:
        tray.stop()
