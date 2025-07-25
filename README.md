# HDLP (Hash‑Based Data Loss Prevention)

A lightweight Python tool that watches a directory, hashes new/changed files with SHA3‑256, compares against a database, and raises alerts (and optional automated remediation) when matches are found.

---

## 🚀 Quick Start

1. **Clone the repo**  
   ```bash
   git clone https://github.com/<username>/HDLP.git
   cd HDLP
# HDLP (Hash-Based Data Loss Prevention)

A lightweight Python tool that monitors file changes, hashes them using SHA3-256, and compares them against a database of known sensitive file hashes. Alerts are triggered when matches are found, with an optional dashboard for viewing and management.

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/HDLP.git
cd HDLP
```

### 2. One-Time Setup

```bash
chmod +x setup_env.sh
./setup_env.sh
```

This will:
- Create a project-local virtual environment (`hdlp-venv`)
- Install required dependencies from `requirements.txt`
- Initialize the SQLite database (`hash_store.db`)
- Create the logs directory (`logs/`)

### 3. Run the Tool

```bash
chmod +x start_services.sh
./start_services.sh
```

This will:
- Activate the virtual environment
- Start the Flask dashboard (`main.py`)
- Start the file-watcher service (`watch_alerts.py`)
- Monitor logs in `logs/`

To stop the tool, press `Ctrl + C`.

### 4. Access the Dashboard

Open your browser and go to:

```
http://localhost:5000
```

---

## Requirements

- Python 3.10+
- Flask
- watchdog

Dependencies will be installed automatically by `setup_env.sh`. If you prefer manual installation:

```bash
pip install -r requirements.txt
```

Note: `sqlite3` is included with Python’s standard library.

---

## Project Structure

```
HDLP/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── setup_env.sh          # One-time environment setup script
├── start_services.sh     # Script to launch dashboard and watcher
├── hdlp-venv/             # (Generated) Python virtual environment
├── hash_store.db          # SQLite DB of known sensitive hashes
├── logs/
│   ├── alerts_log.txt
│   ├── flask.log
│   └── watchdog.log
├── main.py                # Flask dashboard server
├── watch_alerts.py        # Watchdog logic and alert triggering
├── static/
│   └── styles.css         # Frontend styles
└── templates/
    └── dashboard.html     # Flask dashboard template
```

---

## Contributing

1. Fork this repository
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Make your changes and commit: `git commit -m "Add YourFeature"`
4. Push to your fork: `git push origin feature/YourFeature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See `LICENSE` for full details.

bash
Copy
Edit
chmod +x setup_env.sh
./setup_env.sh
Creates a project‑local virtualenv named hdlp-venv

Installs dependencies from requirements.txt

Initializes hash_store.db

Creates the logs/ directory

Launch services

bash
Copy
Edit
chmod +x start_services.sh
./start_services.sh
Activates hdlp-venv

Clears the alerts log (logs/alerts_log.txt)

Starts the Flask dashboard (main.py)

Starts the file‑watcher (watch_alerts.py)

Press Ctrl+C to shut down gracefully

View dashboard
Open your browser at:

arduino
Copy
Edit
http://localhost:5000
📦 Requirements
Python 3.10+

Flask

watchdog

Install (done for you by setup_env.sh):

bash
Copy
Edit
pip install -r requirements.txt
Note: sqlite3 is built into Python and does not need to be listed.

📁 Project Structure
csharp
Copy
Edit
HDLP/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── setup_env.sh        # one‑time setup: venv, deps, DB, logs
├── start_services.sh   # start/stop Flask & watcher
├── hdlp-venv/          # project‑local virtualenv
├── hash_store.db       # SQLite DB of known hashes
├── logs/
│   ├── alerts_log.txt
│   ├── flask.log
│   └── watchdog.log
├── main.py             # Flask dashboard & API
├── watch_alerts.py     # file‑system watcher & alert logic
├── static/
│   └── styles.css
└── templates/
    └── dashboard.html
⚙️ Usage
Populate the DB with your sensitive‑file hashes (via script or direct SQLite insert).

Run the watcher and dashboard:

bash
Copy
Edit
./start_services.sh
Monitor alerts in the dashboard or check logs/alerts_log.txt.

🤝 Contributing
Fork the repo.

git checkout -b feature/YourFeature

git commit -m "Add awesome feature"

git push origin feature/YourFeature

Open a Pull Request.

📝 License
This project is licensed under the MIT License. 
