# Industrial Wearable AI: A Low-Cost, Human-Centric Real-Time Monitoring System for Textile Manufacturing

**Full title:** Industrial Wearable AI: A Low-Cost, Human-Centric Real-Time Monitoring System for Worker Activity, Ergonomic Risk, and Fatigue in Textile Manufacturing SMEs

---

**Authors:**  
[Author 1 Name], [Author 2 Name], [Author 3 Name], [Author 4 Name], [Author 5 Name]

**Affiliations:**  
[Department/Institution 1], [Address/City, Country]  
[Department/Institution 2], [Address/City, Country]  
*Correspondence: [email placeholder]*

---

## Abstract

Small and medium textile manufacturing enterprises (SMEs) lack affordable, real-time visibility into worker activity, ergonomic risk, and fatigue. Existing Industry 4.0 solutions are machine-centric, data-heavy, and financially out of reach for many units. We present **Industrial Wearable AI**, an end-to-end system comprising a low-cost wrist-worn inertial measurement unit (IMU), an edge gateway for real-time activity classification, a backend for persistence and live broadcast, and a supervisor dashboard. The wearable streams raw accelerometer and gyroscope data over Bluetooth Low Energy (BLE) to a laptop-based edge that applies a sliding-window feature pipeline and a lightweight classifier (ML or rule-based) to infer activity states (sewing, idle, adjusting, break, error) and risk flags (ergonomic, fatigue). Results are pushed to a REST API and broadcast via WebSocket to a web dashboard, enabling supervisors to see who is working, idle, or at risk in real time. We describe the architecture, implementation, and a proof-of-concept deployment. The system demonstrates that human-centric, real-time shop-floor monitoring is achievable at a fraction of the cost of traditional smart manufacturing solutions, with immediate value for productivity and safety in labour-intensive textile settings.

**Keywords:** Wearable sensors, activity recognition, textile manufacturing, Industry 4.0, human-centric IoT, ergonomic risk, fatigue monitoring, edge computing, real-time dashboard, SMEs.

---

## 1. Introduction

### 1.1 Background and Motivation

The textile manufacturing sector remains one of the most labour-intensive industries worldwide and is a major employer in many emerging economies [1]. Despite advances in automation, a large share of value creation still depends on human operators performing repetitive tasks such as sewing, cutting, and assembly. These workers are exposed to ergonomic risks, fatigue, and variable environmental conditions, yet many small and medium enterprises (SMEs) have no systematic, real-time way to monitor worker state, activity, or safety [2].

Industry 4.0 and smart manufacturing have introduced IoT, AI, and data analytics into factories, but adoption has been uneven. Large firms invest in machine monitoring, predictive maintenance, and digital twins; SMEs often lack the budget, expertise, and infrastructure for such systems [3]. Moreover, most commercial solutions focus on *machines*—sensorising equipment, production lines, and energy consumption—while *human* contribution remains a blind spot: who is active, who is idle, who is at ergonomic or fatigue risk, and why [4]. This gap—*human–machine invisibility*—limits both operational efficiency and worker safety in precisely the settings where improvements would have the highest impact [5].

Wearable technology offers a human-centric alternative. Low-cost inertial and environmental sensors worn on the wrist or body can capture motion and context continuously; when combined with lightweight AI at the edge and a simple backend and dashboard, they can deliver real-time activity and risk insights without heavy infrastructure [6], [7]. The challenge is to design such a system so that it is *affordable*, *deployable in resource-constrained environments*, and *actionable* for supervisors.

### 1.2 Problem Statement

We address the following problem: *How can small and medium textile manufacturing units obtain real-time, actionable visibility into worker activity (e.g., sewing, idle, adjusting) and risk (ergonomic, fatigue) using low-cost wearables and minimal infrastructure?*

Concretely, we target settings where:

- There is little or no real-time data on worker activity or shop-floor conditions.
- Monitoring relies on manual observation, spot checks, or paper-based records.
- Safety and ergonomics are reactive (addressed after incidents) rather than preventive.
- Budget and technical capacity rule out full-scale Industry 4.0 platforms.

### 1.3 Objectives and Contributions

