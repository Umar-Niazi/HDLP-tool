# HDLP (Hash‑Based Data Loss Prevention)

A lightweight Python tool that watches a directory, hashes new/changed files with SHA3‑256, compares against a database, and raises alerts (and optional automated remediation) when matches are found.

---

## 🚀 Quick Start

1. **Clone the repo**  
   ```bash
   git clone https://github.com/<username>/HDLP.git
   cd HDLP
One‑time setup

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
