/* =========================================================
   SMARTFLOW - AI-BASED ADAPTIVE TRAFFIC SIGNAL MANAGEMENT
   Four-way intersection monitoring dashboard
========================================================= */

let junctions = [];
let analyses = {};
let validations = {};

let selectedJunctionId = "J01";
let selectedDirection = "North";

const DIRECTIONS = ["North", "East", "South", "West"];

document.addEventListener("DOMContentLoaded", initializeSmartFlow);


/* =========================================================
   INITIALIZATION
========================================================= */

async function initializeSmartFlow() {
    setupNavigation();

    const refreshButton = document.getElementById("refresh-btn");

    if (refreshButton && !refreshButton.dataset.bound) {
        refreshButton.addEventListener("click", initializeSmartFlow);
        refreshButton.dataset.bound = "true";
    }

    try {
        const response = await fetch("../data/junctions.json");

        if (!response.ok) {
            throw new Error("Unable to load data/junctions.json");
        }

        const config = await response.json();
        junctions = config.junctions || [];

        await loadJunctionData();

        if (!junctions.some(j => j.id === selectedJunctionId)) {
            selectedJunctionId =
                junctions.find(j => j.status === "analyzed")?.id || "J01";
        }

        renderEverything();

        window.SmartFlow = {
            junctions,
            analyses,
            validations
        };

    } catch (error) {
        console.error("SmartFlow initialization error:", error);
        showLoadError(error.message);
    }
}


/* =========================================================
   LOAD ANALYSIS AND VALIDATION FILES
========================================================= */

async function loadJunctionData() {
    analyses = {};
    validations = {};

    for (const junction of junctions) {
        if (junction.status !== "analyzed") continue;

        if (junction.analysis_file) {
            try {
                const response = await fetch(junction.analysis_file);

                if (response.ok) {
                    analyses[junction.id] = await response.json();
                }
            } catch (error) {
                console.warn("Analysis could not load:", junction.id, error);
            }
        }

        if (junction.validation_file) {
            try {
                const response = await fetch(junction.validation_file);

                if (response.ok) {
                    validations[junction.id] = await response.json();
                }
            } catch (error) {
                console.warn("Validation could not load:", junction.id, error);
            }
        }
    }
}


/* =========================================================
   RENDER ALL DASHBOARD SECTIONS
========================================================= */

function renderEverything() {
    renderKPIs();
    renderJunctionNetwork();
    renderJunctionManagement();
    renderMonitoring(selectedJunctionId);
    renderAnalytics();
    renderValidation();
    renderNetworkSummary();
}


/* =========================================================
   HELPER FUNCTIONS
========================================================= */

function getAnalysis(junctionId) {
    return analyses[junctionId] || null;
}

function getTraffic(junctionId) {
    return getAnalysis(junctionId)?.analysis || {};
}

function getSignal(junctionId) {
    return getAnalysis(junctionId)?.adaptive_signal || {};
}

