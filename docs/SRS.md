# Software Requirements Specification (SRS)
## Keystroke Dynamics Based Cross-Platform Passwordless Authentication System

**Version:** 1.0  
**Date:** February 21, 2026  
**Project Name:** KeyAuth

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for KeyAuth — a passwordless authentication system that verifies user identity through their unique typing rhythm (keystroke dynamics). The system eliminates the need for traditional passwords by using behavioral biometrics.

### 1.2 Scope
KeyAuth provides:
- User registration with keystroke enrollment
- Authentication via typing pattern matching
- Real-time biometric feature extraction (36 features)
- Machine learning–based identity verification
- Cross-platform web interface
- REST API backend with JWT authentication

### 1.3 Definitions & Abbreviations

| Term | Definition |
|------|-----------|
| **Keystroke Dynamics** | Behavioral biometric measuring typing patterns (dwell time, flight time, speed) |
| **Dwell Time** | Duration a key is held down (press → release) |
| **Flight Time** | Time between releasing one key and pressing the next |
| **Digraph Latency** | Time between pressing two consecutive keys |
| **Isolation Forest** | Unsupervised ML algorithm for anomaly detection |
| **JWT** | JSON Web Token for stateless authentication |
| **SPA** | Single Page Application |

---

## 2. Overall Description

### 2.1 System Perspective

```
┌──────────────┐     REST API     ┌──────────────────┐     SQLite/
│  Web Client  │ ◄──────────────► │  FastAPI Backend  │ ◄── PostgreSQL
│  (React)     │     /api/*       │  (Python 3.11)    │
└──────────────┘                  └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │   ML Engine       │
                                  │  (Scikit-learn)   │
                                  └──────────────────┘
```

### 2.2 Product Features
1. **Keystroke Enrollment** — Collect 5 typing samples to build a biometric profile
2. **Keystroke Authentication** — Verify identity by comparing new sample against stored profile
3. **Dual-Mode ML** — Statistical mode (< 5 samples) and Isolation Forest (≥ 5 samples)
4. **Real-Time Metrics** — Live display of dwell time, flight time, and typing speed
5. **Confidence Scoring** — 0–100% confidence gauge with pass/fail threshold
6. **Security Layer** — Anti-replay protection, rate limiting, JWT tokens

### 2.3 User Classes
| User Class | Description |
|------------|------------|
| **New User** | Registers and completes enrollment by typing 5 samples |
| **Enrolled User** | Authenticates by typing the challenge phrase |
| **Authenticated User** | Accesses dashboard, views profile, and auth history |

### 2.4 Operating Environment
- **Backend:** Python 3.11+, FastAPI, SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React 19, Vite 6, modern browsers (Chrome, Firefox, Edge, Safari)
- **Deployment:** Docker, Docker Compose

---

## 3. Functional Requirements

### 3.1 User Registration (FR-01)
| ID | Requirement |
|----|------------|
| FR-01.1 | System shall accept username, name, and first keystroke sample |
| FR-01.2 | Username must be unique (case-insensitive) |
| FR-01.3 | System shall extract 36 biometric features from the sample |
| FR-01.4 | System shall create a keystroke profile for the user |
| FR-01.5 | System shall return enrollment status (samples collected / required) |

### 3.2 Enrollment (FR-02)
| ID | Requirement |
|----|------------|
| FR-02.1 | System shall accept additional typing samples for an existing user |
| FR-02.2 | After 5 samples collected, system shall train an Isolation Forest model |
| FR-02.3 | System shall store the serialized ML model in the keystroke profile |
| FR-02.4 | System shall mark the user as enrolled after model training |

### 3.3 Authentication (FR-03)
| ID | Requirement |
|----|------------|
| FR-03.1 | System shall accept username and keystroke sample for authentication |
| FR-03.2 | System shall extract features and compare against stored profile |
| FR-03.3 | System shall return a confidence score (0.0 – 1.0) |
| FR-03.4 | System shall issue a JWT token if confidence ≥ threshold (default 0.85) |
| FR-03.5 | System shall log every authentication attempt (success/failure, score, IP, device) |

### 3.4 User Dashboard (FR-04)
| ID | Requirement |
|----|------------|
| FR-04.1 | Authenticated users shall view their profile information |
| FR-04.2 | Authenticated users shall view authentication history (last 50 attempts) |
| FR-04.3 | Dashboard shall display security score based on auth history |
| FR-04.4 | Dashboard shall show quick stats (total logins, success rate, avg confidence) |

### 3.5 Feature Extraction (FR-05)
| ID | Requirement |
|----|------------|
| FR-05.1 | System shall extract the following 36 features from keystroke data: |
| | – Dwell time statistics (mean, std, min, max, median, Q25, Q75) |
| | – Flight time statistics (7 features) |
| | – Digraph latency statistics (7 features) |
| | – Typing speed (chars/sec) |
| | – Total typing duration |
| | – Pause ratio |
| | – Key transition entropy |
| | – Pressure statistics (7 features, mobile) |
| | – Touch size statistics (if available, mobile) |

---

## 4. Non-Functional Requirements

