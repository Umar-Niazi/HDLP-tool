# HDLP-tool (Hash‑Based Data Loss Prevention)

A lightweight Python tool that watches a directory, hashes new/changed files with SHA3‑256, compares against a database, and raises alerts (and optional automated remediation) when matches are found.

## Features

- **Real‑time monitoring** of your sensitive folder
- **SHA3‑256 hashing** for robust fingerprinting
- **Alert logging** to `logs/alerts_log.txt`
- **Optional remediation scripts** (e.g. quarantine, notifications)
- **Web dashboard** (`Flask`‑powered) at `localhost:5000`

## Requirements

- Python 3.10+  
- Flask  
- watchdog  
- sqlite3 (built‑in)

Install dependencies with:

```bash
pip install -r requirements.txt