The main objectives of this work are:

1. **To design and implement** an end-to-end system—wearable device, edge gateway, backend, and dashboard—that delivers real-time worker activity and risk information to supervisors.
2. **To keep the solution low-cost and deployable** on a single laptop (no cloud or Raspberry Pi required for the core pipeline) using off-the-shelf hardware (ESP32, IMU) and open-source software.
3. **To demonstrate** that human-centric, real-time monitoring is feasible and useful for productivity and safety in a textile manufacturing context.

Our main contributions are:

- **System architecture** that clearly separates sensing (wearable), inference (edge), persistence and broadcast (backend), and visualisation (dashboard), with BLE and HTTP/WebSocket as the glue.
- **A working prototype** including firmware (ESP32 + IMU, BLE), edge pipeline (buffer, feature extraction, classifier), REST and WebSocket APIs, and a React-based supervisor dashboard with live worker states, alerts, and historical views.
- **Design choices and implementation details** (feature set, classification strategy, live vs. historical data) that can be reused or extended for similar SME settings.

### 1.4 Paper Organisation

The rest of the paper is organised as follows. Section 2 reviews related work on wearables, activity recognition, and industrial IoT. Section 3 formalises the problem and scope. Section 4 presents the proposed system architecture and methodology. Section 5 describes the implementation. Section 6 discusses evaluation and results. Section 7 discusses limitations and implications. Section 8 concludes and outlines future work.

---

## 2. Related Work

### 2.1 IoT and Smart Manufacturing

IoT-based monitoring in manufacturing has been widely studied for machine health, energy use, and production metrics [8], [9]. These systems typically instrument equipment and production lines; they improve efficiency and enable predictive maintenance but are machine-centric and assume substantial connectivity and backend infrastructure. Their cost and complexity limit adoption in SMEs [3].

### 2.2 Wearables in Industrial and Occupational Settings

Wearable sensors have been used in healthcare, sports, and occupational safety [10], [11]. In industrial contexts, studies have explored posture detection [12], fatigue estimation [13], and activity recognition [14] using accelerometers, gyroscopes, and sometimes physiological sensors. Much of this work focuses on *offline* analysis or *single-user* validation; fewer systems are designed for *multi-worker, real-time* dashboards with minimal infrastructure [15].

### 2.3 Activity Recognition from IMU Data

Activity recognition from inertial sensors is a well-established topic [16]. Common approaches include hand-crafted features (statistical, frequency-domain) with classical ML (e.g., SVM, Random Forest) or deep learning (e.g., CNNs, RNNs) on raw or windowed signals [17], [18]. For industrial tasks (e.g., assembly, sewing), domain-specific labels (e.g., sewing, idle, adjusting) and small, targeted datasets are often used [19]. We adopt a similar pipeline—sliding windows, hand-crafted features, and a classifier—but emphasise *edge deployment* and *real-time* streaming to a supervisor dashboard rather than offline accuracy alone.

### 2.4 Gap Addressed by This Work

Existing work leaves a gap: *low-cost, human-centric, real-time monitoring systems that are deployable in SME textile units with minimal infrastructure*. Our system fills this gap by combining (1) a low-cost wearable (ESP32 + IMU), (2) edge-based inference on a laptop, (3) a simple backend and WebSocket broadcast, and (4) a web dashboard for live and historical visibility. We do not require cloud, specialised gateways, or large datasets; we prioritise feasibility and immediate utility for supervisors.

---

## 3. Problem Formulation and Scope

### 3.1 Setting

We consider a textile manufacturing unit (or a simulated shop-floor) where workers perform tasks such as operating sewing machines, adjusting fabric, handling errors, and taking breaks. Each worker may wear a single wrist-worn device that streams motion (and optionally temperature) to a nearby edge gateway (e.g., a laptop) on the same premises.

### 3.2 Activity and Risk Model

We define:

- **Activity states:** *Sewing*, *Idle*, *Adjusting*, *Error*, *Break*. These are mutually exclusive at any instant and summarise the current task from motion and context.
- **Risk flags:** *Ergonomic risk* (e.g., posture or repetitive strain), *Fatigue risk* (e.g., prolonged low activity or inferred fatigue). These are binary and can be derived from rules or simple models over the activity stream.