function getDirectionExamples() {
    /*
       Direction-specific values are illustrative.
       The current Python pipeline analyzes the video overall;
       it does not validate separate counts for each direction.
    */
    return [
        { direction: "North", vehicles: 18, queue: 6, density: "Medium" },
        { direction: "East", vehicles: 14, queue: 4, density: "Medium" },
        { direction: "South", vehicles: 17, queue: 5, density: "Medium" },
        { direction: "West", vehicles: 14, queue: 3, density: "Low" }
    ];
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function densityClass(density) {
    const normalized = String(density || "").toLowerCase();

    if (normalized === "high") return "density-high";
    if (normalized === "medium") return "density-medium";
    if (normalized === "low") return "density-low";

    return "";
}


/* =========================================================
   KPI CARDS
========================================================= */

function renderKPIs() {
    const active = junctions.filter(j => j.status === "analyzed").length;

    let vehicles = 0;
    let queue = 0;

    Object.values(analyses).forEach(data => {
        vehicles += Number(data.analysis?.unique_vehicles || 0);
        queue += Number(data.analysis?.estimated_queue || 0);
    });

    setText("kpi-junctions", junctions.length);
    setText("kpi-active", active);
    setText("kpi-vehicles", vehicles);
    setText("kpi-queue", queue);
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}


/* =========================================================
   JUNCTION NETWORK
========================================================= */

function renderJunctionNetwork() {
    const container = document.getElementById("junction-network");
    if (!container) return;

    container.innerHTML = junctions.map(createJunctionCard).join("");
}

function renderJunctionManagement() {
    const container = document.getElementById("junction-management");
    if (!container) return;

    container.innerHTML = junctions.map(createJunctionCard).join("");
}

function createJunctionCard(junction) {
    const analysis = getAnalysis(junction.id);
    const traffic = analysis?.analysis || {};
    const signal = analysis?.adaptive_signal || {};
    const active = junction.status === "analyzed" && analysis;

    if (!active) {
        return `
            <article class="junction-card">
                <div class="junction-card-top">
                    <div class="junction-id">${escapeHTML(junction.id)}</div>
                    <h3>${escapeHTML(junction.name)}</h3>
                    <div class="junction-location">
                        ${escapeHTML(junction.location)}
                    </div>
                    <div class="junction-status pending">
                        <span class="status-dot"></span>
                        ANALYSIS PENDING
                    </div>
                </div>
                <div class="junction-body">
                    <div class="empty-state">
                        <h3>Awaiting configuration</h3>
                        <p>Video and AI analysis are not configured.</p>
                    </div>
                </div>
            </article>
        `;
    }

    return `
        <article class="junction-card">
            <div class="junction-card-top">
                <div class="junction-id">${escapeHTML(junction.id)}</div>
                <h3>${escapeHTML(junction.name)}</h3>
                <div class="junction-location">
                    ${escapeHTML(junction.location)}
                </div>
                <div class="junction-status active">
                    <span class="status-dot"></span>
                    ANALYSIS AVAILABLE
                </div>
            </div>

            <div class="junction-body">
                <div class="junction-metrics">
                    <div class="metric">
                        <span>Vehicles</span>
                        <strong>${traffic.unique_vehicles ?? "—"}</strong>
                    </div>
                    <div class="metric">
                        <span>Estimated Queue</span>
                        <strong>${traffic.estimated_queue ?? "—"}</strong>
                    </div>
                    <div class="metric">
                        <span>Density</span>
                        <strong>${escapeHTML(traffic.traffic_density ?? "—")}</strong>
                    </div>
                    <div class="metric">
                        <span>Green Time</span>
                        <strong>${signal.recommended_green_time_seconds ?? "—"} sec</strong>
                    </div>
                </div>

                <button class="junction-action"
                    onclick="openJunction('${escapeHTML(junction.id)}')">
                    Open Traffic Control →
                </button>
            </div>
        </article>
    `;
}


/* =========================================================
   OPEN A JUNCTION
========================================================= */

function openJunction(junctionId) {
    const junction = junctions.find(j => j.id === junctionId);

    if (!junction) return;

    if (junction.status !== "analyzed" || !getAnalysis(junctionId)) {
        alert(`${junction.name} is awaiting AI analysis.`);
        return;
    }

    selectedJunctionId = junctionId;
    showPage("monitoring");
    renderMonitoring(junctionId);
}


/* =========================================================
   LIVE MONITORING
========================================================= */

function renderMonitoring(junctionId = selectedJunctionId) {
    const container = document.getElementById("monitoring-content");
    if (!container) return;

    selectedJunctionId = junctionId;

    const junction = junctions.find(j => j.id === junctionId);
    const analysis = getAnalysis(junctionId);

    if (!junction || !analysis) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No analyzed junction available</h3>
                <p>Configure a video and run the AI analysis first.</p>
            </div>
        `;
        return;
    }

    const traffic = analysis.analysis || {};
    const signal = analysis.adaptive_signal || {};
    const pipeline = analysis.ai_pipeline || {};
    const vehicles = analysis.vehicle_classification || {};
    const videoFile = junction.video_file || "../data/traffic_video.mp4";
    const directionData = getDirectionExamples();

    const density = traffic.traffic_density || "Unknown";
    const densityCSS = densityClass(density);

    container.innerHTML = `
        <div class="control-center">

            <div class="control-toolbar">
                <div>
                    <span class="control-kicker">INTERSECTION OPERATIONS</span>
                    <h2>${escapeHTML(junction.name)}</h2>
                    <p>${escapeHTML(junction.location)}</p>
                </div>

                <div class="control-badges">
                    <span class="control-badge badge-available">
                        <span class="status-dot"></span>
                        ANALYSIS AVAILABLE
                    </span>
                    <span class="control-badge">
                        ${escapeHTML(junction.id)}
                    </span>
                </div>
            </div>

            <div class="control-kpis">
                <div class="control-kpi">
                    <span>Total Vehicles Detected</span>
                    <strong>${traffic.unique_vehicles ?? "—"}</strong>
                    <small>Recorded video analysis</small>
                </div>

                <div class="control-kpi">
                    <span>Estimated Queue</span>
                    <strong>${traffic.estimated_queue ?? "—"}</strong>
                    <small>Approximate queue estimate</small>
                </div>

                <div class="control-kpi">
                    <span>Traffic Density</span>
                    <strong class="${densityCSS}">
                        ${escapeHTML(density)}
                    </strong>
                    <small>AI analysis result</small>
                </div>

                <div class="control-kpi">
                    <span>Recommended Green</span>
                    <strong>
                        ${signal.recommended_green_time_seconds ?? "—"}
                        <small class="unit">sec</small>
                    </strong>
                    <small>Prototype timing recommendation</small>
                </div>
            </div>

            <div class="intersection-layout">

                <section class="intersection-panel">
                    <div class="intersection-panel-header">
                        <div>
                            <span class="control-kicker">ROAD NETWORK</span>
                            <h3>Four-Way Intersection</h3>
                        </div>
                        <span class="illustrative-label">
                            ILLUSTRATIVE VIEW
                        </span>
                    </div>

                    <div class="intersection-stage">

                        <div class="direction-label north-label">
                            <strong>NORTH</strong>
                            <span>Approach N</span>
                        </div>

                        <div class="direction-label east-label">
                            <strong>EAST</strong>
                            <span>Approach E</span>
                        </div>

                        <div class="direction-label south-label">
                            <strong>SOUTH</strong>
                            <span>Approach S</span>
                        </div>

                        <div class="direction-label west-label">
                            <strong>WEST</strong>
                            <span>Approach W</span>
                        </div>

                        <div class="road road-vertical"></div>
                        <div class="road road-horizontal"></div>

                        <div class="lane-divider lane-divider-vertical"></div>
                        <div class="lane-divider lane-divider-horizontal"></div>

                        <div class="crosswalk crosswalk-north"></div>
                        <div class="crosswalk crosswalk-south"></div>
                        <div class="crosswalk crosswalk-east"></div>
                        <div class="crosswalk crosswalk-west"></div>

                        <div class="intersection-center">
                            <span>SMARTFLOW</span>
                            <strong>AI</strong>
                            <small>JUNCTION</small>
                        </div>

                        ${renderSignal("North", "signal-north")}
                        ${renderSignal("East", "signal-east")}
                        ${renderSignal("South", "signal-south")}
                        ${renderSignal("West", "signal-west")}

                        <div class="road-vehicles vehicles-north">
                            <span>🚗</span><span>🏍️</span><span>🚙</span>
                        </div>

                        <div class="road-vehicles vehicles-east">
                            <span>🚕</span><span>🚗</span>
                        </div>

                        <div class="road-vehicles vehicles-south">
                            <span>🏍️</span><span>🚗</span><span>🚌</span>
                        </div>

                        <div class="road-vehicles vehicles-west">
                            <span>🚙</span><span>🏍️</span>
                        </div>

                    </div>

                    <div class="intersection-legend">
                        <span><i class="legend-dot legend-red"></i> Red</span>
                        <span><i class="legend-dot legend-amber"></i> Amber</span>
                        <span><i class="legend-dot legend-green"></i> Green</span>
                        <span class="illustrative-label">
                            Signal states are illustrative
                        </span>
                    </div>

                    <div class="direction-grid">
                        ${directionData.map(item => `
                            <button
                                class="direction-card ${selectedDirection === item.direction ? "direction-selected" : ""}"
                                onclick="selectDirection('${item.direction}')">

                                <div class="direction-card-top">
                                    <strong>${item.direction}</strong>
                                    <span class="direction-status">
                                        ${item.density}
                                    </span>
                                </div>

                                <div class="direction-numbers">
                                    <div>
                                        <strong>${item.vehicles}</strong>
                                        <span>Vehicles*</span>
                                    </div>
                                    <div>
                                        <strong>${item.queue}</strong>
                                        <span>Queue*</span>
                                    </div>
                                </div>

                                <div class="direction-card-footer">
                                    Illustrative directional data
                                </div>
                            </button>
                        `).join("")}
                    </div>

                    <p class="data-disclaimer">
                        *Directional vehicle counts and queues are illustrative
                        placeholders, not measured AI outputs. The current
                        model provides aggregate video-analysis results.
                    </p>
                </section>

                <aside class="control-side">

                    <section class="control-panel signal-recommendation-panel">
                        <div class="panel-heading-row">
                            <div>
                                <span class="control-kicker">AI DECISION</span>
                                <h3>Signal Recommendation</h3>
                            </div>
                            <span class="decision-icon">✦</span>
                        </div>

                        <div class="recommended-time">
                            <strong>
                                ${signal.recommended_green_time_seconds ?? "—"}
                            </strong>
                            <span>SECONDS</span>
                        </div>

                        <div class="decision-banner">
                            <span class="decision-indicator"></span>
                            ${escapeHTML(signal.signal_decision || "NO DECISION")}
                        </div>

                        <p class="decision-description">
                            ${escapeHTML(
                                signal.decision_reason ||
                                "No signal recommendation is available."
                            )}
                        </p>

                        <div class="recommendation-meta">
                            <span>Algorithm</span>
                            <strong>Queue-based heuristic</strong>
                        </div>

                        <div class="recommendation-meta">
                            <span>Timing limits</span>
                            <strong>20–60 seconds</strong>
                        </div>

                        <p class="prototype-notice">
                            Prototype recommendation only. No physical traffic
                            signal is controlled by this dashboard.
                        </p>
                    </section>

                    <section class="control-panel">
                        <div class="panel-heading-row">
                            <div>
                                <span class="control-kicker">COMPUTER VISION</span>
                                <h3>AI Pipeline</h3>
                            </div>
                            <span class="pipeline-count">8 stages</span>
                        </div>

                        <div class="control-pipeline">
                            ${pipelineRow("YOLOv8 Detection", pipeline.vehicle_detection)}
                            ${pipelineRow("ByteTrack Tracking", pipeline.multi_object_tracking)}
                            ${pipelineRow("Vehicle Counting", pipeline.vehicle_counting)}
                            ${pipelineRow("Classification", pipeline.vehicle_classification)}
                            ${pipelineRow("Queue Estimation", pipeline.queue_estimation)}
                            ${pipelineRow("Traffic Density", pipeline.traffic_density)}
                            ${pipelineRow("Green-Time Calculation", pipeline.adaptive_green_time)}
                            ${pipelineRow("Signal Decision", pipeline.signal_decision)}
                        </div>
                    </section>

                </aside>
            </div>

            <div class="monitor-lower-grid">

                <section class="control-panel recorded-video-panel">
                    <div class="panel-heading-row">
                        <div>
                            <span class="control-kicker">SOURCE FOOTAGE</span>
                            <h3>Recorded Traffic Video</h3>
                        </div>
                        <span class="recorded-badge">RECORDED</span>
                    </div>

                    <video class="traffic-video" controls preload="metadata">
                        <source src="${escapeHTML(videoFile)}" type="video/mp4">
                        Your browser does not support HTML5 video.
                    </video>

                    <p class="video-caption">
                        Recorded case-study footage. The displayed AI metrics
                        are generated by the Python analysis pipeline.
                    </p>
                </section>

                <section class="control-panel">
                    <div class="panel-heading-row">
                        <div>
                            <span class="control-kicker">VEHICLE BREAKDOWN</span>
                            <h3>Detected Vehicle Classes</h3>
                        </div>
                    </div>

                    ${renderVehicleBars(vehicles, traffic.unique_vehicles)}

                    <div class="vehicle-summary">
                        <span>Frames Processed</span>
                        <strong>${traffic.frames_processed ?? analysis.analysis?.total_frames ?? "—"}</strong>
                    </div>

                    <div class="vehicle-summary">
                        <span>Video Duration</span>
                        <strong>
                            ${traffic.video_duration_seconds ??
                            analysis.analysis?.video_duration_seconds ??
                            "—"} sec
                        </strong>
                    </div>
                </section>

            </div>

        </div>
    `;
}


/* =========================================================
   INTERSECTION SIGNALS
========================================================= */

function renderSignal(direction, positionClass) {
    /*
       This is a visual prototype only.
       It does not represent actual independently controlled
       signals for the four approaches.
    */
    const state = direction === "North" ? "green" : "red";

    return `
        <div class="intersection-signal ${positionClass}">
            <span class="signal-direction">${direction}</span>
            <div class="signal-housing">
                <i class="light-red ${state === "red" ? "on" : ""}"></i>
                <i class="light-amber"></i>
                <i class="light-green ${state === "green" ? "on" : ""}"></i>
            </div>
        </div>
    `;
}


/* =========================================================
   DIRECTION CARD INTERACTION
========================================================= */

function selectDirection(direction) {
    selectedDirection = direction;
    renderMonitoring(selectedJunctionId);
}


/* =========================================================
   AI PIPELINE ROWS
========================================================= */

function pipelineRow(label, status) {
    const completed = String(status || "").toLowerCase() === "completed";

    return `
        <div class="control-pipeline-row">
            <span class="pipeline-stage-icon">
                ${completed ? "✓" : "•"}
            </span>

            <span class="pipeline-stage-label">${escapeHTML(label)}</span>

            <span class="pipeline-stage-status ${completed ? "stage-completed" : "stage-pending"}">
                ${escapeHTML(status || "Pending")}
            </span>
        </div>
    `;
}


/* =========================================================
   VEHICLE COMPOSITION BARS
========================================================= */

function renderVehicleBars(vehicles, total) {
    const rows = [
        ["Cars", Number(vehicles.car || 0)],
        ["Motorcycles", Number(vehicles.motorcycle || 0)],
        ["Buses", Number(vehicles.bus || 0)],
        ["Trucks", Number(vehicles.truck || 0)]
    ];

    const denominator = Math.max(Number(total || 0), 1);

    return `
        <div class="vehicle-bars">
            ${rows.map(([label, count]) => {
                const percent = Math.min(100, (count / denominator) * 100);

                return `
                    <div class="vehicle-bar-row">
                        <div class="vehicle-bar-label">
                            <span>${label}</span>
                            <strong>${count}</strong>
                        </div>
                        <div class="vehicle-bar-track">
                            <div class="vehicle-bar-fill" style="width:${percent}%"></div>
                        </div>
                    </div>
                `;
            }).join("")}
        </div>
    `;
}


/* =========================================================
   ANALYTICS PAGE
========================================================= */

function renderAnalytics() {
    const container = document.getElementById("analytics-content");
    if (!container) return;

    const data = getAnalysis("J01");

    if (!data) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No analytics available</h3>
                <p>Run an AI analysis first.</p>
            </div>
        `;
        return;
    }

    const vehicles = data.vehicle_classification || {};
    const total = Number(data.analysis?.unique_vehicles || 0);

    const rows = [
        ["Cars", Number(vehicles.car || 0)],
        ["Motorcycles", Number(vehicles.motorcycle || 0)],
        ["Buses", Number(vehicles.bus || 0)],
        ["Trucks", Number(vehicles.truck || 0)]
    ];

    container.innerHTML = `
        <div class="analytics-grid">

            <div class="panel">
                <div class="panel-header">
                    <div>
                        <h3>Vehicle Composition</h3>
                        <span>Oppanakara Street</span>
                    </div>
                </div>

                ${rows.map(([name, value]) => {
                    const percent = total ? value / total * 100 : 0;

                    return `
                        <div class="chart-row">
                            <div class="chart-label">
                                <span>${name}</span>
                                <strong>${value}</strong>
                            </div>
                            <div class="chart-track">
                                <div class="chart-fill" style="width:${percent}%"></div>
                            </div>
                        </div>
                    `;
                }).join("")}
            </div>

            <div class="panel">
                <div class="panel-header">
                    <div>
                        <h3>Traffic Snapshot</h3>
                        <span>Actual Python analysis output</span>
                    </div>
                </div>

                <div class="summary-list">
                    <div class="summary-row">
                        <span>Total Vehicles</span>
                        <strong>${total}</strong>
                    </div>

                    <div class="summary-row">
                        <span>Heavy Vehicles</span>
                        <strong>${vehicles.heavy_vehicles ?? "—"}</strong>
                    </div>

                    <div class="summary-row">
                        <span>Queue Ratio</span>
                        <strong>${data.analysis?.queue_ratio_percent ?? "—"}%</strong>
                    </div>

                    <div class="summary-row">
                        <span>Traffic Density</span>
                        <strong>${escapeHTML(data.analysis?.traffic_density ?? "—")}</strong>
                    </div>
                </div>
            </div>
        </div>
    `;
}


