async function loadJSON(file) {
    const response = await fetch(`../${file}`);

    if (!response.ok) {
        throw new Error(`Could not load ${file}`);
    }

    return await response.json();
}


async function loadDashboard() {

    try {

        const analysis = await loadJSON(
            "results/analysis_results.json"
        );

        const validation = await loadJSON(
            "results/validation_results.json"
        );

        const feedback = await loadJSON(
            "results/user_feedback.json"
        );


        // ----------------------------------------
        // CASE STUDY
        // ----------------------------------------

        document.getElementById("caseStudy").textContent =
            analysis.case_study;


        // ----------------------------------------
        // TRAFFIC METRICS
        // ----------------------------------------

        document.getElementById("vehicles").textContent =
            analysis.traffic_analysis.vehicles_detected;

        document.getElementById("queue").textContent =
            analysis.traffic_analysis.queue_length;

        document.getElementById("density").textContent =
            analysis.traffic_analysis.traffic_density;

        document.getElementById("green").textContent =
            `${analysis.adaptive_signal.recommended_green_time} sec`;


        // ----------------------------------------
        // SIGNAL DECISION
        // ----------------------------------------

        document.getElementById("signalDecision").textContent =
            analysis.adaptive_signal.signal_decision;

        document.getElementById("signalReason").textContent =
            `${analysis.traffic_analysis.traffic_density} traffic with ` +
            `${analysis.traffic_analysis.queue_length} queued vehicles.`;


        document.getElementById("greenLarge").textContent =
            `${analysis.adaptive_signal.recommended_green_time} sec`;


        // ----------------------------------------
        // VALIDATION
        // ----------------------------------------

        document.getElementById("throughput").textContent =
            validation.performance_metrics.estimated_throughput;

        document.getElementById("queueReduction").textContent =
            `${validation.performance_metrics.queue_reduction_percentage}%`;

        document.getElementById("greenImprovement").textContent =
            `${validation.signal_comparison.green_time_improvement_percentage}%`;

        document.getElementById("fixedGreen").textContent =
            `${validation.signal_comparison.fixed_green_time_seconds} sec`;


        // ----------------------------------------
        // USER FEEDBACK
        // ----------------------------------------

        document.getElementById("usefulness").textContent =
            `${feedback.summary.average_usefulness}/5`;

        document.getElementById("understanding").textContent =
            `${feedback.summary.average_understanding}/5`;

        document.getElementById("confidence").textContent =
            `${feedback.summary.average_confidence}/5`;


    } catch (error) {

        console.error(error);

        alert(
            "Dashboard could not load the AI results. " +
            "Make sure the JSON files exist in the results folder."
        );

    }
}


loadDashboard();