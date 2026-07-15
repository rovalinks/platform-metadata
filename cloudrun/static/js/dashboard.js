/**
 * Metadata Governance Dashboard - dashboard.js
 */

let loading = false;
let projectCache = []; // Cache for all discovered projects

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    
    document.getElementById("refresh").addEventListener("click", () => {
        loadDashboard();
    });
    
    document.getElementById("scope").addEventListener("change", onScopeChanged);
    document.getElementById("project").addEventListener("change", loadDashboard);
});

async function loadDashboard() {
    if (loading) return;
    const loader = document.getElementById("loading");
    if (loader) loader.classList.remove("hidden");
    
    loading = true;
    
    try {
        const scope = document.getElementById("scope").value;
        const projectEl = document.getElementById("project");
        const selectedProject = projectEl.value; 
        
        // Guard check
        if (scope === "project" && !selectedProject) {
            loading = false;
            if (loader) loader.classList.add("hidden");
            return;
        }
        
        let url = `/reports/dashboard?scope=${scope}${scope === "project" && selectedProject ? "&project_id=" + selectedProject : ""}`;
        
        const response = await fetch(url);
        const data = await response.json();

        // Render sections
        renderSummaryCards(data.executive_summary);
        renderBrownfield(data.executive_summary.brownfield);
        renderGreenfield(data.executive_summary.greenfield);
        
        // Render Tables/Cards
        if (data.mode === "greenfield") {
            renderGreenfieldProjects(data.projects);
            renderGreenfieldResourceTypes(data.resource_types);
            renderGreenfieldRecentActivity(data.recent_activity);
            document.getElementById("non-compliant-container").innerHTML = "";
        } else {
            renderProjects(data.projects);
            renderResourceTypes(data.resource_types);
            renderRecentRuns(data.recent_activity);
            renderNonCompliant(data.top_non_compliant);
        }

        if (data.all_projects) {
            populateProjects(data.all_projects);
        } else if (scope === "organization") {
            populateProjects(data.projects);
        }
        
        if (selectedProject) {
            projectEl.value = selectedProject;
        }
        
        const lastUpdated = document.getElementById("last-updated");
        if (lastUpdated) lastUpdated.textContent = "Last Updated: " + new Date().toLocaleString();
        
    } catch (err) {
        console.error("Dashboard error:", err);
    } finally {
        loading = false;
        if (loader) loader.classList.add("hidden");
    }
}

// --- Lifecycle & UI Helpers ---

function onScopeChanged() {
    const project = document.getElementById("project");
    const scope = document.getElementById("scope").value;
    project.disabled = scope !== "project";
    if (scope === "organization") {
        loadDashboard();
        return;
    }
    if (!project.value) return;
    loadDashboard();
}

function populateProjects(projects) {
    if (projects.length > projectCache.length) projectCache = projects;
    const select = document.getElementById("project");
    if (!select) return;
    const current = select.value;
    select.innerHTML = '<option value="">Select a project...</option>' + projectCache.map(p => `<option value="${p.project_id}">${p.project_id}</option>`).join("");
    if (projectCache.some(p => p.project_id === current)) select.value = current;
}

// --- Render Functions ---

function renderSummaryCards(summary) {
    const estate = summary.estate;
    const cards = [
        { title: "Resources", icon: "📦", value: formatNumber(estate.total_resources), subtitle: "Discovered resources" },
        { title: "Projects", icon: "📁", value: formatNumber(estate.projects), subtitle: "Managed projects" },
        { title: "Supported", icon: "✅", value: formatNumber(estate.supported_resources), subtitle: "Supported assets" },
        { title: "Compliance", icon: "🛡️", value: estate.compliance_percentage + "%", subtitle: "Overall compliance" }
    ];
    document.getElementById("summary-cards").innerHTML = cards.map(c => `
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><div class="card-title">${c.title}</div><div class="card-value">${c.value}</div><div style="margin-top:8px;color:#64748b;font-size:13px;">${c.subtitle}</div></div>
                <div style="font-size:42px">${c.icon}</div>
            </div>
        </div>`).join("");
}

