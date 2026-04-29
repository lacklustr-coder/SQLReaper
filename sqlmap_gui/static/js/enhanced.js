/**
 * SQLReaper v2.1 - Enhanced Features
 * WebSocket, Templates, Vulnerabilities, Fuzzer, Queue, Statistics
 */

// WebSocket Connection
let socket = null;
let currentScanId = null;

function initWebSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('[WebSocket] Connected');
        showToast('WebSocket connected', 'success');
    });

    socket.on('disconnect', () => {
        console.log('[WebSocket] Disconnected');
        showToast('WebSocket disconnected', 'warning');
    });

    socket.on('scan_output', (data) => {
        if (data.scan_id === currentScanId) {
            appendOutput(data.output);
        }
    });

    socket.on('scan_status', (data) => {
        if (data.scan_id === currentScanId) {
            updateScanProgress(data.progress || 0, data.details || data.status);
        }
    });

    socket.on('scan_complete', (data) => {
        if (data.scan_id === currentScanId) {
            updateScanProgress(100, `Complete - ${data.vulnerabilities} vulnerabilities found`);
            showToast(`Scan complete: ${data.vulnerabilities} vulnerabilities`, data.success ? 'success' : 'error');
            loadHistory();
            loadVulnerabilities();
        }
    });

    socket.on('vulnerability_found', (data) => {
        if (data.scan_id === currentScanId) {
            showToast(`Vulnerability found: ${data.vulnerability.vuln_type}`, 'warning');
            notifyVulnerability(data.vulnerability);
        }
    });

    socket.on('scan_error', (data) => {
        if (data.scan_id === currentScanId) {
            showToast(`Error: ${data.error}`, 'error');
        }
    });
}

function joinScanRoom(scanId) {
    currentScanId = scanId;
    if (socket && socket.connected) {
        socket.emit('join_scan', { scan_id: scanId });
    }
}

function leaveScanRoom(scanId) {
    if (socket && socket.connected) {
        socket.emit('leave_scan', { scan_id: scanId });
    }
    currentScanId = null;
}

// Templates
async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();

        const container = document.getElementById('templates-list');
        if (!data.templates || data.templates.length === 0) {
            container.innerHTML = '<p class="text-muted">No templates available</p>';
            return;
        }

        container.innerHTML = data.templates.map(template => `
            <div class="template-card ${template.is_default ? 'default' : ''}">
                <div class="template-header">
                    <h4>${template.name}</h4>
                    ${template.is_default ? '<span class="badge badge-primary">Default</span>' : ''}
                </div>
                <p class="template-description">${template.description || ''}</p>
                <div class="template-footer">
                    <button class="btn-small" onclick="useTemplate('${template.id}')">Use Template</button>
                    <button class="btn-icon" onclick="viewTemplateOptions('${template.id}')" title="View Options">&#128196;</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load templates:', error);
        showToast('Failed to load templates', 'error');
    }
}

async function useTemplate(templateId) {
    try {
        const response = await fetch(`/api/templates/${templateId}/options`);
        const data = await response.json();

        document.getElementById('custom-options').value = data.options_string;
        document.querySelector('[data-tab="direct-scan"]').click();
        showToast(`Template applied: ${data.options_string.substring(0, 50)}...`, 'success');
    } catch (error) {
        console.error('Failed to use template:', error);
        showToast('Failed to apply template', 'error');
    }
}

async function viewTemplateOptions(templateId) {
    try {
        const response = await fetch(`/api/templates/${templateId}`);
        const data = await response.json();

        alert(`Template: ${data.name}\\n\\nOptions: ${JSON.stringify(data.options, null, 2)}`);
    } catch (error) {
        console.error('Failed to view template:', error);
    }
}

// Vulnerabilities
async function loadVulnerabilities() {
    const severity = document.getElementById('vuln-severity-filter').value;
    const status = document.getElementById('vuln-status-filter').value;

    try {
        const params = new URLSearchParams();
        if (severity) params.append('severity', severity);
        if (status) params.append('status', status);

        const response = await fetch(`/api/vulnerabilities?${params}`);
        const data = await response.json();

        const container = document.getElementById('vulnerabilities-list');
        if (!data.vulnerabilities || data.vulnerabilities.length === 0) {
            container.innerHTML = '<p class="text-muted">No vulnerabilities found</p>';
            return;
        }

        container.innerHTML = data.vulnerabilities.map(vuln => `
            <div class="vuln-card severity-${vuln.severity}">
                <div class="vuln-header">
                    <h4>${vuln.vuln_type.replace(/_/g, ' ').toUpperCase()}</h4>
                    <span class="severity-badge ${vuln.severity}">${vuln.severity}</span>
                </div>
                <div class="vuln-details">
                    <p><strong>Parameter:</strong> ${vuln.parameter || 'N/A'}</p>
                    <p><strong>Database:</strong> ${vuln.database_type || 'Unknown'}</p>
                    <p><strong>OWASP:</strong> ${vuln.owasp_category || 'N/A'}</p>
                    <p><strong>Description:</strong> ${vuln.description || 'N/A'}</p>
                    ${vuln.payload ? `<p><strong>Payload:</strong> <code>${vuln.payload.substring(0, 100)}</code></p>` : ''}
                </div>
                <div class="vuln-actions">
                    <select onchange="updateVulnStatus(${vuln.id}, this.value)">
                        <option value="new" ${vuln.status === 'new' ? 'selected' : ''}>New</option>
                        <option value="confirmed" ${vuln.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                        <option value="fixed" ${vuln.status === 'fixed' ? 'selected' : ''}>Fixed</option>
                        <option value="ignored" ${vuln.status === 'ignored' ? 'selected' : ''}>Ignored</option>
                    </select>
                    <button class="btn-small" onclick="markFalsePositive(${vuln.id}, ${!vuln.false_positive})">
                        ${vuln.false_positive ? 'Unmark FP' : 'Mark as False Positive'}
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load vulnerabilities:', error);
        showToast('Failed to load vulnerabilities', 'error');
    }
}

