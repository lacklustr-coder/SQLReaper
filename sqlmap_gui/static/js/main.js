(function () {
  "use strict";
  var API = "",
    output,
    currentScanId = null,
    scanning = false,
    pendingSaveHandlers = [];

  var $ = function (s, p) {
    return (p || document).querySelector(s);
  };
  var $$ = function (s, p) {
    return Array.prototype.slice.call((p || document).querySelectorAll(s));
  };
  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }

  /** Split a line like POSIX shlex (whitespace outside quotes); keeps values with spaces intact. */
  function splitShellLine(str) {
    if (!str || !String(str).trim()) return [];
    var out = [],
      cur = "",
      i = 0,
      q = null,
      s = String(str);
    while (i < s.length) {
      var c = s[i++];
      if (q) {
        if (c === q) q = null;
        else if (c === "\\" && q === '"' && i < s.length) cur += s[i++];
        else cur += c;
      } else if (c === '"' || c === "'") {
        q = c;
      } else if (/\s/.test(c)) {
        if (cur) {
          out.push(cur);
          cur = "";
        }
      } else cur += c;
    }
    if (cur) out.push(cur);
    return out.filter(Boolean);
  }

  /** Serialize argv for textarea / profile display (quote tokens that contain spaces). */
  function argvToShellLine(argv) {
    if (argv == null) return "";
    if (typeof argv === "string") return argv;
    if (!Array.isArray(argv)) return String(argv);
    return argv
      .map(function (a) {
        var t = String(a);
        if (/[\s"'\\]/.test(t))
          return '"' + t.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
        return t;
      })
      .join(" ");
  }

  function toast(m, t) {
    var c = $("#toast-container");
    if (!c) return;
    var d = document.createElement("div");
    var color =
      t === "success"
        ? "#00ff44"
        : t === "error"
          ? "#ff3333"
          : t === "warning"
            ? "#ffaa00"
            : "#00aaff";
    d.style.cssText =
      "padding:10px 16px;border-radius:6px;color:#fff;font-size:.85em;max-width:300px;border-left:3px solid " +
      color +
      ";background:rgba(0,0,0,.85);animation:toastIn .3s,toastOut .3s 2.7s forwards;";
    d.textContent = m;
    c.appendChild(d);
    setTimeout(function () {
      if (d.parentNode) d.parentNode.removeChild(d);
    }, 3000);
  }

  function appendMsg(t, c) {
    if (!output) return;
    var line = c ? '<span class="' + c + '">' + esc(t) + "</span>" : esc(t);
    output.innerHTML += (output.innerHTML ? "\n" : "") + line;
    output.scrollTop = output.scrollHeight;
  }

  function clearOutput() {
    if (output)
      output.innerHTML =
        '<span style="color:var(--text-muted);">[-] Cleared.</span>';
  }

  function setProgress(p, t) {
    var f = $("#progress-fill");
    if (f) f.style.width = p + "%";
    var pt = $("#progress-text");
    if (pt && t) pt.textContent = t;
  }

  function showSettingsModal() {
    var m = $("#settings-modal");
    if (m) m.style.display = "flex";
    api("/api/settings")
      .then(function (d) {
        var c = $("#settings-content");
        if (!c) return;
        c.innerHTML =
          '<div class="form-group"><label>SQLMap Path *</label><input type="text" id="s-sqlmap-path" value="' +
          esc(d.sqlmap_path || "") +
          '" placeholder="/path/to/sqlmap/sqlmap.py"><small>Full path to sqlmap.py or sqlmap directory</small></div>' +
          '<hr style="border:none;border-top:1px solid var(--border-subtle);margin:12px 0">' +
          '<div class="form-group"><label>Proxy Host</label><input type="text" id="s-proxy" value="' +
          esc(d.proxy_host || "") +
          '"></div>' +
          '<div class="form-row"><div class="form-group"><label>Proxy Port</label><input type="number" id="s-port" value="' +
          (d.proxy_port || "") +
          '"></div>' +
          '<div class="form-group"><label>Auth Header</label><input type="text" id="s-auth" value="' +
          esc(d.auth_header || "") +
          '"></div></div>' +
          '<div class="button-group"><button class="btn-primary" id="s-save">Save</button></div>';
        var sb = $("#s-save");
        if (sb)
          sb.onclick = function () {
            api("/api/settings", {
              method: "POST",
              body: JSON.stringify({
                sqlmap_path: $("#s-sqlmap-path").value.trim(),
                proxy_host: $("#s-proxy").value.trim(),
                proxy_port: $("#s-port").value.trim(),
                auth_header: $("#s-auth").value.trim(),
              }),
            })
              .then(function () {
                toast("Saved", "success");
                closeModal("settings-modal");
              })
              .catch(function (e) {
                toast("Failed: " + e.message, "error");
              });
          };
      })
      .catch(function () {
        var c = $("#settings-content");
        if (c) c.innerHTML = '<p class="term-error">Failed to load</p>';
      });
  }

  function closeModal(id) {
    var e = $("#" + id);
    if (e) e.style.display = "none";
  }

  function api(url, o) {
    o = o || {};
    o.headers = o.headers || {};
    o.headers["Content-Type"] = "application/json";
    o.headers["Accept"] = "application/json";
    return fetch(API + url, o).then(function (r) {
      return r.json().then(function (d) {
        if (!r.ok) throw new Error(d.error || "Error");
        return d;
      });
    });
  }

  // ========== Init ==========
  document.addEventListener("DOMContentLoaded", function () {
    output = $("#output");
    if (!output) {
      console.error("#output not found");
      return;
    }

    // ---- Helpers bind after DOM ready ----
    function bind(id, ev, fn) {
      var el = $("#" + id);
      if (el) el.addEventListener(ev, fn);
    }
    function bindAll(sel, ev, fn) {
      $$(sel).forEach(function (el) {
        el.addEventListener(ev, fn);
      });
    }

    // ---- Theme ----
    var theme = localStorage.getItem("sql-theme") || "dark";
    document.documentElement.dataset.theme = theme;
    bind("theme-toggle", "click", function () {
      var n =
        document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = n;
      localStorage.setItem("sql-theme", n);
    });

    // ---- Tabs ----
    $$(".tab-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        $$(".tab-btn").forEach(function (x) {
          x.classList.remove("active");
        });
        $$(".tab-content").forEach(function (x) {
          x.classList.remove("active");
        });
        b.classList.add("active");
        var tg = $("#" + b.dataset.tab);
        if (tg) tg.classList.add("active");
      });
    });

    // ---- Keyboard ----
    document.addEventListener("keydown", function (e) {
      if (e.ctrlKey && e.key === "Enter" && !scanning) {
        e.preventDefault();
        var sb = $("#scan-btn");
        if (sb) sb.click();
      }
      if (e.key === "Escape") {
        e.preventDefault();
        if (scanning) {
          var st = $("#stop-btn");
          if (st) st.click();
        }
      }
      if (e.ctrlKey && e.key === "k") {
        e.preventDefault();
        var t = $("#target");
        if (t) t.focus();
      }
      if (e.ctrlKey && e.key === "l") {
        e.preventDefault();
        clearOutput();
      }
    });

    // ---- Modal open/close ----
    bind("shortcuts-btn", "click", function () {
      var m = $("#shortcuts-modal");
      if (m) m.style.display = "flex";
    });
    bind("shortcuts-close", "click", function () {
      closeModal("shortcuts-modal");
    });
    bind("export-pdf-btn", "click", function () {
      var m = $("#export-modal");
      if (m) m.style.display = "flex";
    });
    bind("export-close", "click", function () {
      closeModal("export-modal");
    });
    bind("save-profile-btn", "click", function () {
      var m = $("#save-profile-modal");
      if (m) m.style.display = "flex";
    });
    bind("save-profile-close", "click", function () {
      closeModal("save-profile-modal");
    });
    bind("settings-btn", "click", function () {
      showSettingsModal();
    });
    bind("settings-close", "click", function () {
      closeModal("settings-modal");
    });
    $$(".modal").forEach(function (m) {
      m.addEventListener("click", function (e) {
        if (e.target === m) m.style.display = "none";
      });
    });

    // ---- Health ----
    function health() {
      api("/api/health")
        .then(function (d) {
          var dot = $("#health-dot");
          if (dot)
            dot.className =
              "status-dot " + (d.status === "healthy" ? "healthy" : "error");
          var ht = $("#health-text");
          if (ht) ht.textContent = d.sqlmap_found ? "sqlmap OK" : "Not found";
        })
        .catch(function () {
          var dot = $("#health-dot");
          if (dot) dot.className = "status-dot error";
          var ht = $("#health-text");
          if (ht) ht.textContent = "Offline";
        });
    }
    health();
    setInterval(health, 30000);

    // ---- Stats ----
    function stats() {
      api("/api/stats")
        .then(function (d) {
          var t = $("#total-scans");
          if (t) t.textContent = "Total: " + (d.total || 0);
          var o = $("#successful-scans");
          if (o) o.textContent = "OK: " + (d.successful || 0);
          var f = $("#failed-scans");
          if (f) f.textContent = "Err: " + (d.errors || 0);
        })
        .catch(function () {});
    }
    stats();

    // ---- History ----
    function loadHistory() {
      api("/api/history")
        .then(function (d) {
          var list = $("#scan-history");
          if (!list) return;
          if (!d.history || !d.history.length) {
            list.innerHTML = '<div class="history-empty">No scans yet</div>';
            return;
          }
          list.innerHTML = d.history
            .map(function (h) {
              return (
                '<div class="history-item" data-id="' +
                h.id +
                '">' +
                '<div class="target">' +
                esc(h.target) +
                "</div>" +
                '<div class="time">' +
                new Date(h.timestamp).toLocaleString() +
                "</div>" +
                '<span class="status ' +
                h.status +
                '">' +
                h.status +
                "</span>" +
                '<div class="history-actions"><button class="history-delete-btn" data-del="' +
                h.id +
                '">&times;</button></div></div>'
              );
            })
            .join("");
          $$(".history-item", list).forEach(function (it) {
            it.addEventListener("click", function (e) {
              if (e.target.tagName === "BUTTON") return;
              var id = it.getAttribute("data-id");
              if (id) loadResult(id);
            });
          });
          $$(".history-delete-btn", list).forEach(function (b) {
            b.addEventListener("click", function (e) {
              e.stopPropagation();
              api("/api/history/" + b.getAttribute("data-del"), {
                method: "DELETE",
              }).then(function () {
                loadHistory();
                stats();
                toast("Deleted", "success");
              });
            });
          });
        })
        .catch(function () {});
    }
    loadHistory();

    function loadResult(id) {
      api("/api/results/" + id)
        .then(function (d) {
          appendMsg("\n[i] History: " + id, "term-info");
          appendMsg(d.output || "No output");
          toast("Loaded", "success");
        })
        .catch(function (e) {
          toast("Failed: " + e.message, "error");
        });
    }

    bind("clear-history-btn", "click", function () {
      if (!confirm("Clear all history?")) return;
      api("/api/history/clear", { method: "POST" }).then(function () {
        loadHistory();
        stats();
        toast("Cleared", "success");
      });
    });

    // ---- Build scan options ----
    function buildOpts() {
      var o = [],
        add = function (id, flag) {
          var el = $("#" + id);
          if (el && el.checked) o.push(flag || "--" + id.replace(/opt-/, ""));
        };
      var v = function (id) {
        var el = $("#" + id);
        return el ? el.value : "";
      };
      if ($("#random-agent") && $("#random-agent").checked)
        o.push("--random-agent");
      if ($("#tor") && $("#tor").checked) o.push("--tor");
      if ($("#flush-session") && $("#flush-session").checked)
        o.push("--flush-session");
      if ($("#smart-check") && $("#smart-check").checked) o.push("--smart");
      if ($("#force-ssl") && $("#force-ssl").checked) o.push("--force-ssl");
      if ($("#skip-waf") && $("#skip-waf").checked) o.push("--skip-waf");
      if ($("#no-cast") && $("#no-cast").checked) o.push("--no-cast");
      if ($("#risk") && $("#risk").checked) o.push("--risk=3");
      if ($("#level") && $("#level").checked) o.push("--level=5");
      if ($("#tamper") && $("#tamper").checked)
        o.push("--tamper=space2comment,between");
      if ($("#dbs") && $("#dbs").checked) o.push("--dbs");
      if ($("#tables") && $("#tables").checked) o.push("--tables");
      if ($("#columns") && $("#columns").checked) o.push("--columns");
      if ($("#dump") && $("#dump").checked) o.push("--dump");
      if ($("#users") && $("#users").checked) o.push("--users");
      if ($("#passwords") && $("#passwords").checked) o.push("--passwords");
      if ($("#os-shell") && $("#os-shell").checked) o.push("--os-shell");
      if ($("#sql-shell") && $("#sql-shell").checked) o.push("--sql-shell");
      if ($("#file-read") && $("#file-read").checked) o.push("--file-read");
      var cu = v("custom-options").trim();
      if (cu) o = o.concat(splitShellLine(cu));
      var pu = v("proxy-url").trim();
      if (pu) {
        o.push("--proxy");
        o.push(pu);
      }
      var ck = v("cookie").trim();
      if (ck) {
        o.push("--cookie");
        o.push(ck);
      }
      var ua = v("user-agent").trim();
      if (ua) {
        o.push("--user-agent");
        o.push(ua);
      }
      return o;
    }

    // ---- Scan Form ----
    var scanForm = $("#scan-form");
    if (scanForm) {
      scanForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var target = $("#target");
        if (!target) return;
        var tv = target.value.trim();
        if (!tv) {
          toast("Enter target URL", "warning");
          return;
        }
        scanning = true;
        var sb = $("#scan-btn");
        if (sb) sb.disabled = true;
        var stb = $("#stop-btn");
        if (stb) stb.disabled = false;
        var si = $("#status-indicator");
        if (si) si.className = "status-indicator status-running";
        clearOutput();
        appendMsg("[+] Scanning: " + tv, "term-info");
        setProgress(10, "Starting...");
        api("/api/scan", {
          method: "POST",
          body: JSON.stringify({ target: tv, options: buildOpts() }),
        })
          .then(function (d) {
            appendMsg(d.output || "Scan complete", "term-success");
            setProgress(100, "Complete");
            currentScanId = d.scan_id;
            toast("Scan done", "success");
            if (si) si.className = "status-indicator status-success";
            loadHistory();
            stats();
          })
          .catch(function (err) {
            appendMsg("Error: " + err.message, "term-error");
            setProgress(0, "Error");
            toast(err.message, "error");
            if (si) si.className = "status-indicator status-error";
          })
          .finally(function () {
            scanning = false;
            var sb2 = $("#scan-btn");
            if (sb2) sb2.disabled = false;
            var stb2 = $("#stop-btn");
            if (stb2) stb2.disabled = true;
          });
      });
    }

    bind("stop-btn", "click", function () {
      scanning = false;
      if (currentScanId)
        api("/api/scan/stop/" + currentScanId, { method: "POST" });
      var sb = $("#scan-btn");
      if (sb) sb.disabled = false;
      var stb = $("#stop-btn");
      if (stb) stb.disabled = true;
      var si = $("#status-indicator");
      if (si) si.className = "status-indicator status-waiting";
      appendMsg("[*] Stopped", "term-warning");
      setProgress(0, "Stopped");
    });

    bind("clear-btn", "click", function () {
      clearOutput();
      setProgress(0, "Cleared");
      var t = $("#target");
      if (t) t.value = "";
    });

    // ---- Batch Scan ----
    bind("batch-scan-btn", "click", function (e) {
      e.preventDefault();
      var ba = $("#batch-urls");
      if (!ba) return;
      var txt = ba.value.trim();
      if (!txt) {
        toast("Enter URLs", "warning");
        return;
      }
      var urls = txt
        .split("\n")
        .filter(function (u) {
          var s = u.trim();
          return s && s[0] !== "#";
        })
        .map(function (u) {
          return u.trim();
        });
      if (!urls.length) {
        toast("No valid URLs", "warning");
        return;
      }
      var btn = $("#batch-scan-btn");
      if (btn) btn.disabled = true;
      api("/api/scan/batch", {
        method: "POST",
        body: JSON.stringify({
          urls: urls,
          options: $("#batch-options") ? $("#batch-options").value : "",
        }),
      })
        .then(function (d) {
          var br = $("#batch-results");
          if (br) br.style.display = "block";
          var bc = $("#batch-results-count");
          if (bc) bc.textContent = d.total + " results";
          var bl = $("#batch-results-list");
          if (bl)
            bl.innerHTML = d.results
              .map(function (r) {
                return (
                  '<div class="batch-result-item ' +
                  r.status +
                  '"><div class="batch-result-url">' +
                  esc(r.url) +
                  "</div>" +
                  '<span class="batch-result-status">' +
                  r.status +
                  "</span>" +
                  '<pre style="margin-top:6px;font-size:.72em;max-height:100px;overflow:auto;white-space:pre-wrap">' +
                  esc(r.output.slice(0, 400)) +
                  "</pre></div>"
                );
              })
              .join("");
          toast("Batch complete", "success");
          loadHistory();
          stats();
        })
        .catch(function (err) {
          toast(err.message, "error");
        })
        .finally(function () {
          var btn2 = $("#batch-scan-btn");
          if (btn2) btn2.disabled = false;
        });
    });
    bind("batch-clear", "click", function () {
      var ba = $("#batch-urls");
      if (ba) ba.value = "";
      var br = $("#batch-results");
      if (br) br.style.display = "none";
    });

    // ---- Dork Scan ----
    var dorkForm = $("#dork-form");
    if (dorkForm) {
      dorkForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var dq = $("#dork-query");
        if (!dq) return;
        var dork = dq.value.trim();
        if (!dork) {
          toast("Enter a dork", "warning");
          return;
        }
        var btn = $("#dork-scan-btn");
        if (btn) btn.disabled = true;
        var di = $("#dork-status-indicator");
        if (di) di.className = "status-indicator status-running";
        clearOutput();
        appendMsg("[+] Dorking: " + dork, "term-info");
        api("/api/google-dork", {
          method: "POST",
          body: JSON.stringify({
            dork: dork,
            search_engine: $("#search-engine")
              ? $("#search-engine").value
              : "Google",
          }),
        })
          .then(function (d) {
            appendMsg(d.output || "No results", "term-success");
            if (di) di.className = "status-indicator status-success";
            toast("Dork done", "success");
            loadHistory();
            stats();
          })
          .catch(function (err) {
            appendMsg("Error: " + err.message, "term-error");
            if (di) di.className = "status-indicator status-error";
            toast(err.message, "error");
          })
          .finally(function () {
            var btn2 = $("#dork-scan-btn");
            if (btn2) btn2.disabled = false;
          });
      });
    }
    bind("dork-clear-btn", "click", function () {
      var dq = $("#dork-query");
      if (dq) dq.value = "";
      clearOutput();
    });
    $$(".preset-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        var dork = b.getAttribute("data-dork");
        var dq = $("#dork-query");
        if (dq) dq.value = dork;
        navigator.clipboard
          .writeText(dork)
          .then(function () {
            toast("Copied & applied", "success");
          })
          .catch(function () {
            toast("Applied", "info");
          });
      });
    });

    // ---- Multi-Dork ----
    bind("multi-dork-btn", "click", function (e) {
      e.preventDefault();
      var md = $("#multi-dorks");
      if (!md) return;
      var txt = md.value.trim();
      if (!txt) {
        toast("Enter dorks", "warning");
        return;
      }
      api("/api/google-dork-multi", {
        method: "POST",
        body: JSON.stringify({
          dorks: txt,
          search_engine: $("#multi-search-engine")
            ? $("#multi-search-engine").value
            : "Google",
        }),
      })
        .then(function (d) {
          var mr = $("#multi-dork-results");
          if (mr) mr.style.display = "block";
          var mc = $("#multi-dork-count");
          if (mc) mc.textContent = d.total_dorks + " dorks";
          var mdc = $("#multi-dork-commands");
          if (mdc)
            mdc.innerHTML = d.scans
              .map(function (s) {
                return (
                  '<div class="multi-command-item"><div class="dork-label">' +
                  esc(s.dork) +
                  '</div><div class="command-text">' +
                  esc(s.command) +
                  '</div><button class="copy-btn" data-clip="' +
                  esc(s.command) +
                  '">Copy</button></div>'
                );
              })
              .join("");
          $$(".copy-btn", mdc || $("#multi-dork-commands")).forEach(
            function (cb) {
              cb.addEventListener("click", function () {
                navigator.clipboard
                  .writeText(cb.getAttribute("data-clip"))
                  .then(function () {
                    toast("Copied", "success");
                  });
              });
            },
          );
          toast("Generated", "success");
        })
        .catch(function (err) {
          toast(err.message, "error");
        });
    });
    bind("multi-clear-btn", "click", function () {
      var md = $("#multi-dorks");
      if (md) md.value = "";
      var mr = $("#multi-dork-results");
      if (mr) mr.style.display = "none";
    });

    // ---- Dork Library ----
    bind("dork-search", "input", function () {
      var q = $("#dork-search").value.toLowerCase();
      filterDorks();
    });
    bind("dork-filter-diff", "change", function () {
      filterDorks();
    });
    function filterDorks() {
      var q = $("#dork-search") ? $("#dork-search").value.toLowerCase() : "";
      var diff = $("#dork-filter-diff") ? $("#dork-filter-diff").value : "";
      $$(".dork-item").forEach(function (d) {
        var matchText = !q || d.textContent.toLowerCase().indexOf(q) !== -1;
        var cat = d.closest(".dork-category");
        var matchDiff =
          !diff ||
          (cat &&
            cat.querySelector(".dork-diff") &&
            cat.querySelector(".dork-diff").classList.contains(diff));
        d.style.display = matchText && matchDiff ? "" : "none";
      });
      $$(".dork-category").forEach(function (cat) {
        var items = cat.querySelectorAll(".dork-item");
        var visCount = 0;
        items.forEach(function (i) {
          if (i.style.display !== "none") visCount++;
        });
        cat.style.display = visCount ? "" : "none";
      });
    }
    $$(".dork-item").forEach(function (d) {
      // Click on dork item (not the clipboard button) - populate field and switch tab
      d.addEventListener("click", function (e) {
        // Don't trigger if clicking the clipboard button
        if (e.target.classList.contains("dork-clipboard-btn")) {
          return;
        }
        var dorkValue = d.getAttribute("data-dork");
        var dorkQueryField = $("#dork-query");
        if (dorkQueryField) {
          dorkQueryField.value = dorkValue;
          // Switch to Google Dorking tab
          var dorkTab = $('[data-tab="google-dork"]');
          if (dorkTab) {
            dorkTab.click();
          }
          toast("Dork applied to Google Dorking tab", "success");
        }
      });

      // Click on clipboard button - copy only
      var clipboardBtn = d.querySelector(".dork-clipboard-btn");
      if (clipboardBtn) {
        clipboardBtn.addEventListener("click", function (e) {
          e.stopPropagation(); // Prevent triggering parent click
          var dorkValue = d.getAttribute("data-dork");
          navigator.clipboard
            .writeText(dorkValue)
            .then(function () {
              toast("Copied to clipboard", "success");
            })
            .catch(function () {
              toast("Failed to copy", "error");
            });
        });
      }
    });

    // ---- Profiles ----
    var profForm = $("#profile-form");
    if (profForm) {
      profForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var pn = $("#profile-name");
        if (!pn || !pn.value.trim()) {
          toast("Enter name", "warning");
          return;
        }
        api("/api/profiles", {
          method: "POST",
          body: JSON.stringify({
            name: pn.value.trim(),
            options: $("#profile-options") ? $("#profile-options").value : "",
          }),
        })
          .then(function () {
            toast("Saved", "success");
            pn.value = "";
            var po = $("#profile-options");
            if (po) po.value = "";
            loadProfiles();
          })
          .catch(function (err) {
            toast(err.message, "error");
          });
      });
    }

    function loadProfiles() {
      api("/api/profiles").then(function (d) {
        var pc = $("#profiles-container");
        if (!pc) return;
        if (!d.profiles.length) {
          pc.innerHTML = '<div class="history-empty">No profiles</div>';
          return;
        }
        pc.innerHTML = d.profiles
          .map(function (p) {
            return (
              '<div class="profile-item"><div class="profile-info"><div class="profile-name">' +
              esc(p.name) +
              "</div></div>" +
              '<div class="profile-actions"><button class="btn-small" data-load="' +
              p.id +
              '">Load</button>' +
              '<button class="btn-small" style="color:var(--error)" data-del="' +
              p.id +
              '">Del</button></div></div>'
            );
          })
          .join("");
        $$("#profiles-container [data-load]").forEach(function (b) {
          b.addEventListener("click", function () {
            api("/api/profiles").then(function (d2) {
              var p = d2.profiles.find(function (x) {
                return x.id === b.getAttribute("data-load");
              });
              if (p) {
                var co = $("#custom-options");
                if (co) co.value = argvToShellLine(p.options);
                toast("Loaded", "success");
              }
            });
          });
        });
        $$("#profiles-container [data-del]").forEach(function (b) {
          b.addEventListener("click", function () {
            api("/api/profiles/" + b.getAttribute("data-del"), {
              method: "DELETE",
            }).then(function () {
              toast("Deleted", "success");
              loadProfiles();
            });
          });
        });
      });
    }
    loadProfiles();

    // Save profile modal
    bind("modal-save-profile", "click", function () {
      var mn = $("#modal-profile-name");
      if (!mn || !mn.value.trim()) {
        toast("Enter name", "warning");
        return;
      }
      api("/api/profiles", {
        method: "POST",
        body: JSON.stringify({ name: mn.value.trim(), options: buildOpts() }),
      })
        .then(function () {
          toast("Saved", "success");
          closeModal("save-profile-modal");
          mn.value = "";
          loadProfiles();
        })
        .catch(function (err) {
          toast(err.message, "error");
        });
    });

    // ---- Export ----
    $$(".export-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        var fmt = b.getAttribute("data-format");
        var txt = output ? output.textContent : "";
        if (!txt) {
          toast("No output", "warning");
          return;
        }
        api("/api/export", {
          method: "POST",
          body: JSON.stringify({
            output: txt,
            format: fmt,
            target: $("#target") ? $("#target").value || "unknown" : "unknown",
          }),
        })
          .then(function (d) {
            window.open(API + d.download_url, "_blank");
            toast("Exported " + fmt, "success");
            closeModal("export-modal");
          })
          .catch(function (e) {
            toast("Export failed", "error");
          });
      });
    });

    // ---- Copy ----
    bind("copy-output-btn", "click", function () {
      var txt = output ? output.textContent : "";
      if (!txt) {
        toast("Nothing", "warning");
        return;
      }
      navigator.clipboard
        .writeText(txt)
        .then(function () {
          toast("Copied", "success");
        })
        .catch(function () {
          toast("Copy failed", "error");
        });
    });

    // ---- Upload + Drag & Drop ----
    var ua = $("#upload-area"),
      fi = $("#file-input");
    if (ua && fi) {
      ua.addEventListener("click", function () {
        fi.click();
      });
      ua.addEventListener("dragover", function (e) {
        e.preventDefault();
        ua.classList.add("drag-over");
      });
      ua.addEventListener("dragleave", function () {
        ua.classList.remove("drag-over");
      });
      ua.addEventListener("drop", function (e) {
        e.preventDefault();
        ua.classList.remove("drag-over");
        if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
      });
      fi.addEventListener("change", function () {
        if (fi.files.length) uploadFile(fi.files[0]);
      });
    }

    function uploadFile(f) {
      appendMsg("\n[i] Uploading: " + f.name, "term-info");
      var fd = new FormData();
      fd.append("file", f);
      fetch(API + "/api/upload", { method: "POST", body: fd })
        .then(function (r) {
          return r.json();
        })
        .then(function (d) {
          appendMsg("[+] Upload: " + d.filename, "term-success");
          if (d.parsed && d.parsed.url) {
            $("#target").value = d.parsed.url;
            appendMsg("[+] URL: " + d.parsed.url, "term-info");
          }
          toast("Uploaded", "success");
        })
        .catch(function (e) {
          appendMsg("[-] " + e.message, "term-error");
        });
    }

    appendMsg("[+] GUI Ready.", "term-success");
  });
})();
