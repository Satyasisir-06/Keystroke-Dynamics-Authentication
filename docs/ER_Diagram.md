# ER Diagram — KeyAuth Database
## Keystroke Dynamics Authentication System

This document contains the Entity-Relationship diagram for the KeyAuth database.

---

## ER Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o| KEYSTROKE_PROFILES : "has one"
    USERS ||--o{ ENROLLMENT_SAMPLES : "has many"
    USERS ||--o{ AUTH_LOGS : "has many"

    USERS {
        varchar(36) id PK "UUID primary key"
        varchar(50) username UK "Unique login identifier"
        varchar(100) name "Display name"
        varchar(20) device_type "web / mobile / tablet"
        boolean is_enrolled "Enrollment status"
        datetime created_at "Registration time"
        datetime updated_at "Last modification"
    }

    KEYSTROKE_PROFILES {
        varchar(36) id PK "UUID primary key"
        varchar(36) user_id FK "References users.id"
        text feature_vector "JSON averaged features (36 dims)"
        text model_data "Serialized Isolation Forest model"
        float threshold "Confidence threshold (default 0.85)"
        boolean is_trained "ML model trained flag"
        datetime created_at "Profile creation time"
        datetime updated_at "Last model update"
    }

    ENROLLMENT_SAMPLES {
        varchar(36) id PK "UUID primary key"
        varchar(36) user_id FK "References users.id"
        integer sample_number "1, 2, 3, 4, 5..."
        text raw_keystrokes "JSON original keystroke events"
        text features "JSON extracted feature vector"
        varchar(20) device_type "Capture device"
        datetime created_at "Sample capture time"
    }

    AUTH_LOGS {
        varchar(36) id PK "UUID primary key"
        varchar(36) user_id FK "References users.id"
        varchar(20) result "accepted / rejected"
        float confidence_score "0.0 to 1.0"
        float threshold_used "Threshold at auth time"
        varchar(30) method_used "statistical / isolation_forest"
        varchar(45) ip_address "Client IP address"
        varchar(20) device_type "Auth device"
        datetime timestamp "Attempt timestamp"
    }
```

---

## Relationships

| Relationship | Cardinality | Description |
|-------------|-------------|-------------|
| Users → Keystroke Profiles | 1 : 0..1 | Each user has at most one keystroke profile |
| Users → Enrollment Samples | 1 : 0..N | Each user can have multiple enrollment samples |
| Users → Auth Logs | 1 : 0..N | Each user can have multiple authentication attempts |

---

## Feature Vector Structure (36 Dimensions)

| Index | Feature | Category |
|-------|---------|----------|
| 0-6 | Dwell time (mean, std, min, max, median, Q25, Q75) | Key hold duration |
| 7-13 | Flight time (mean, std, min, max, median, Q25, Q75) | Inter-key interval |
| 14-20 | Digraph latency (mean, std, min, max, median, Q25, Q75) | Key-pair timing |
| 21 | Typing speed (chars/sec) | Overall speed |
| 22 | Total typing duration (ms) | Session length |
| 23 | Pause ratio | Pauses / total time |
| 24 | Key transition entropy | Timing consistency |
| 25-31 | Pressure stats (mean, std, min, max, median, Q25, Q75) | Touch pressure (mobile) |
| 32-35 | Touch size stats (mean, std, Q25, Q75) | Touch area (mobile) |