async function updateVulnStatus(vulnId, status) {
    try {
        await fetch(`/api/vulnerabilities/${vulnId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        showToast('Vulnerability status updated', 'success');
        loadVulnerabilities();
    } catch (error) {
        console.error('Failed to update status:', error);
        showToast('Failed to update status', 'error');
    }
}

async function markFalsePositive(vulnId, isFP) {
    try {
        await fetch(`/api/vulnerabilities/${vulnId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ false_positive: isFP })
        });
        showToast(isFP ? 'Marked as false positive' : 'Unmarked false positive', 'success');
        loadVulnerabilities();
    } catch (error) {
        console.error('Failed to mark false positive:', error);
        showToast('Failed to update', 'error');
    }
}

// Parameter Fuzzer
document.getElementById('fuzzer-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = document.getElementById('fuzz-url').value;
    const parameter = document.getElementById('fuzz-parameter').value;
    const types = Array.from(document.querySelectorAll('#fuzzer-form input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    if (types.length === 0) {
        showToast('Select at least one fuzzing type', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/fuzz/parameter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, parameter, types })
        });

        const data = await response.json();

        const container = document.getElementById('fuzz-results');
        container.innerHTML = `
            <div class="fuzz-results-header">
                <h4>Generated ${data.total} Fuzzed URLs</h4>
                <button class="btn-small" onclick="exportFuzzResults()">Export</button>
            </div>
            <div class="fuzz-results-list">
                ${data.fuzzed_urls.slice(0, 100).map((item, i) => `
                    <div class="fuzz-result-item">
                        <span class="fuzz-index">${i + 1}</span>
                        <span class="fuzz-category">${item.category}</span>
                        <code class="fuzz-url">${item.url}</code>
                        <button class="btn-icon" onclick="copyToClipboard('${item.url.replace(/'/g, "\\'")}')">&#128203;</button>
                    </div>
                `).join('')}
            </div>
            ${data.total > 100 ? `<p class="text-muted">Showing first 100 of ${data.total} results</p>` : ''}
        `;

        showToast(`Generated ${data.total} fuzzed URLs`, 'success');
    } catch (error) {
        console.error('Failed to generate fuzzing payloads:', error);
        showToast('Failed to generate payloads', 'error');
    }
});