**[INSERT FIGURE 2 HERE — Activity state machine]**  
*Suggested source:* Generate from `docs/uml/08-state-activity.puml`.  
*Caption:* Figure 2. Worker activity state machine: states (sewing, idle, adjusting, error, break) and transitions from classifier output.

The system’s job is to (1) infer the current activity state from the wearable stream, (2) optionally set risk flags, (3) persist events and sessions, and (4) present live and historical views to supervisors.

### 3.3 Constraints

- **Cost:** Hardware per worker should be in the range of low-cost development boards and IMU modules (order of tens of USD or equivalent).
- **Infrastructure:** No mandatory cloud; edge and backend can run on one laptop; database can be local (e.g., PostgreSQL in Docker or installed locally).
- **Latency:** Supervisor view should update within seconds of a state change.
- **Privacy and ethics:** Data is used for operational and safety insights; we assume appropriate consent and governance in deployment.

---

## 4. Proposed System

### 4.1 High-Level Architecture

The system has four layers (see *Figure 1*):

**[INSERT FIGURE 1 HERE — System architecture / context diagram]**  
*Suggested source:* Generate from `docs/uml/00-context.puml` or `docs/uml/02-component.puml` (PlantUML); export as PNG/SVG.  
*Caption:* Figure 1. System architecture: Wearable (ESP32 + IMU) → BLE → Edge (Python) → HTTP/WebSocket → Backend (FastAPI + PostgreSQL) → WebSocket → Dashboard (React).

1. **Wearable layer:** A wrist-worn device (ESP32 + 6-axis IMU, optionally temperature) that samples motion at ~25 Hz and sends JSON payloads over BLE GATT notify.
2. **Edge layer:** A gateway (laptop) that connects to the wearable via BLE, buffers samples, runs a sliding-window feature extractor and classifier, and sends event batches and sensor snapshots to the backend over HTTP.
3. **Backend layer:** A REST API (FastAPI) and WebSocket server that receives events and sensor data, persists them (PostgreSQL), maintains worker and session state, and broadcasts live state to connected dashboard clients.
4. **Dashboard layer:** A web application (React) that authenticates supervisors, subscribes to the WebSocket for live updates, and displays worker cards, alerts, KPIs, and charts (state distribution, activity timeline, alerts trend); it can also show historical sessions and worker history.

### 4.2 Wearable Layer

The wearable runs firmware that:

- Initialises I2C and the IMU (MPU6050 or MPU9250; we support WHO_AM_I 0x68 and 0x70 for compatibility with common breakout boards).
- Reads accelerometer and gyroscope at a fixed rate (e.g., 25 Hz), and optionally temperature.
- Packs each sample into a JSON object: `worker_id`, `ts`, `ax`, `ay`, `az`, `gx`, `gy`, `gz`, `temp`.
- Exposes a BLE GATT service with a notify characteristic; each sample is sent as a notification.
- If the IMU is not detected (e.g., wiring fault), it sends a periodic status message (`mpu_connected: false`) so the dashboard can show “No MPU connected” rather than stale data.

No inference runs on the device; it is a data source only. Worker ID is configured at compile time (e.g., W01). This keeps the wearable simple, low-power, and easy to replicate.

### 4.3 Edge Layer

The edge gateway (Python) performs the following steps:

1. **Connect:** Scan and connect to the wearable by BLE address (or run in simulator mode if no device is present).
2. **Buffer:** Append incoming samples to a ring buffer (e.g., 3–6 s at 25 Hz).
3. **Window:** Extract overlapping windows (e.g., 3 s window, 0.5 overlap); each window is a list of samples.
4. **Filter:** Apply a low-pass filter (exponential moving average) per axis to reduce noise.
5. **Features:** For each window, compute a 30-dimensional feature vector: for each of the six axes (ax, ay, az, gx, gy, gz), compute mean, standard deviation, min, max, and zero-crossing rate. This yields 6 × 5 = 30 features, consistent with common IMU-based activity recognition pipelines.
6. **Classify:** Run a classifier on the feature vector. We support (a) a pre-trained scikit-learn model (e.g., Random Forest) loaded from disk, or (b) a rule-based fallback that uses the sum and max of per-axis standard deviations to map low variance → idle, medium → adjusting, high → sewing. The output is one of: sewing, idle, adjusting, error, break.
7. **Risk:** Set risk flags by simple rules (e.g., fatigue risk when state is idle for extended periods; ergonomic risk can be extended from posture features in future work).
8. **Send:** Batch events (ts, label, risk_ergo, risk_fatigue) and POST to `POST /api/events` at the backend; periodically send sensor snapshots (temp, acceleration magnitude) to `POST /api/live/sensor` for the dashboard’s live sensor strip.

The edge thus turns a raw stream into a sequence of *activity events* and *sensor snapshots* that the backend can store and broadcast.

**[INSERT FIGURE 3 HERE — Edge pipeline activity diagram]**  
*Suggested source:* Generate from `docs/uml/07-activity-edge-pipeline.puml`.  
*Caption:* Figure 3. Edge pipeline: receive BLE sample → buffer → window → filter → extract features → classify → batch events → POST to backend; device-status and sensor snapshot.

### 4.4 Backend Layer

The backend provides:

- **Auth:** JWT-based login and registration; protected routes for dashboard.
- **Events API:** `POST /api/events` accepts a batch of events per worker; it resolves or creates the worker and the current session, inserts rows into an `activity_events` table, and updates session aggregates (e.g., active_pct, idle_pct). After each batch, it broadcasts the latest worker state (worker_id, name, current_state, risk_ergo, risk_fatigue, updated_at) to all WebSocket clients.
- **Live APIs:** `POST /api/live/sensor` and `POST /api/live/device-status` receive sensor snapshots and MPU connection status; the backend broadcasts these to the dashboard so it can show temperature, movement, and “No MPU connected” when relevant.
- **Workers and history:** `GET /api/workers` returns the list of workers; `GET /api/workers/{worker_name}/history` returns session history (started_at, ended_at, active_pct, idle_pct, alert_count, etc.) for that worker.
- **Sessions:** `GET /api/sessions` and `GET /api/sessions/{session_id}/summary` support the “Shift Summary” view.
- **Activity timeline:** `GET /api/activity/timeline?from_ts=&to_ts=&bucket_minutes=` returns bucketed activity counts for historical charts.

The WebSocket channel is a single broadcast channel; all connected dashboards receive the same live updates. This keeps the design simple and avoids per-user state on the server.

### 4.5 Dashboard Layer

The dashboard is a single-page application (React + TypeScript + Vite) with:

- **Login** and optional change-password flow.
- **Live Overview:** The main view. It shows KPIs (Live, Working, Idle, At Risk, Sample), an alerts panel (workers with risk_ergo or risk_fatigue), a “Live now” section (worker cards for workers with an active wearable feed), a “Sample workers” section (demo workers with historical data and expandable “View history”), and a charts section: state distribution donut, activity timeline (with selectable time range: last 10 min live, or 1 h / 6 h / 24 h from the activity timeline API), and alerts trend. A live sensor strip shows temperature and movement magnitude per worker when available.
- **Shift Summary:** List of sessions and session summaries (active_pct, idle_pct, etc.).

The dashboard merges data from the REST API (worker list, history, activity timeline) with WebSocket updates (live state, sensor, device status) so that “live” and “sample” workers are clearly separated and supervisors see up-to-date activity and alerts.

**[INSERT FIGURE 4 HERE — Use case diagram]**  
*Suggested source:* Generate from `docs/uml/01-use-case.puml`.  
*Caption:* Figure 4. Use cases: Worker (wear device, stream data), System (classify, post events), Supervisor (login, view live overview, alerts, history, charts).

---

## 5. Implementation

### 5.1 Hardware and Firmware

