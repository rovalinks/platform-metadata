/**
 * Metadata Governance Dashboard - dashboard.js
 */

let loading = false;
let projectCache = []; // Cache for all discovered projects[cite: 2]

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
        
        // Construct URL
        let url = `/reports/dashboard?scope=${scope}${scope === "project" && selectedProject ? "&project_id=" + selectedProject : ""}`;
        
        const response = await fetch(url);
        const data = await response.json();

        // Render sections
        renderSummaryCards(data.executive_summary);
        renderBrownfield(data.executive_summary.brownfield);
        renderGreenfield(data.executive_summary.greenfield);
        
        // Render Tables
        renderProjects(data.projects);
        renderResourceTypes(data.resource_types);
        renderRecentRuns(data.recent_runs);
        renderNonCompliant(data.top_non_compliant);

        // Update project list logic
        if (data.all_projects) {
            populateProjects(data.all_projects);
        } else if (scope === "organization") {
            populateProjects(data.projects);
        }
        
        // Preserve selected project after refresh
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

    if (project.value === "") {
        project.selectedIndex = 0;
    }

    loadDashboard();
}

function populateProjects(projects) {
    // Only cache if the incoming project list is larger than current cache
    if (projects.length > projectCache.length) {
        projectCache = projects;
    }

    const select = document.getElementById("project");
    if (!select) return;

    const current = select.value;

    select.innerHTML = projectCache.map(project =>
        `<option value="${project.project_id}">${project.project_id}</option>`
    ).join("");

    if (projectCache.some(project => project.project_id === current)) {
        select.value = current;
    }
}

// --- Render Functions ---

function renderSummaryCards(summary) {
    const estate = summary.estate;
    const cards = [
        { title: "Resources", value: formatNumber(estate.total_resources) },
        { title: "Projects", value: formatNumber(estate.projects) },
        { title: "Supported", value: formatNumber(estate.supported_resources) },
        { title: "Compliance", value: statusBadge(estate.compliance_percentage) },
    ];
    document.getElementById("summary-cards").innerHTML = cards.map(card => `
        <div class="card">
            <div class="card-title">${card.title}</div>
            <div class="card-value">${card.value}</div>
        </div>
    `).join("");
}

function renderBrownfield(data) {
    document.getElementById("brownfield-card").innerHTML = `
        <div class="card">
            <h3>Brownfield</h3>
            <table class="summary-table">
                <tr><td>Planned</td><td>${formatNumber(data.planned)}</td></tr>
                <tr><td>Completed</td><td>${formatNumber(data.completed)}</td></tr>
                <tr><td>Remaining</td><td>${formatNumber(data.remaining)}</td></tr>
                <tr><td>Failed</td><td>${formatNumber(data.failed)}</td></tr>
                <tr><td>Success Rate</td><td>${data.success_rate}%</td></tr>
            </table>
        </div>`;
}

function renderGreenfield(data) {
    document.getElementById("greenfield-card").innerHTML = `
        <div class="card">
            <h3>Greenfield</h3>
            <table class="summary-table">
                <tr><td>Events</td><td>${formatNumber(data.total_events)}</td></tr>
                <tr><td>Remediated</td><td>${formatNumber(data.remediated)}</td></tr>
                <tr><td>Compliant</td><td>${formatNumber(data.compliant)}</td></tr>
                <tr><td>Failed</td><td>${formatNumber(data.failed)}</td></tr>
                <tr><td>Avg Latency</td><td>${data.average_duration_ms} ms</td></tr>
            </table>
        </div>`;
}

function renderProjects(projects) {
    const container = document.getElementById("projects-container");
    if (!projects || projects.length === 0) {
        container.innerHTML = '<div class="card">No projects found.</div>';
        return;
    }
    container.innerHTML = `<table class="data-table"><thead><tr><th>Project</th><th>Resources</th><th>Compliant</th><th>Non-Compliant</th><th>Compliance</th><th>Progress</th></tr></thead><tbody>${projects.map(p => `<tr><td>${p.project_id}</td><td>${formatNumber(p.total_resources)}</td><td>${formatNumber(p.compliant_resources)}</td><td>${formatNumber(p.non_compliant_resources)}</td><td>${statusBadge(p.compliance_percentage)}</td><td>${progressBar(p.compliance_percentage)}</td></tr>`).join("")}</tbody></table>`;
}