/* =========================================================
   VALIDATION PAGE
========================================================= */

function renderValidation() {
    const container = document.getElementById("validation-content");
    if (!container) return;

    const validation = validations["J01"];

    if (!validation) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No validation data available</h3>
                <p>Run the validation script first.</p>
            </div>
        `;
        return;
    }

    // Read the actual Python validation JSON structure
    const signal = validation.signal_comparison || {};
    const performance = validation.performance_metrics || {};

    const fixedGreen = signal.fixed_green_time_seconds;
    const adaptiveGreen = signal.adaptive_green_time_seconds;
    const throughput = performance.estimated_throughput;
    const reduction = performance.queue_reduction_percentage;

    container.innerHTML = `
        <div class="validation-grid">

            <div class="validation-card">
                <span>Fixed Green Time</span>
                <strong>${fixedGreen ?? "—"}${fixedGreen != null ? "s" : ""}</strong>
            </div>

            <div class="validation-card">
                <span>Adaptive Green Time</span>
                <strong>${adaptiveGreen ?? "—"}${adaptiveGreen != null ? "s" : ""}</strong>
            </div>

            <div class="validation-card">
                <span>Estimated Throughput</span>
                <strong>${throughput ?? "—"}</strong>
            </div>

            <div class="validation-card">
                <span>Estimated Queue Reduction</span>
                <strong>${reduction != null ? `${reduction}%` : "—"}</strong>
            </div>

        </div>

        <div class="panel validation-note">
            <strong>Prototype Validation Notice</strong>
            <p>
                These validation metrics are prototype estimates. They are
                not measured field improvements or a guarantee of real-world
                traffic reduction.
            </p>
        </div>
    `;
}


/* =========================================================
   NETWORK SUMMARY
========================================================= */

function renderNetworkSummary() {
    const analyzed = Object.values(analyses);

    if (!analyzed.length) return;

    const priority = { High: 3, Medium: 2, Low: 1 };

    const densities = analyzed
        .map(item => item.analysis?.traffic_density)
        .filter(Boolean);

    densities.sort((a, b) => (priority[b] || 0) - (priority[a] || 0));

    const density = densities[0] || "—";

    const greenTimes = analyzed
        .map(item => Number(item.adaptive_signal?.recommended_green_time_seconds))
        .filter(Number.isFinite);

    const averageGreen = greenTimes.length
        ? Math.round(greenTimes.reduce((sum, value) => sum + value, 0) / greenTimes.length)
        : "—";

    const highCount = analyzed.filter(
        item => item.analysis?.traffic_density === "High"
    ).length;

    setText("summary-density", density);
    setText("summary-green", averageGreen === "—" ? "—" : `${averageGreen} sec`);
    setText("summary-high", highCount);
}


/* =========================================================
   NAVIGATION
========================================================= */

function setupNavigation() {
    document.querySelectorAll(".nav-item").forEach(button => {
        if (button.dataset.bound) return;

        button.addEventListener("click", () => {
            showPage(button.dataset.page);
        });

        button.dataset.bound = "true";
    });
}

function showPage(pageName) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.remove("active");
    });

    const page = document.getElementById(`page-${pageName}`);

    if (page) page.classList.add("active");

    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.toggle(
            "active",
            button.dataset.page === pageName
        );
    });

    const titles = {
        command: "Command Center",
        junctions: "Junctions",
        monitoring: "Live Monitoring",
        ai: "AI Analysis",
        analytics: "Analytics",
        validation: "Validation"
    };

    setText("page-title", titles[pageName] || "Command Center");

    if (pageName === "monitoring") {
        renderMonitoring(selectedJunctionId);
    }
}


/* =========================================================
   ERROR HANDLING
========================================================= */

function showLoadError(message) {
    const container = document.getElementById("junction-network");

    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>Unable to load SmartFlow data</h3>
                <p>${escapeHTML(message)}</p>
                <p>Open the project using VS Code Live Server.</p>
            </div>
        `;
    }

    const monitor = document.getElementById("monitoring-content");

    if (monitor) {
        monitor.innerHTML = `
            <div class="empty-state">
                <h3>Monitoring data unavailable</h3>
                <p>${escapeHTML(message)}</p>
            </div>
        `;
    }
}