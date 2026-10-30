SmartFlow — AI-Based Adaptive Traffic Signal Management

SmartFlow is an academic traffic-management prototype that analyzes recorded traffic video, detects and tracks vehicles, estimates queue length and traffic density, and recommends an adaptive green-signal duration.

**Case study:** Oppanakara Street, Coimbatore, Tamil Nadu, India.

**Project status:** Prototype. The system recommends signal timings but does not control physical traffic signals. Throughput and queue-reduction figures are prototype estimates, not real-world measured improvements.

---

## 1. Problem Statement

Fixed-time traffic signals may not respond to changing traffic conditions. SmartFlow explores how computer vision can analyze recorded traffic and recommend signal timings based on observed traffic conditions.

2. Project Objectives

- Detect cars, motorcycles, buses, and trucks in traffic video.
- Track vehicles across video frames to support unique-vehicle counting.
- Estimate the number of queued vehicles and classify traffic density.
- Recommend a green-signal duration.
- Display available analysis information through a browser dashboard.
- Compare prototype estimates with a fixed-time baseline.

Dashboard and other interface behavior is limited to what is present in the checked-out project files; this README does not claim a live monitoring service.

## 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming language | Python | Video processing and traffic analysis |
| Object detection | YOLOv8 | Vehicle detection |
| Multi-object tracking | ByteTrack | Tracking detections across frames |
| Video processing | OpenCV | Reading and processing video frames |
| Dashboard | HTML, CSS, JavaScript | Browser-based display of project data |
| Structured data | JSON | Junction configuration and analysis results |
| Testing | Python `unittest` | Automated unit tests |

Dependency versions are listed in `requirements.txt`.

## 4. System Architecture

The project processes a local recorded video through vehicle detection and tracking, derives traffic estimates, recommends signal timing, and saves results as JSON. The browser dashboard reads available static JSON resources.

```text
Recorded traffic video
        ↓
YOLOv8 detection → ByteTrack tracking → vehicle classification/counting
        ↓
Queue estimate → traffic-density analysis → green-time recommendation
        ↓
JSON analysis and validation results
        ↓
Browser dashboard (static files served locally)
```

### Main project directories

```text
smartflow-ai-traffic-management/
├── ai/
│   ├── vehicle_detection.py
│   └── traffic_logic.py
├── dashboard/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── data/
│   ├── junctions.json
│   └── traffic_video.mp4       # Local input; may be gitignored
├── results/
│   ├── analysis_results.json
│   ├── validation_results.json
│   └── user_feedback.json
├── tests/
│   ├── test_traffic_logic.py
│   └── test_validation_metrics.py
├── validation/
│   ├── validation_metrics.py
│   └── user_feedback.py
├── requirements.txt
└── README.md
```

The traffic video is a local input and may not be included in the repository. Provide the video at the path configured by the analysis module.

## 5. AI Processing Methodology

### 5.1 Vehicle detection

YOLOv8 identifies supported vehicle classes in processed frames. The pipeline uses COCO class IDs 2 (car), 3 (motorcycle), 5 (bus), and 7 (truck). Detection quality can vary with camera angle, lighting, image quality, occlusion, and visibility.

### 5.2 Vehicle tracking and counting

ByteTrack associates detections across successive frames to support unique-vehicle counting. Missed detections, tracking errors, and vehicles entering or leaving the camera's field of view can affect counts.

### 5.3 Queue estimation

The prototype estimates queue length using a region near the bottom of the frame. The current heuristic treats vehicle centers below approximately 60% of frame height as potential queued vehicles. It is not a physically calibrated queue measurement in metres and may need adjustment for other camera views.

### 5.4 Traffic density

Traffic density is classified using the rules implemented in the project. The category informs the signal-timing heuristic and is a prototype estimate, not an engineering measurement.

### 5.5 Adaptive green-time recommendation

The rule-based prototype uses a minimum green duration of 20 seconds, an estimated queue contribution, a traffic-density adjustment, and a maximum of 60 seconds. It is not a trained reinforcement-learning model, fuzzy controller, or full implementation of Webster's method. The recommendation is software output only; it does not actuate a signal.

## 6. Running SmartFlow

### Prerequisites

- Python compatible with the dependencies in `requirements.txt`.
- A local traffic video at the path configured by the script, if the video is not included.
- A modern web browser to view the static dashboard, if desired.

### Install dependencies

From the project root:

```bash
python -m venv .venv
```

On Windows, activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Run vehicle analysis

From the project root, use the module command:

```bash
python -m ai.vehicle_detection
```

The module is intended to be run through this package entry point. Ensure the input video path configured by the module is valid. On successful processing, it writes or updates `results/analysis_results.json`.

### View the dashboard

Serve the `dashboard` directory using a local HTTP server or an editor extension such as Live Server, then open the served `index.html` in a browser. The browser loads configuration and results as static JSON files. Opening the HTML directly with a `file://` URL may prevent those fetches from working.

### Run validation

From the project root:

```bash
python -m validation.validation_metrics
```