// Scan Queue
async function loadQueue() {
    try {
        const response = await fetch('/api/queue');
        const data = await response.json();

        const container = document.getElementById('queue-list');
        const statsContainer = document.getElementById('queue-stats');

        const pending = data.queue.filter(q => q.status === 'pending').length;
        const running = data.queue.filter(q => q.status === 'running').length;
        const completed = data.queue.filter(q => q.status === 'completed').length;

        statsContainer.innerHTML = `
            <div class="queue-stat-grid">
                <div class="queue-stat">
                    <span class="stat-value">${pending}</span>
                    <span class="stat-label">Pending</span>
                </div>
                <div class="queue-stat">
                    <span class="stat-value">${running}</span>
                    <span class="stat-label">Running</span>
                </div>
                <div class="queue-stat">
                    <span class="stat-value">${completed}</span>
                    <span class="stat-label">Completed</span>
                </div>
            </div>
        `;

        if (!data.queue || data.queue.length === 0) {
            container.innerHTML = '<p class="text-muted">Queue is empty</p>';
            return;
        }

        container.innerHTML = data.queue.map(item => `
            <div class="queue-item status-${item.status}">
                <div class="queue-info">
                    <strong>Scan ID:</strong> ${item.scan_id}<br>
                    <strong>Priority:</strong> ${item.priority}<br>
                    <strong>Status:</strong> <span class="badge badge-${item.status}">${item.status}</span><br>
                    <strong>Retry:</strong> ${item.retry_count}/${item.max_retries}
                </div>
                <div class="queue-actions">
                    ${item.status === 'pending' ? `<button class="btn-small" onclick="removeFromQueue(${item.id})">Remove</button>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load queue:', error);
        showToast('Failed to load queue', 'error');
    }
}

document.getElementById('refresh-queue-btn')?.addEventListener('click', loadQueue);

// Statistics Dashboard
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();

        const container = document.getElementById('stats-grid');
        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${data.total_scans}</div>
                <div class="stat-label">Total Scans</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.completed_scans}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.failed_scans}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.total_vulnerabilities}</div>
                <div class="stat-label">Vulnerabilities</div>
            </div>
            <div class="stat-card severity-critical">
                <div class="stat-value">${data.critical_vulns}</div>
                <div class="stat-label">Critical</div>
            </div>
            <div class="stat-card severity-high">
                <div class="stat-value">${data.high_vulns}</div>
                <div class="stat-label">High</div>
            </div>
            <div class="stat-card severity-medium">
                <div class="stat-value">${data.medium_vulns}</div>
                <div class="stat-label">Medium</div>
            </div>
            <div class="stat-card severity-low">
                <div class="stat-value">${data.low_vulns}</div>
                <div class="stat-label">Low</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.scan_success_rate.toFixed(1)}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        `;

        const chartsContainer = document.getElementById('stats-charts');
        chartsContainer.innerHTML = `
            <div class="chart-section">
                <h4>Vulnerability Types</h4>
                <div class="chart-bars">
                    ${Object.entries(data.vuln_types).map(([type, count]) => `
                        <div class="chart-bar">
                            <span class="chart-label">${type.replace(/_/g, ' ')}</span>
                            <div class="chart-bar-fill" style="width: ${(count / Math.max(...Object.values(data.vuln_types))) * 100}%"></div>
                            <span class="chart-value">${count}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="chart-section">
                <h4>OWASP Categories</h4>
                <div class="chart-bars">
                    ${Object.entries(data.owasp_categories).map(([cat, count]) => `
                        <div class="chart-bar">
                            <span class="chart-label">${cat}</span>
                            <div class="chart-bar-fill" style="width: ${(count / Math.max(...Object.values(data.owasp_categories))) * 100}%"></div>
                            <span class="chart-value">${count}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load statistics:', error);
        showToast('Failed to load statistics', 'error');
    }
}

// Utility Functions
function notifyVulnerability(vuln) {
    const notification = document.createElement('div');
    notification.className = `vuln-notification severity-${vuln.severity}`;
    notification.innerHTML = `
        <strong>${vuln.vuln_type.replace(/_/g, ' ').toUpperCase()}</strong><br>
        ${vuln.description || 'Vulnerability detected'}
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 5000);
}

function updateScanProgress(progress, text) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');

    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }

    if (progressText) {
        progressText.textContent = text;
    }
}

function appendOutput(text) {
    const output = document.getElementById('output');
    if (output) {
        output.textContent += text + '\\n';
        output.scrollTop = output.scrollHeight;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Enhanced] Initializing new features...');

    // Initialize WebSocket
    initWebSocket();

    // Load data for new tabs
    const observer = new MutationObserver(() => {
        const activeTab = document.querySelector('.tab-content.active');
        if (!activeTab) return;

        switch (activeTab.id) {
            case 'templates':
                loadTemplates();
                break;
            case 'vulnerabilities':
                loadVulnerabilities();
                break;
            case 'queue':
                loadQueue();
                break;
            case 'statistics':
                loadStatistics();
                break;
        }
    });

    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class'],
        subtree: true
    });

    // Set up filter listeners
    document.getElementById('vuln-severity-filter')?.addEventListener('change', loadVulnerabilities);
    document.getElementById('vuln-status-filter')?.addEventListener('change', loadVulnerabilities);

    console.log('[Enhanced] Initialization complete');
});