function renderBrownfield(data) {
    document.getElementById("brownfield-card").innerHTML = `
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;"><h3>🟦 Brownfield</h3><span class="badge badge-info">Remediation</span></div>
            <div class="metric"><div class="metric-title">Planned</div><div class="metric-value">${formatNumber(data.planned)}</div></div>
            <div class="metric"><div class="metric-title">Completed</div><div class="metric-value status-success">${formatNumber(data.completed)}</div></div>
            <div class="metric"><div class="metric-title">Remaining</div><div class="metric-value">${formatNumber(data.remaining)}</div></div>
            <div class="metric"><div class="metric-title">Failed</div><div class="metric-value status-failed">${formatNumber(data.failed)}</div></div>
            <div class="metric"><div class="metric-title">Success Rate</div><div class="metric-value">${data.success_rate}%</div></div>
            <div style="margin-top:18px">${progressBar(data.success_rate)}</div>
        </div>`;
}

function renderGreenfield(data) {
    document.getElementById("greenfield-card").innerHTML = `
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;"><h3>🟩 Greenfield</h3><span class="badge badge-good">Realtime</span></div>
            <div class="metric"><div class="metric-title">Events</div><div class="metric-value">${formatNumber(data.total_events)}</div></div>
            <div class="metric"><div class="metric-title">Successful</div><div class="metric-value status-success">${formatNumber(data.successful)}</div></div>
            <div class="metric"><div class="metric-title">Failed</div><div class="metric-value status-failed">${formatNumber(data.failed)}</div></div>
            <div class="metric"><div class="metric-title">Unsupported</div><div class="metric-value">${formatNumber(data.unsupported)}</div></div>
            <div class="metric"><div class="metric-title">Average Processing</div><div class="metric-value">${data.average_duration_ms} ms</div></div>
            <div class="metric"><div class="metric-title">Last Event</div><div style="font-weight:600">${formatDate(data.last_event)}</div></div>
        </div>`;
}

function renderProjects(projects) {
    const container = document.getElementById("projects-container");
    if (!projects || projects.length === 0) { container.innerHTML = `<div class="panel-empty">No projects found.</div>`; return; }
    container.innerHTML = `
        <div class="project-grid">
            ${projects.map(project => `
                <div class="project-card">
                    <div class="project-header"><div><div class="project-title">${project.project_id}</div><div class="project-subtitle">Google Cloud Project</div></div><div>${statusBadge(project.compliance_percentage)}</div></div>
                    <div class="project-progress">${progressBar(project.compliance_percentage)}</div>
                    <div class="project-metrics">
                        <div class="project-metric"><div class="metric-label">Resources</div><div class="metric-number">${formatNumber(project.total_resources)}</div></div>
                        <div class="project-metric"><div class="metric-label">Compliant</div><div class="metric-number text-success">${formatNumber(project.compliant_resources)}</div></div>
                        <div class="project-metric"><div class="metric-label">Missing</div><div class="metric-number text-danger">${formatNumber(project.non_compliant_resources)}</div></div>
                    </div>
                </div>`).join("")}
        </div>`;
}

function renderResourceTypes(resources) {
    const container = document.getElementById("resource-types-container");
    if (!resources || resources.length === 0) { container.innerHTML = `<div class="panel-empty">No resource types found.</div>`; return; }
    container.innerHTML = `
        <div class="resource-grid">
            ${resources.map(resource => `
                <div class="resource-card">
                    <div class="resource-header"><div><div class="resource-title">${formatAssetType(resource.asset_type)}</div><div class="resource-subtitle">${resource.asset_type}</div></div><div>${statusBadge(resource.compliance_percentage)}</div></div>
                    <div class="resource-progress">${progressBar(resource.compliance_percentage)}</div>
                    <div class="resource-metrics">
                        <div class="resource-metric"><div class="metric-label">Resources</div><div class="metric-number">${formatNumber(resource.total)}</div></div>
                        <div class="resource-metric"><div class="metric-label">Compliant</div><div class="metric-number text-success">${formatNumber(resource.compliant)}</div></div>
                        <div class="resource-metric"><div class="metric-label">Missing</div><div class="metric-number text-danger">${formatNumber(resource.non_compliant)}</div></div>
                    </div>
                </div>`).join("")}
        </div>`;
}

