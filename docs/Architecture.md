# System Architecture
## KeyAuth — Keystroke Dynamics Authentication

---

## High-Level Architecture

```mermaid
graph TB
    subgraph Client["🌐 Client Layer"]
        WEB["React SPA<br/>(Vite, Port 5173)"]
    end

    subgraph API["⚙️ API Layer"]
        FASTAPI["FastAPI Server<br/>(Uvicorn, Port 8000)"]
        CORS["CORS Middleware"]
        RATE["Rate Limiter"]
        REPLAY["Anti-Replay Guard"]
        JWT["JWT Auth"]
    end

    subgraph ML["🧠 ML Engine"]
        FE["Feature Extractor<br/>(36 dimensions)"]
        STAT["Statistical Mode<br/>(Manhattan + Cosine)"]
        ISO["Isolation Forest<br/>(Scikit-learn)"]
    end

    subgraph DB["💾 Data Layer"]
        SQLITE["SQLite / PostgreSQL"]
        MODELS["4 ORM Models"]
    end

    WEB -->|"REST /api/*"| CORS
    CORS --> FASTAPI
    FASTAPI --> RATE
    FASTAPI --> REPLAY
    FASTAPI --> JWT
    FASTAPI -->|"Keystroke Data"| FE
    FE -->|"< 5 samples"| STAT
    FE -->|"≥ 5 samples"| ISO
    STAT -->|"Confidence Score"| FASTAPI
    ISO -->|"Confidence Score"| FASTAPI
    FASTAPI -->|"SQLAlchemy ORM"| MODELS
    MODELS --> SQLITE
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User Browser
    participant F as React Frontend
    participant A as FastAPI Backend
    participant ML as ML Engine
    participant DB as SQLite Database

    Note over U,DB: Registration & Enrollment Flow
    U->>F: Enter name, username
    F->>U: Show typing challenge
    U->>F: Type phrase (keydown/keyup captured)
    F->>A: POST /api/register {username, name, keystrokes}
    A->>ML: extract_features(keystrokes)
    ML-->>A: 36-dim feature vector
    A->>DB: Store User + Profile + Sample
    A-->>F: {samples_collected: 1, required: 5}

    loop 4 more times
        U->>F: Re-type phrase
        F->>A: POST /api/enroll {username, keystrokes}
        A->>ML: extract_features(keystrokes)
        A->>DB: Store sample
    end
    A->>ML: Train Isolation Forest model
    A->>DB: Store serialized model
    A-->>F: {is_enrolled: true}

    Note over U,DB: Authentication Flow
    U->>F: Enter username + type phrase
    F->>A: POST /api/authenticate {username, keystrokes}
    A->>A: Rate limit check ✓
    A->>A: Anti-replay check ✓
    A->>ML: extract_features(keystrokes)
    ML-->>A: Feature vector
    A->>DB: Load user profile + model
    A->>ML: model.authenticate(features)
    ML-->>A: confidence_score
    A->>DB: Log auth attempt
    alt confidence ≥ 0.85
        A-->>F: {authenticated: true, token: JWT}
        F->>U: Show dashboard
    else confidence < 0.85
        A-->>F: {authenticated: false, score: 0.62}
        F->>U: Show rejection + confidence gauge
    end
```

---

## ML Pipeline Detail

```mermaid
graph LR
    subgraph Input
        KE["Raw Keystroke Events<br/>{key, press_time, release_time}"]
    end

    subgraph Features["Feature Extraction (36 dims)"]
        DT["Dwell Time<br/>(7 stats)"]
        FT["Flight Time<br/>(7 stats)"]
        DG["Digraph Latency<br/>(7 stats)"]
        SP["Speed + Duration<br/>+ Pause + Entropy"]
        PR["Pressure<br/>(7 stats, mobile)"]
        TS["Touch Size<br/>(4 stats, mobile)"]
    end

    subgraph Model["Model Selection"]
        CHECK{"Samples ≥ 5?"}
        SM["Statistical Mode<br/>Manhattan + Cosine"]
        MLM["Isolation Forest<br/>(anomaly detection)"]
    end

    subgraph Output
        SCORE["Confidence Score<br/>0.0 — 1.0"]
    end

    KE --> DT & FT & DG & SP & PR & TS
    DT & FT & DG & SP & PR & TS --> CHECK
    CHECK -->|"No"| SM
    CHECK -->|"Yes"| MLM
    SM --> SCORE
    MLM --> SCORE
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph Docker["Docker Compose"]
        subgraph FE_CTR["Frontend Container"]
            NGINX["Nginx :80"]
            REACT["React Build (static)"]
        end
        subgraph BE_CTR["Backend Container"]
            UVI["Uvicorn :8000"]
            APP["FastAPI App"]
            MLENG["ML Engine"]
        end
        VOL["Volume: backend-data"]
    end

    USER["👤 User"] -->|"HTTP :80"| NGINX
    NGINX -->|"Static files"| REACT
    NGINX -->|"Proxy /api/*"| UVI
    UVI --> APP --> MLENG
    APP -->|"SQLAlchemy"| VOL
```

---

## Security Architecture

| Layer | Protection | Implementation |
|-------|-----------|---------------|
| Transport | API proxy | Nginx reverse proxy strips direct backend access |
| Request | Rate limiting | 5 attempts / username / 60 seconds |
| Request | Anti-replay | Hash-based duplicate detection (10 min window) |
| Auth | JWT tokens | HS256, configurable expiry (default 60 min) |
| Data | No passwords | Behavioral biometrics only — nothing to steal |
| CORS | Origin whitelist | Configurable allowed origins |

---

## Directory Structure

```
Keystroke Dynamics Authentication/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (env vars)
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # 4 ORM models
│   │   ├── schemas.py           # Pydantic validation
│   │   ├── auth.py              # JWT utilities
│   │   ├── security.py          # Anti-replay + rate limiter
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── feature_extractor.py  # 36-feature extraction
│   │   │   ├── model.py              # ML engine
│   │   │   └── utils.py              # Math helpers
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── registration.py   # Register + Enroll
│   │       ├── authentication.py # Authenticate
│   │       └── user.py           # Profile + History
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── .dockerignore
├── web-frontend/
│   ├── src/
│   │   ├── api/client.js         # API client
│   │   ├── hooks/useKeystrokeCapture.js
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ConfidenceGauge.jsx
│   │   │   └── TypingMetrics.jsx
│   │   ├── pages/
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── styles/index.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── SRS.md
│   ├── ER_Diagram.md
│   └── Architecture.md
├── docker-compose.yml
└── README.md
```
