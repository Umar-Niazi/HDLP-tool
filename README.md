# HDLP (Hash-Based Data Loss Prevention)

A lightweight Python tool that monitors file changes, hashes them using SHA3-256, and compares them against a database of known sensitive file hashes. Alerts are triggered when matches are found, with an optional dashboard for viewing and management.

-----

## Quick Start

### 1\. Clone the Repository

```bash
git clone https://github.com/<your-username>/HDLP.git
cd HDLP
```

### 2\. One-Time Setup

```bash
chmod +x setup_env.sh
./setup_env.sh
```

This will:

  - Create a project-local virtual environment (`hdlp-venv`)
  - Install required dependencies from `requirements.txt`
  - Initialize the SQLite database (`hash_store.db`)
  - Create the logs directory (`logs/`)

### 3\. Run the Tool

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

### 4\. Access the Dashboard

Open your browser and go to:

```
http://localhost:5000
```

-----

## Requirements

  - Python 3.10+
  - Flask
  - watchdog

Dependencies will be installed automatically by `setup_env.sh`. If you prefer manual installation:

```bash
pip install -r requirements.txt
```

Note: `sqlite3` is included with Python’s standard library.

-----

## Project Structure

```
HDLP/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── setup_env.sh          # One-time environment setup script
├── start_services.sh     # Script to launch dashboard and watcher
├── hdlp-venv/            # (Generated) Python virtual environment
├── hash_store.db         # SQLite DB of known sensitive hashes
├── logs/
│   ├── alerts_log.txt
│   ├── flask.log
│   └── watchdog.log
├── main.py               # Flask dashboard server
├── watch_alerts.py       # Watchdog logic and alert triggering
├── static/
│   └── styles.css        # Frontend styles
└── templates/
    └── dashboard.html    # Flask dashboard template
```

-----

## Contributing

1.  Fork this repository
2.  Create a new branch: `git checkout -b feature/YourFeature`
3.  Make your changes and commit: `git commit -m "Add YourFeature"`
4.  Push to your fork: `git push origin feature/YourFeature`
5.  Open a Pull Request

-----

## License

This project is licensed under the MIT License. See `LICENSE` for full details.