- **MCU:** ESP32 (e.g., ESP32-WROOM-32 or DevKitC).
- **IMU:** MPU6050 (I2C 0x68) or MPU9250/clone (WHO_AM_I 0x70); we patched the Adafruit MPU6050 library to accept 0x70 so that common “MPU6050” breakouts that ship with MPU9250 work without code fork.
- **Wiring:** SDA → GPIO 21, SCL → GPIO 22; VCC 3.3 V, GND common. Optional temperature sensor on GPIO 4.
- **BLE:** NimBLE stack; custom GATT service/characteristic UUIDs; notify-only for streaming JSON.
- **Firmware behaviour:** Delay after I2C init (150 ms) and up to 3 retries for IMU begin to improve reliability across different boards and power-up sequences.

### 5.2 Edge Pipeline

- **Language and libraries:** Python 3.10+; bleak (BLE), numpy, pandas, scikit-learn, joblib, aiohttp.
- **Buffer:** Configurable max length (e.g., 6 s at 25 Hz); windows of 3 s with 0.5 overlap; step size in samples so we do not run the classifier on every new sample but at a fixed stride.
- **Feature extraction:** Exactly 30 features per window (mean, std, min, max, zero-crossing rate per axis), implemented in a dedicated module so it can be shared with offline training scripts.
- **Classifier:** If a joblib model exists at the configured path, it is loaded and used; otherwise the rule-based classifier is used. The rule-based classifier uses thresholds on the sum and maximum of the six standard-deviation features to classify into idle, adjusting, or sewing; thresholds were tuned so that typical sewing motion is classified as working rather than idle.

### 5.3 Backend and Database

- **Framework:** FastAPI; async SQLAlchemy with asyncpg for PostgreSQL.
- **Models:** User (auth), Worker, Device, Session, SessionAggregate, ActivityEvent (with label enum: sewing, idle, adjusting, error, break). Migrations via Alembic.
- **WebSocket:** In-memory hub that holds a set of connected clients and broadcasts JSON messages (worker state, sensor, device_status) to all. No persistence of WebSocket messages; persistence is event-based via the events API.

### 5.4 Dashboard

- **Stack:** React 19, TypeScript, Vite, Recharts (charts), Framer Motion (animations), Axios (HTTP), JWT in localStorage.
- **State:** WebSocket hook maintains the latest worker map, sensor-by-worker map, MPU-connected-by-worker map, and a rolling buffer of activity events for the last 10 minutes (for the live activity timeline). Worker list from the API is merged with WebSocket state to distinguish “live” (has recent WebSocket update) vs “sample” (API-only, for demo/history).
- **Charts:** State donut (current live workers by state); activity timeline (stacked area by state, time range selector for 10 min / 1 h / 6 h / 24 h, with 1 h+ data from the activity timeline API); alerts trend (at-risk counts over last 10 min).

### 5.5 Deployment

The system is designed for “laptop-only” deployment: PostgreSQL runs in Docker (or as a local install if Docker is unavailable); backend, edge, and dashboard dev server run on the same machine. The wearable connects via BLE to the laptop running the edge. No cloud or Raspberry Pi is required for the core pipeline. This reduces cost and complexity for SME pilots.

**[INSERT FIGURE 5 HERE — Deployment diagram]**  
*Suggested source:* Generate from `docs/uml/03-deployment.puml`.  
*Caption:* Figure 5. Deployment: Wearable device (ESP32), Laptop (Edge + Backend + Dashboard), PostgreSQL; BLE and HTTP/WebSocket connections.

**[INSERT FIGURE 6 HERE — Data flow sequence diagram]**  
*Suggested source:* Generate from `docs/uml/04-sequence-data-flow.puml`.  
*Caption:* Figure 6. Sequence: Wearable → Edge (BLE samples) → buffer → classify → POST events → Backend → DB → WebSocket broadcast → Dashboard.

**[INSERT FIGURE 7 HERE — Domain model / class diagram]**  
*Suggested source:* Generate from `docs/uml/06-class-domain.puml`.  
*Caption:* Figure 7. Backend domain model: User, Worker, Device, Session, ActivityEvent, SessionAggregate, ActivityLabel.

---

## 6. Evaluation and Results

### 6.1 Evaluation Setup

We evaluated the system as a proof-of-concept:

- **Hardware:** ESP32 DevKitC with MPU6050/MPU9250 breakout; wiring as per design.
- **Software:** All four layers (firmware, edge, backend, dashboard) running on a single laptop (Windows); PostgreSQL via Docker or local install.
- **Scenarios:** (1) Wearable streaming to edge with real IMU data; (2) Edge in simulator mode (no BLE device) generating synthetic samples and events; (3) Dashboard with both “live” workers (from WebSocket) and “sample” workers (from seed data) to demonstrate live vs historical views.

### 6.2 Functional Results

- **End-to-end pipeline:** Raw IMU samples flow from wearable to edge; the edge produces activity labels and risk flags and posts events to the backend; the backend persists events and broadcasts state; the dashboard shows updating worker cards, KPIs, and alerts within seconds.
- **Live vs historical:** The dashboard correctly separates workers with an active BLE feed (“Live now”) from workers that exist only in the database (“Sample workers” with expandable session history). Time-range selection on the activity timeline (10 min live, 1 h / 6 h / 24 h historical) works with the activity timeline API.
- **No-IMU handling:** When the wearable reports `mpu_connected: false`, the edge posts device status and does not send fake IMU data; the dashboard shows a “No MPU connected” banner for that worker. This avoids misleading “live” data when the sensor is absent or faulty.
- **Classifier behaviour:** With the rule-based classifier, typical hand/wrist motion (e.g., sewing-like movement) is classified as sewing or adjusting rather than idle after threshold tuning. With an optional trained model (joblib), the edge uses the model’s predictions; the pipeline supports both.

**[INSERT TABLE I HERE — Results summary / key metrics]**  
*Suggested content:* Rows for pipeline latency (e.g. BLE→dashboard), event throughput, classifier mode (rule-based / trained), test scenario (single wearable, simulator). Columns: Metric, Value, Notes. Leave blank or fill when quantitative results are available.

| *Metric* | *Value* | *Notes* |
|----------|---------|---------|
| (placeholder) | (placeholder) | (placeholder) |

### 6.3 Qualitative Findings

- **Usability:** Supervisors can see at a glance who is working, idle, or at risk; the alerts panel and KPIs provide a quick summary. The separation of “Live now” and “Sample workers” avoids confusion when demo data is present.

**[INSERT FIGURE 8 HERE — Dashboard screenshot]**  
*Suggested content:* Screenshot of the supervisor dashboard showing live worker cards, KPIs, alerts panel, and activity timeline. No UML source; capture from running app and place in `figures/` (e.g. `figures/dashboard-screenshot.png`).  
*Caption:* Figure 8. Supervisor dashboard: live workers, KPIs, alerts, and activity timeline (live and historical).
- **Deployability:** Running the stack on one laptop with optional local PostgreSQL (when Docker is unavailable) lowers the barrier for pilot deployment in resource-constrained environments.
- **Extensibility:** The backend’s REST and WebSocket design and the dashboard’s hooks allow adding more workers, more sensors, or more charts without changing the core flow.

### 6.4 Limitations of the Evaluation

We did not conduct a formal user study or a long-term field trial. Accuracy of the activity classifier was not evaluated against a labelled test set in this paper; such evaluation is planned as future work. The results above are intended to demonstrate feasibility and end-to-end behaviour rather than to claim statistically validated accuracy or impact.

---

## 7. Discussion

### 7.1 Limitations

- **Single role:** The activity vocabulary (sewing, idle, adjusting, error, break) is tailored to one role (e.g., sewing operator). Extending to other roles (cutter, packer) would require new labels and possibly new sensors or features.
- **Classifier:** The rule-based classifier is heuristic; a trained model on labelled data would likely improve accuracy. We have not reported precision/recall or confusion matrices here.
- **Risk models:** Ergonomic and fatigue risks are currently simple rules (e.g., fatigue when idle). Richer models (e.g., posture from orientation, heart rate if available) would strengthen the risk signals.
- **Scale:** The prototype has been tested with one wearable and one edge instance. Scaling to many workers would require multiple BLE connections or a different radio strategy (e.g., multiple edge gateways or a different protocol).
- **Privacy and consent:** Deployment in a real factory must address worker consent, data retention, and use policies; we have not implemented access control per worker or anonymisation.