function renderRecentRuns(runs) {
    const container = document.getElementById("recent-runs-container");
    if (!runs || runs.length === 0) {
        container.innerHTML = `<div class="panel-empty">No remediation activity found.</div>`;
        return;
    }
    container.innerHTML = `
        <div class="activity-timeline">
            ${runs.map(run => {
                const success = Number(run.success_rate || 0);
                let badge = "badge-info";
                let icon = "⚡";
                if (success >= 95) { badge = "badge-good"; icon = "🟢"; }
                else if (success >= 80) { badge = "badge-warning"; icon = "🟡"; }
                else { badge = "badge-error"; icon = "🔴"; }
                return `
                    <div class="activity-item">
                        <div class="activity-icon">${icon}</div>
                        <div class="activity-content">
                            <div class="activity-header">
                                <div><div class="activity-title">Run ${shortRunId(run.run_id)}</div><div class="activity-subtitle">Brownfield Remediation</div></div>
                                <div><span class="badge ${badge}">${run.success_rate}%</span></div>
                            </div>
                            <div class="activity-metrics">
                                <div><strong>${formatNumber(run.planned)}</strong><br>Planned</div>
                                <div><strong>${formatNumber(run.completed)}</strong><br>Completed</div>
                                <div><strong>${formatNumber(run.failed)}</strong><br>Failed</div>
                                <div><strong>${formatNumber(run.remaining)}</strong><br>Remaining</div>
                            </div>
                            <div class="activity-footer">Started ${formatDate(run.started)}</div>
                        </div>
                    </div>`;
            }).join("")}
        </div>`;
}

function renderNonCompliant(resources) {
    const container = document.getElementById("non-compliant-container");
    if (!resources || resources.length === 0) {
        container.innerHTML = `
            <div class="panel-empty">
                🎉 Excellent! No non-compliant resources detected.
            </div>
        `;
        return;
    }
    container.innerHTML = `
        <div class="resource-grid">
            ${resources.map(resource => `
                <div class="resource-card noncompliant-card">
                    <div class="resource-header">
                        <div>
                            <div class="resource-title">${shortResource(resource.resource_name)}</div>
                            <div class="resource-subtitle">${resource.project_id || ""}</div>
                        </div>
                        <div><span class="badge badge-error">Attention</span></div>
                    </div>
                    <div class="resource-type">${formatAssetType(resource.asset_type)}</div>
                    <div class="label-section">
                        <div class="label-title">Missing Labels</div>
                        <div class="label-list">${renderLabelBadges(resource.missing_labels, "missing")}</div>
                    </div>
                    <div class="label-section">
                        <div class="label-title">Incorrect Labels</div>
                        <div class="label-list">${renderLabelBadges(resource.incorrect_labels, "incorrect")}</div>
                    </div>
                    <div class="resource-footer">
                        <div>Resource requires remediation</div>
                        <div>⚠️</div>
                    </div>
                </div>
            `).join("")}
        </div>
    `;
}

// --- Greenfield Renderers ---

function renderGreenfieldProjects(p) { document.getElementById("projects-container").innerHTML = `<table class="data-table"><thead><tr><th>Project</th><th>Events</th><th>Successful</th><th>Failed</th></tr></thead><tbody>${p.map(x => `<tr><td>${x.project_id}</td><td>${formatNumber(x.total_events)}</td><td>${formatNumber(x.successful)}</td><td>${formatNumber(x.failed)}</td></tr>`).join("")}</tbody></table>`; }

function renderGreenfieldResourceTypes(r) { document.getElementById("resource-types-container").innerHTML = `<table class="data-table"><thead><tr><th>Resource Type</th><th>Events</th><th>Successful</th><th>Failed</th></tr></thead><tbody>${r.map(x => `<tr><td>${formatAssetType(x.asset_type)}</td><td>${formatNumber(x.total_events)}</td><td>${formatNumber(x.successful)}</td><td>${formatNumber(x.failed)}</td></tr>`).join("")}</tbody></table>`; }