### 4.1 Security (NFR-01)
| ID | Requirement |
|----|------------|
| NFR-01.1 | Anti-replay protection shall reject duplicate keystroke submissions within a time window |
| NFR-01.2 | Rate limiter shall restrict to 5 authentication attempts per username per 60 seconds |
| NFR-01.3 | JWT tokens shall expire after the configured time (default 60 min) |
| NFR-01.4 | CORS shall be restricted to configured origins |
| NFR-01.5 | No plaintext passwords are stored or transmitted |

### 4.2 Performance (NFR-02)
| ID | Requirement |
|----|------------|
| NFR-02.1 | Feature extraction shall complete in < 50ms |
| NFR-02.2 | ML inference shall complete in < 100ms |
| NFR-02.3 | API response time shall be < 500ms for all endpoints |
| NFR-02.4 | Frontend shall capture keystrokes with sub-millisecond precision (performance.now()) |

### 4.3 Usability (NFR-03)
| ID | Requirement |
|----|------------|
| NFR-03.1 | Registration shall guide users through a 2-step wizard |
| NFR-03.2 | Live typing metrics shall be displayed during input |
| NFR-03.3 | Confidence gauge shall provide immediate visual feedback |
| NFR-03.4 | Dark glassmorphism UI shall provide premium feel |

### 4.4 Reliability (NFR-04)
| ID | Requirement |
|----|------------|
| NFR-04.1 | System shall gracefully handle fewer than minimum keystrokes |
| NFR-04.2 | System shall fall back to statistical mode when ML model is unavailable |
| NFR-04.3 | Docker health checks shall monitor service availability |

---

## 5. System Architecture

```
                    ┌─────────────────────────────────────────┐
                    │             Docker Compose              │
                    │  ┌───────────┐       ┌───────────────┐  │
 User ◄──────────►  │  │  Nginx    │──────►│  FastAPI      │  │
   Browser          │  │  (React   │ /api  │  (Python)     │  │
                    │  │   SPA)    │       │               │  │
                    │  │  :80      │       │  :8000        │  │
                    │  └───────────┘       └───────┬───────┘  │
                    │                              │          │
                    │                     ┌────────▼────────┐ │
                    │                     │    SQLite DB     │ │
                    │                     │  (Volume Mount)  │ │
                    │                     └─────────────────┘ │
                    └─────────────────────────────────────────┘
```

---

## 6. Data Dictionary

### 6.1 Users Table
| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | VARCHAR(36) | PK | UUID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login identifier |
| name | VARCHAR(100) | NOT NULL | Display name |
| device_type | VARCHAR(20) | DEFAULT 'web' | Primary device |
| is_enrolled | BOOLEAN | DEFAULT FALSE | Enrollment completed |
| created_at | DATETIME | AUTO | Registration timestamp |
| updated_at | DATETIME | AUTO | Last update timestamp |

### 6.2 Keystroke Profiles Table
| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | VARCHAR(36) | PK | UUID |
| user_id | VARCHAR(36) | FK → users.id | Owner |
| feature_vector | TEXT | JSON | Averaged feature vector |
| model_data | TEXT | JSON | Serialized ML model |
| threshold | FLOAT | DEFAULT 0.85 | Confidence threshold |
| is_trained | BOOLEAN | DEFAULT FALSE | ML model trained |
| created_at | DATETIME | AUTO | Creation timestamp |
| updated_at | DATETIME | AUTO | Last update |

### 6.3 Enrollment Samples Table
| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | VARCHAR(36) | PK | UUID |
| user_id | VARCHAR(36) | FK → users.id | Owner |
| sample_number | INTEGER | NOT NULL | Sample sequence number |
| raw_keystrokes | TEXT | JSON | Original keystroke data |
| features | TEXT | JSON | Extracted feature vector |
| device_type | VARCHAR(20) | | Device used |
| created_at | DATETIME | AUTO | Capture timestamp |

### 6.4 Auth Logs Table
| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| id | VARCHAR(36) | PK | UUID |
| user_id | VARCHAR(36) | FK → users.id | User attempted |
| result | VARCHAR(20) | NOT NULL | accepted / rejected |
| confidence_score | FLOAT | | Match confidence |
| threshold_used | FLOAT | | Threshold at time of auth |
| method_used | VARCHAR(30) | | statistical / isolation_forest |
| ip_address | VARCHAR(45) | | Client IP |
| device_type | VARCHAR(20) | | Device used |
| timestamp | DATETIME | AUTO | Attempt time |

---

## 7. API Specification

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | ❌ | Health check |
| POST | `/api/register` | ❌ | Register + first sample |
| POST | `/api/enroll` | ❌ | Submit enrollment sample |
| GET | `/api/enrollment-status/{username}` | ❌ | Check enrollment progress |
| POST | `/api/authenticate` | ❌ | Login via keystroke |
| GET | `/api/user/profile` | ✅ JWT | Get user profile |
| GET | `/api/user/auth-history` | ✅ JWT | Get auth history |

---

## 8. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend Framework | FastAPI | 0.109+ |
| ML Library | Scikit-learn | 1.4+ |
| Database ORM | SQLAlchemy | 2.0+ |
| Database | SQLite / PostgreSQL | 3.x / 16+ |
| Auth Tokens | python-jose (JWT) | 3.3+ |
| Frontend Framework | React | 19.x |
| Build Tool | Vite | 6.x |
| Routing | React Router | 7.x |
| Containerization | Docker | 24+ |
| Orchestration | Docker Compose | 2.x |