### 7.2 Practical Implications

- **For SMEs:** The system shows that human-centric, real-time monitoring need not depend on expensive cloud or industrial IoT platforms. A laptop, a low-cost wearable, and open-source software can deliver live activity and risk visibility.
- **For researchers:** The architecture (wearable → edge → backend → dashboard) and the open implementation (feature pipeline, classifier interface, API design) can serve as a base for experiments with different sensors, models, or dashboard designs.
- **For education:** The project is suitable as a teaching or capstone prototype for courses in IoT, embedded systems, or human-centred computing.

### 7.3 Comparison with Related Work

Unlike machine-centric IoT monitoring [8], [9], our system focuses on *workers* and their activity and risk. Unlike many wearable studies that analyse data offline [12], [13], we stream inference results to a live dashboard. Unlike heavy AI platforms that assume large datasets and cloud [3], we keep the pipeline lightweight and runnable on a single laptop with optional ML. Our contribution is the *integration* of these elements into a working, deployable prototype for SME textile settings.

---

## 8. Conclusion and Future Work

### 8.1 Summary

We presented **Industrial Wearable AI**, a low-cost, human-centric system for real-time monitoring of worker activity and risk in textile manufacturing. The system consists of (1) a wrist-worn wearable (ESP32 + IMU) streaming raw motion over BLE, (2) an edge gateway that buffers, filters, extracts features, and classifies activity (and optionally risk), (3) a backend that persists events and broadcasts live state over WebSocket, and (4) a supervisor dashboard that displays live workers, alerts, KPIs, and historical charts. We described the architecture, implementation, and a proof-of-concept evaluation, and we argued that such a system is feasible and useful for SMEs that cannot afford full Industry 4.0 solutions but need visibility into human labour and safety.

### 8.2 Future Work

- **Labelled dataset and classifier evaluation:** Collect labelled IMU data for sewing, idle, adjusting, etc., and report precision, recall, and confusion matrices; compare rule-based vs trained models.
- **Richer risk models:** Integrate posture (e.g., from quaternions or orientation) and optional physiological sensors for ergonomic and fatigue risk.
- **Multi-worker and multi-site:** Design for many wearables (e.g., multiple BLE connections or gateways) and optional cloud aggregation for multi-site dashboards.
- **Field pilot:** Deploy in one or more textile units for a sustained period and measure impact on supervisor decisions, incident rates, or productivity metrics.
- **Privacy and ethics:** Formalise consent, retention, and access policies; consider anonymisation or aggregation for analytics.

---

## Acknowledgments

(To be added by the authors: funding bodies, institutions, and individuals who contributed to the project.)

---

## References

[1] International Labour Organization, “Employment in the textile and clothing sector,” in *World Employment and Social Outlook*, 2020.

[2] B. Neumann and M. Montag, “Human factors in smart manufacturing: A systematic literature review,” in *Proc. Int. Conf. Applied Human Factors and Ergonomics*, 2020, pp. 3–12.

[3] M. Brettel, N. Friederichsen, M. Keller, and M. Rosenberg, “How virtualization, decentralization and network building change the manufacturing landscape: An Industry 4.0 perspective,” *Int. J. Information and Communication Engineering*, vol. 8, no. 1, pp. 37–44, 2014.

[4] A. Longo, L. Zappatore, M. Bochicchio, and M. A. Wimmer, “Towards a collaborative and integrated approach to sustainable manufacturing,” *Computers in Industry*, vol. 96, pp. 45–55, 2018.

[5] K. Kadam, S. Kadam, A. Koyande, M. Choudhari, and R. K. Ajetrao, “AI-driven wearable tool for real-time data collection in textile manufacturing units,” Patent/Concept Document, 2025.

[6] S. Bhattacharya and S. K. Tripathi, “Wearable sensors for industrial applications: A survey,” *IEEE Sensors Journal*, vol. 20, no. 18, pp. 10829–10840, 2020.