The validation module reads `results/analysis_results.json` and writes `results/validation_results.json` when its required input is available.

## 7. Unit Testing Strategy and Verified Results

The automated tests use Python's built-in `unittest` framework. The verified suite contains **32 passing tests**: 16 traffic-logic tests and 16 validation-metrics tests.

Run the validation-metrics tests:

```bash
python -m unittest tests.test_validation_metrics -v
```

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

The reported 32 passing tests cover the implemented traffic-logic and validation-metrics modules. They do not establish that every video-processing, dashboard, deployment, or hardware scenario is automated or verified.

## 8. Error Boundaries and Failure Handling

### 8.1 Python processing and validation

The vehicle-analysis module depends on a valid local video and its configured model/runtime dependencies. Validation requires a readable analysis JSON object containing the fields expected by `validation_metrics.py`. The validation module checks required values and reports invalid or missing inputs rather than treating them as valid metrics. Use the actual module messages and code as the authority for specific failure behavior.

### 8.2 Dashboard data loading

The dashboard fetches static JSON resources through a local web server. A missing file, invalid JSON, or missing expected fields can prevent the associated data from loading or displaying correctly. These are local resource loads, not calls to a custom backend API.

### 8.3 Verification boundaries

The 32 passing unit tests verify traffic logic and validation metrics. Do not infer from those results that video hardware, a production dashboard, REST services, or physical signal control have been tested.

## 9. Data Files and JSON Resources

SmartFlow uses JSON files for configuration, analysis results, validation results, and feedback. It does not use a database.

### 9.1 Junction configuration

**File:** `data/junctions.json`

This is a static configuration resource for junction information. Refer to the file itself for the exact property names and values. The case study is Oppanakara Street, Coimbatore.

### 9.2 Analysis results

**File:** `results/analysis_results.json`

This file is produced by vehicle analysis and supplies data consumed by validation and, where configured, the dashboard. Refer to the current JSON file and analysis code for exact keys and values.

### 9.3 Validation results

**File:** `results/validation_results.json`

The validation module records the comparison against the configured fixed-time baseline and estimated metrics. Refer to the module and generated file for the exact schema.

### 9.4 User feedback

**File:** `results/user_feedback.json`

This is a JSON resource associated with the feedback module. Consult the implementation for the fields and workflow currently supported.

### 9.5 Database status

**Database: Not implemented.** The current project does not use SQL tables, an ORM, or a database server. JSON files are its structured data resources.

## 10. API Documentation

**Custom REST API: Not implemented.** SmartFlow runs Python modules and can display project data in a static browser dashboard. It does not expose custom application endpoints such as `/api/vehicles` or `/api/signals`.

When served locally, the browser may request JSON paths such as `data/junctions.json` and `results/analysis_results.json`. Those are static file resources served by the local web server, not custom REST API endpoints or a backend API contract.

## 11. Validation Methodology and Limitations

The validation module compares an adaptive recommendation with a fixed 30-second baseline and calculates prototype performance indicators. A previously recorded example reported 63 detected vehicles, an initial estimated queue of 18, adaptive green time of 39 seconds, estimated throughput of 25 vehicles, and estimated queue reduction of 4 vehicles (22.22%). These are example prototype outputs, not independent field measurements.

Key limitations:

- The fixed-time baseline is a configured comparison value.
- Estimated throughput is not a field-measured vehicle discharge rate.
- Estimated queue reduction is not a measured before-and-after outcome.
- The input is recorded video, not a live CCTV feed.
- Queue estimation uses a simplified image-based heuristic.
- Dashboard illustrations or placeholders should not be treated as direction-specific detector results unless produced by the analysis pipeline.
- The system does not control physical traffic signals.

Real-world effectiveness would require calibrated measurements, appropriate baselines, repeated observations, and controlled field evaluation.

## 12. Code Quality and Maintenance

- Keep documentation aligned with the code and generated data.
- Validate inputs before calculations.
- Keep configuration separate from analysis output.
- Explain non-obvious algorithms and boundary conditions.
- Describe estimates as estimates unless measured evidence supports stronger claims.
- Run the relevant `unittest` commands after changes to tested logic.

## 13. Future Enhancements

Potential future work, not claims of current implementation, includes:

- Broader automated tests and continuous integration.
- More robust queue estimation and camera calibration.
- Direction-specific vehicle detection and counting.
- Field validation using measured traffic data.
- Historical traffic storage in a database.
- A documented REST API.
- Multi-junction coordination.
- Integration with an authorized signal controller after safety and regulatory evaluation.

## 14. Project Safety Notice

SmartFlow is an academic decision-support prototype. Its recommendations are not certified traffic-control commands. Do not connect it directly to public-road traffic signals without appropriate engineering validation, safety mechanisms, authorization, and regulatory approval.

---

**Project:** SmartFlow — AI-Based Adaptive Traffic Signal Management  
**Case study:** Oppanakara Street, Coimbatore  
**Purpose:** Academic prototype and evaluation