function renderGreenfieldRecentActivity(activity) {
    const container = document.getElementById("recent-runs-container");
    if (!activity || activity.length === 0) {
        container.innerHTML = `<div class="panel-empty">No recent Greenfield activity found.</div>`;
        return;
    }
    container.innerHTML = `
        <div class="activity-timeline">
            ${activity.map(event => {
                let badge = "badge-info";
                let icon = "⚡";
                switch ((event.status || "").toUpperCase()) {
                    case "SUCCESS": badge = "badge-good"; icon = "🟢"; break;
                    case "FAILED": badge = "badge-error"; icon = "🔴"; break;
                    case "RUNNING": badge = "badge-warning"; icon = "🟡"; break;
                    default: badge = "badge-info"; icon = "🔵";
                }
                return `
                    <div class="activity-item">
                        <div class="activity-icon">${icon}</div>
                        <div class="activity-content">
                            <div class="activity-header">
                                <div>
                                    <div class="activity-title">${operationIcon(event.operation)} ${formatAssetType(event.asset_type)}</div>
                                    <div class="activity-subtitle">${shortResource(event.resource_name)}</div>
                                </div>
                                <span class="badge ${badge}">${event.status}</span>
                            </div>
                            <div class="activity-metrics">
                                <div><strong>${event.project_id}</strong><br>Project</div>
                                <div><strong>${event.duration_ms}</strong><br>ms</div>
                                <div><strong>${event.execution_mode || "GREENFIELD"}</strong><br>Mode</div>
                                <div><strong>${event.operation || "CREATE"}</strong><br>Operation</div>
                            </div>
                            <div class="activity-footer">${formatDate(event.executed_at)}</div>
                        </div>
                    </div>`;
            }).join("")}
        </div>`;
}

// --- Helpers ---

function formatNumber(v) { return Number(v).toLocaleString(); }

function formatLabels(v) { 
    if (!v || v === "[]") return "-"; 
    try { const l = typeof v === 'string' ? JSON.parse(v) : v; return l.length === 0 ? "-" : l.join(", "); } catch { return v; } 
}

function renderLabelBadges(labels, type) {
    if (!labels || labels === "[]") {
        return `<span class="badge badge-good">None</span>`;
    }
    try {
        const list = typeof labels === "string" ? JSON.parse(labels) : labels;
        if (list.length === 0) {
            return `<span class="badge badge-good">None</span>`;
        }
        return list.map(label => `
            <span class="badge ${type === "missing" ? "badge-error" : "badge-warning"}">${label}</span>
        `).join(" ");
    } catch {
        return `<span class="badge badge-warning">${labels}</span>`;
    }
}

function formatAssetType(a) { 
    const n = { "compute.googleapis.com/Instance": "Compute Instance", "compute.googleapis.com/Disk": "Compute Disk", "compute.googleapis.com/Address": "Static IP", "compute.googleapis.com/ForwardingRule": "Forwarding Rule", "storage.googleapis.com/Bucket": "Cloud Storage Bucket", "bigquery.googleapis.com/Dataset": "BigQuery Dataset", "pubsub.googleapis.com/Topic": "Pub/Sub Topic", "artifactregistry.googleapis.com/Repository": "Artifact Registry", "container.googleapis.com/Cluster": "GKE Cluster", "container.googleapis.com/NodePool": "GKE Node Pool", "sqladmin.googleapis.com/Instance": "Cloud SQL", "secretmanager.googleapis.com/Secret": "Secret Manager Secret", "cloudkms.googleapis.com/CryptoKey": "Cloud KMS Key" }; 
    return n[a] || a; 
}

function operationIcon(operation) {
    switch ((operation || "").toUpperCase()) {
        case "CREATE": return "➕";
        case "UPDATE": return "✏️";
        case "DELETE": return "🗑️";
        default: return "⚡";
    }
}

function shortRunId(id) { return id.substring(0, 8); }
function formatDate(v) { return new Date(v).toLocaleString(); }
function shortResource(n) { return n.split("/").pop(); }
function statusBadge(v) { if (v >= 95) return `<span class="badge badge-good">${v}%</span>`; if (v >= 80) return `<span class="badge badge-warning">${v}%</span>`; return `<span class="badge badge-error">${v}%</span>`; }
function progressBar(v) { return `<div class="progress"><div class="progress-fill" style="width:${v}%"></div></div>`; }