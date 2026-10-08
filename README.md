# SmartFlow
## AI-Based Adaptive Traffic Signal Management

SmartFlow is an AI-powered traffic management prototype that analyzes real traffic video and recommends adaptive traffic signal timing based on detected vehicle density and estimated queue length.

### Case Study

**Location:** Oppanakara Street, Coimbatore  
**Observation Time:** 4:30 PM – 6:00 PM

The system uses real traffic footage collected from the selected case-study location.

---

## Problem Statement

Traditional traffic signals commonly use fixed timing, which may not respond effectively to changing traffic conditions.

During peak hours, one direction may have a large queue while another direction has comparatively less traffic.

SmartFlow aims to analyze traffic conditions using computer vision and recommend a suitable green-light duration.

---

## Proposed Solution

SmartFlow follows an AI-based traffic analysis pipeline:

```text
Traffic Video
      ↓
YOLOv8 Vehicle Detection
      ↓
ByteTrack Object Tracking
      ↓
Vehicle Counting
      ↓
Queue Estimation
      ↓
Traffic Density Classification
      ↓
Adaptive Green-Time Calculation
      ↓
Signal Decision
      ↓
Validation Dashboard