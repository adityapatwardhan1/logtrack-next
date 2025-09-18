# LogTrack

LogTrack is a log monitoring and anomaly detection system with an optional dashboard built using Streamlit. This setup focuses on **reproducibility**, using Docker for the PostgreSQL database and a Makefile for all commands.

---

## Requirements

- Python 3.10+  
- Docker & Docker Compose (sudo permissions required)  
- Make  

---

## Setup

### 1. Clone the repository

```
git clone <repo-url>
cd logtrack-next
```

### 2. Set up a Python virtual environment

```
make venv
```

Activate the environment:

```
source venv/bin/activate
```

### 3. Initialize the database (Docker)

We use Docker **only for PostgreSQL**, so the system is fully reproducible.

```
# In one terminal
sudo make docker-down         # Stop and remove any existing containers
sudo rm -rf ./db/data         # Delete old database files to start fresh
sudo make docker-up           # Start PostgreSQL container
```

Once done with your session:

```
sudo make docker-down         # Stop database container
```

> ⚠️ You need `sudo` because Docker may require it to manage containers and volumes.

---

## Initialize the application

In another terminal (while Docker is running):

```
source venv/bin/activate
make reinit                    # Reset & initialize database and migrate rules
make user username=yourname    # Create a user; follow prompt to set password
make dash                      # Start the Streamlit dashboard
```

---

## Common Make Commands

| Command                  | Description |
|---------------------------|-------------|
| make reinit             | Reset DB, initialize, migrate rules |
| make init-db            | Initialize DB and migrate rules |
| make reset-db           | Clear the database |
| make ingest-detect file=<filename> | Ingest logs from a file and run detection |
| make ingest file=<filename> | Ingest logs only |
| make detect             | Run anomaly detection |
| make print              | Show logs in CLI |
| make test               | Run tests |
| make dash               | Launch Streamlit dashboard |
| make docker-up          | Start PostgreSQL container via Docker |
| make docker-down        | Stop PostgreSQL container |
| make venv               | Create virtual environment & install dependencies |
| make activate           | Instructions to activate virtual environment |
| make user username=<name> | Create a new user (prompt for password) |

---

## Notes

- The dashboard and CLI are **independent**; you can use either.  
- The system is **reproducible**: deleting `./db/data` and restarting Docker will give a clean database.  
- Docker is used only for the database, so all Python commands run in the host environment (or venv).  
- For a fully fresh start:

```
sudo make docker-down
sudo rm -rf ./db/data
sudo make docker-up
make reinit
```

---

## Optional: Adding More Users

```
make user username=<new_username>
```

Follow the prompt to set a password and assign a role (currently only `user`).

---

## Recommended Workflow

1. Start PostgreSQL:

```
sudo make docker-up
```

2. In another terminal:

```
make reinit
make user username=yourname
make dash
```

3. When done:

```
sudo make docker-down
```