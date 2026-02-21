<p align="center">
  <img src="logo.svg" alt="KeyAuth Logo" width="180" />
</p>

# 🔐 KeyAuth — Keystroke Dynamics Authentication

> **Passwordless authentication powered by your unique typing rhythm.**  
> No passwords. No hardware tokens. Just type.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- **🧠 ML-Powered Authentication** — Isolation Forest anomaly detection with statistical fallback
- **⌨️ 36 Biometric Features** — Dwell time, flight time, digraph latency, speed, pressure, and more
- **🎯 Confidence Scoring** — Real-time 0–100% confidence gauge
- **🔒 Security First** — Anti-replay protection, rate limiting, JWT tokens
- **🌙 Premium Dark UI** — Glassmorphism design with neon accents
- **📊 Dashboard** — Auth history, security score, and quick stats
- **🐳 Docker Ready** — One-command deployment with Docker Compose

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Docker & Docker Compose

### Development

**1. Backend:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Frontend:**
```bash
cd web-frontend
npm install
npm run dev
```

**3. Open:** http://localhost:5173

### Docker (Production)
```bash
docker compose up --build -d
# Open http://localhost
```

---

## 🔄 How It Works

```
Register ──→ Type phrase 5× ──→ ML model trained
                                       │
Login ──→ Type phrase ──→ Feature extraction ──→ ML comparison ──→ Score
                                                                     │
                              ┌─────────────────────────────────────┘
                              │
                    Score ≥ 85% → ✅ Verified (JWT issued)
                    Score < 85% → ❌ Rejected
```

1. **Register** — Enter your name + username, then type `the quick brown fox jumps over the lazy dog`
2. **Enroll** — Repeat 5 times so the system learns your typing pattern
3. **Login** — Type the phrase again; the system compares your rhythm to its model
4. **Dashboard** — View your security score, auth history, and typing stats

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | ❌ | Health check |
| `POST` | `/api/register` | ❌ | Register + first sample |
| `POST` | `/api/enroll` | ❌ | Submit enrollment sample |
| `GET` | `/api/enrollment-status/{username}` | ❌ | Check progress |
| `POST` | `/api/authenticate` | ❌ | Login via keystrokes |
| `GET` | `/api/user/profile` | ✅ | User profile |
| `GET` | `/api/user/auth-history` | ✅ | Auth attempt logs |

Full interactive docs: http://localhost:8000/docs

---

## 🗄️ Database Schema

```
Users (1) ──── (0..1) Keystroke Profiles
  │
  ├──── (0..N) Enrollment Samples
  │
  └──── (0..N) Auth Logs
```

See [ER Diagram](docs/ER_Diagram.md) for full schema details.

---

## 📁 Project Structure

```
├── backend/           # FastAPI + ML engine
│   ├── app/
│   │   ├── ml/        # Feature extraction + Isolation Forest
│   │   └── routes/    # API endpoints
│   └── Dockerfile
├── web-frontend/      # React + Vite SPA
│   ├── src/
│   │   ├── components/  # Navbar, ConfidenceGauge, TypingMetrics
│   │   ├── pages/       # Register, Login, Dashboard
│   │   └── hooks/       # useKeystrokeCapture
│   └── Dockerfile
├── docs/              # SRS, ER Diagram, Architecture
├── docker-compose.yml
└── README.md
```

---

## 📚 Documentation

- [Software Requirements Specification (SRS)](docs/SRS.md)
- [ER Diagram](docs/ER_Diagram.md)
- [System Architecture](docs/Architecture.md)

---

## 🛡️ Security

| Feature | Description |
|---------|------------|
| No Passwords | Behavioral biometrics — nothing to steal |
| Anti-Replay | Hash-based duplicate submission detection |
| Rate Limiting | 5 attempts per user per 60 seconds |
| JWT Tokens | Short-lived, HS256-signed access tokens |
| CORS | Configurable origin whitelist |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