function renderResourceTypes(resources) {
    const container = document.getElementById("resource-types-container");
    if (!resources || resources.length === 0) {
        container.innerHTML = '<div class="card">No resource types found.</div>';
        return;
    }
    container.innerHTML = `<table class="data-table"><thead><tr><th>Resource Type</th><th>Total</th><th>Compliant</th><th>Non-Compliant</th><th>Compliance</th><th>Progress</th></tr></thead><tbody>${resources.map(r => `<tr><td>${formatAssetType(r.asset_type)}</td><td>${formatNumber(r.total)}</td><td>${formatNumber(r.compliant)}</td><td>${formatNumber(r.non_compliant)}</td><td>${statusBadge(r.compliance_percentage)}</td><td>${progressBar(r.compliance_percentage)}</td></tr>`).join("")}</tbody></table>`;
}

function renderRecentRuns(runs) {
    const container = document.getElementById("recent-runs-container");
    if (!runs || runs.length === 0) {
        container.innerHTML = '<div class="card">No remediation runs found.</div>';
        return;
    }
    container.innerHTML = `<table class="data-table"><thead><tr><th>Run ID</th><th>Planned</th><th>Completed</th><th>Failed</th><th>Remaining</th><th>Success</th><th>Started</th></tr></thead><tbody>${runs.map(r => `<tr><td>${shortRunId(r.run_id)}</td><td>${formatNumber(r.planned)}</td><td>${formatNumber(r.completed)}</td><td>${formatNumber(r.failed)}</td><td>${formatNumber(r.remaining)}</td><td>${r.success_rate}%</td><td>${formatDate(r.started)}</td></tr>`).join("")}</tbody></table>`;
}

function renderNonCompliant(resources) {
    const container = document.getElementById("non-compliant-container");
    if (!resources || resources.length === 0) {
        container.innerHTML = '<div class="card">No non-compliant resources found.</div>';
        return;
    }
    container.innerHTML = `<table class="data-table"><thead><tr><th>Resource</th><th>Type</th><th>Missing Labels</th><th>Incorrect Labels</th></tr></thead><tbody>${resources.map(r => `<tr><td>${shortResource(r.resource_name)}</td><td>${formatAssetType(r.asset_type)}</td><td>${formatLabels(r.missing_labels)}</td><td>${formatLabels(r.incorrect_labels)}</td></tr>`).join("")}</tbody></table>`;
}

// --- Formatting Helpers ---

function formatNumber(v) { return Number(v).toLocaleString(); }

function formatLabels(value) {
    if (!value || value === "[]") return "-";
    try {
        const labels = typeof value === 'string' ? JSON.parse(value) : value;
        return labels.length === 0 ? "-" : labels.join(", ");
    } catch { return value; }
}

function formatAssetType(asset) {
    const names = {
        "compute.googleapis.com/Instance": "Compute Instance",
        "compute.googleapis.com/Disk": "Compute Disk",
        "compute.googleapis.com/Address": "Static IP",
        "compute.googleapis.com/ForwardingRule": "Forwarding Rule",
        "storage.googleapis.com/Bucket": "Cloud Storage Bucket",
        "bigquery.googleapis.com/Dataset": "BigQuery Dataset",
        "pubsub.googleapis.com/Topic": "Pub/Sub Topic",
        "artifactregistry.googleapis.com/Repository": "Artifact Registry",
        "container.googleapis.com/Cluster": "GKE Cluster",
        "container.googleapis.com/NodePool": "GKE Node Pool",
        "sqladmin.googleapis.com/Instance": "Cloud SQL",
        "secretmanager.googleapis.com/Secret": "Secret Manager Secret",
        "cloudkms.googleapis.com/CryptoKey": "Cloud KMS Key"
    };
    return names[asset] || asset;
}

function shortRunId(id) { return id.substring(0, 8); }
function formatDate(value) { return new Date(value).toLocaleString(); }
function shortResource(name) { return name.split("/").pop(); }

function statusBadge(value) {
    if (value >= 95) return `<span class="badge badge-good">${value}%</span>`;
    if (value >= 80) return `<span class="badge badge-warning">${value}%</span>`;
    return `<span class="badge badge-error">${value}%</span>`;
}

function progressBar(value) {
    return `<div class="progress"><div class="progress-fill" style="width:${value}%"></div></div>`;
}