[7] J. A. Ward, P. Lukowicz, and H. W. Gellersen, “Performance metrics for activity recognition,” *ACM Trans. Intelligent Systems and Technology*, vol. 2, no. 1, pp. 1–23, 2011.

[8] P. K. Singh, R. Singh, and S. K. Sharma, “IoT in manufacturing: A review,” in *Proc. Int. Conf. Computing, Communication and Automation*, 2017, pp. 1–6.

[9] Z. Zhou, Y. Xie, and X. Chen, “Fundamentals of digital twin and its application in smart manufacturing,” *Journal of Manufacturing Systems*, vol. 58, pp. 1–15, 2021.

[10] S. Majumder, E. A. Deen, and M. J. Deen, “Wearable sensors for remote health monitoring,” *Sensors*, vol. 17, no. 1, p. 130, 2017.

[11] A. Bulling, U. Blanke, and B. Schiele, “A tutorial on human activity recognition using body-worn inertial sensors,” *ACM Computing Surveys*, vol. 46, no. 3, pp. 1–33, 2014.

[12] D. Antón, G. Pardo, and L. G. Begoña, “A review of wearable sensors for posture and movement monitoring,” *Sensors*, vol. 20, no. 18, p. 5127, 2020.

[13] S. J. Kim, H. J. Cho, and Y. G. Kim, “Fatigue detection using wearable sensors in industrial environments: A survey,” *Applied Sciences*, vol. 10, no. 15, p. 5234, 2020.

[14] O. D. Lara and M. A. Labrador, “A survey on human activity recognition using wearable sensors,” *IEEE Communications Surveys & Tutorials*, vol. 15, no. 3, pp. 1192–1209, 2013.

[15] F. J. O. Morales and D. Roggen, “Deep learning for multimodal wearable and ambient sensors: A survey,” *IET Smart Cities*, vol. 3, no. 1, pp. 1–18, 2021.

[16] N. Y. Hammerla, S. Halloran, and T. Plötz, “Deep, convolutional, and recurrent models for human activity recognition using wearables,” in *Proc. IJCAI*, 2016, pp. 1533–1540.

[17] A. Reiss and D. Stricker, “Introducing a new benchmarked dataset for activity recognition,” in *Proc. IEEE Int. Symp. Wearable Computers*, 2012, pp. 108–109.

[18] J. R. Kwapisz, G. M. Weiss, and S. A. Moore, “Activity recognition using cell phone accelerometers,” *ACM SIGKDD Explorations*, vol. 12, no. 2, pp. 74–82, 2011.

[19] A. Mannini and A. M. Sabatini, “Machine learning methods for classifying human physical activity from on-body accelerometers,” *Sensors*, vol. 10, no. 2, pp. 1154–1175, 2010.

---

## Appendix A — System Parameters (Summary)

| Parameter | Value or range |
|-----------|----------------|
| IMU sample rate | 25 Hz |
| Window length | 3 s |
| Window overlap | 0.5 |
| Feature dimension | 30 (6 axes × 5 features) |
| Activity labels | sewing, idle, adjusting, error, break |
| BLE GATT | Notify; JSON per sample |
| Event batch size | 5 (configurable); flush interval ~2.5 s |
| Sensor snapshot interval | ~2.5 s |

---

## Appendix B — List of Key Software Artefacts

- **Firmware:** `firmware/IndustrialWearableAI/IndustrialWearableAI.ino` (Arduino/ESP32).
- **Edge:** `edge/src/main.py`, `ble_client.py`, `buffer.py`, `pipeline.py`, `feature_extractor.py`, `classifier.py`, `api_client.py`.
- **Backend:** `backend/app/main.py`, `api/` (auth, events, live, workers, sessions, activity), `models/`, `services/websocket_hub.py`.
- **Dashboard:** `dashboard/src/` (pages, components, hooks, api).
- **Documentation:** `docs/PROJECT_DOCUMENTATION.md`, `docs/RUN_COMMANDS.md`, `docs/HARDWARE_CONNECTIONS.md`.

---

*Document version: 1.0. For the full implementation and run instructions, see the project repository and docs/PROJECT_DOCUMENTATION.md.*
