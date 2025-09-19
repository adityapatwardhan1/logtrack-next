# LogTrack

LogTrack is a log monitoring and anomaly detection system with an optional dashboard built using Streamlit. This setup focuses on **reproducibility**, using Docker for the PostgreSQL database and a Makefile for all commands.

---

## Features

- **Reproducible environment**: Docker for PostgreSQL + Makefile automation  
- **Parsers**: Pluggable parsers for:  
  - Line-oriented formats (CLF / Apache / Nginx)  
  - HDFS-style CSV (Hadoop Distributed File System) 
  - JSON CloudTrail-style logs  
- **Detection**:  
  - Rule-based detectors  
  - Z-score statistical detector  
- **CLI**: Ingest logs, run detection, view logs, create users  
- **Dashboard**: Streamlit UI to explore logs and alerts (optional)  
- **User management**: Hashed passwords (argon2-cffi)  
- **Tests**: Pytest-based unit tests for detection logic  

---

## How Detection Works (High Level)

- **Keyword threshold**: Counts messages containing a keyword inside sliding windows.  
- **Repeated message**: Detects identical messages repeated N times within a window.  
- **Inactivity**: Triggers if a service has been silent for `max_idle_minutes`.  
- **Rate spike**: Detects N+ logs for a service in a given short window.  
- **Z-score**: Bins recent log volume into windows, computes baseline mean/std, flags if z-score exceeds threshold.  

All detectors operate on the normalized schema, making them source-agnostic.

---

## Requirements

- Python 3.10+  
- Docker & Docker Compose (sudo permissions required)  
- Make  

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd logtrack-next
```

### 2. Set up a Python virtual environment

```bash
make venv
```

Activate the environment:

```bash
source venv/bin/activate
```

### 3. Initialize the database (Docker)

We use Docker **only for PostgreSQL**, ensuring full reproducibility.

```bash
# In one terminal
sudo make docker-down         # Stop and remove any existing containers
sudo rm -rf ./db/data         # Delete old database files to start fresh
sudo make docker-up           # Start PostgreSQL container
```

When finished with your session:

```bash
sudo make docker-down         # Stop database container
```

> ⚠️ You need `sudo` because Docker may require it to manage containers and volumes.

---

## Initialize the Application

In another terminal (while Docker is running):

```bash
source venv/bin/activate
make reinit                    # Reset & initialize database and migrate rules
make user username=yourname    # Create a user; follow prompt to set password
make dash                      # Start the Streamlit dashboard
```

---

## Ingesting Logs & Running Detection (Example)

Place a log file (in one of the supported formats) in the repo root, or specify a full file path.

In an **activated virtual environment**:

```bash
make ingest file=example.clf     # Parse & insert logs into the database
make detect                      # Run detection and write alerts to the DB
```

Or run both in one command:

```bash
make ingest-detect file=example.clf
```

---

### View Logs in the CLI

```bash
make print
```

---

### Open the Dashboard

```bash
make dash
```

Then open the Streamlit URL printed in the terminal, e.g.:

```
http://localhost:8501
```

---

## Common Make Commands

| Command                     | Description                             |
|-----------------------------|-------------------------------------|
| `make reinit`               | Reset DB, initialize, migrate rules  |
| `make init-db`              | Initialize DB and migrate rules       |
| `make reset-db`             | Clear the database                    |
| `make ingest-detect file=<filename>` | Ingest logs from a file and run detection |
| `make ingest file=<filename>`          | Ingest logs only                 |
| `make detect`               | Run anomaly detection                 |
| `make print`                | Show logs in CLI                     |
| `make test`                 | Run tests                           |
| `make dash`                 | Launch Streamlit dashboard           |
| `make docker-up`            | Start PostgreSQL container via Docker|
| `make docker-down`          | Stop PostgreSQL container            |
| `make venv`                 | Create virtual environment & install dependencies |
| `make activate`             | Instructions to activate virtual environment |
| `make user username=<name>` | Create a new user (prompt for password) |

---

## Notes

- The dashboard and CLI are **independent**; you can use either.  
- The system is **reproducible**: deleting `./db/data` and restarting Docker will give a clean database.  
- Docker is used only for the database, so all Python commands run in the host environment (or virtualenv).  
- For a fully fresh start:

```bash
sudo make docker-down
sudo rm -rf ./db/data
sudo make docker-up
make reinit
```

---

## Optional: Adding More Users

```bash
make user username=<new_username>
```

Follow the prompt to set a password and assign a role (currently only `user`).

---

## Recommended Workflow

1. Start PostgreSQL:

```bash
sudo make docker-up
```

2. In another terminal:

```bash
make reinit
make user username=yourname
make dash
```

3. When done:

```bash
sudo make docker-down
```
