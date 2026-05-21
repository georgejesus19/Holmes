<div align="center">

# 🕵️‍♂️ Holmes

**Backdoor Detector for Windows Systems**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![VirusTotal](https://img.shields.io/badge/API-VirusTotal-394EFF?style=for-the-badge&logo=virustotal&logoColor=white)](https://www.virustotal.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-red?style=for-the-badge)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)]()

<br/>

> *Lightweight, modular and transparent Windows backdoor detection tool.*

<br/>

[Features](#-features) · [Modules](#-modules) · [Getting Started](#-getting-started) · [Roadmap](#-roadmap)

---

</div>

## 📖 Overview

**Holmes** is a lightweight and modular backdoor detection tool built for Windows system auditing. It identifies suspicious behaviors across processes, persistence mechanisms, network connections, and file execution — all from a clean terminal interface.

Holmes is **self-configuring**: on first run, it installs its own dependencies, initializes the SQLite database, and prepares its internal structure. No manual setup required.

```
⚡ Lightweight    🧩 Modular    🔍 Transparent    🖥️ Low resource usage
```

---

## 🌐 Internet Dependency

Holmes is **offline-first** in its analysis, but requires internet access for:

| Feature | Requirement |
|---|---|
| 📦 Dependency installation | First run only |
| 🔬 VirusTotal hash analysis | Active internet + API key |

---

## ✨ Features

<details>
<summary><strong>🔍 Process Analysis</strong></summary>

<br/>

- List and inspect all active processes
- Detect anomalous executable paths
- Collect: PID, PPID, process name, executable path, user, file hash, digital signature
- Compare against security blacklists
- Auto-insert results into SQLite

</details>

<details>
<summary><strong>🧷 Persistence Detection</strong></summary>

<br/>

Detects mechanisms used to keep malware active across reboots:

- **Registry keys:** `HKCU\...\Run` and `HKLM\...\Run`
- **Windows Services**
- **Scheduled Tasks**
- **Startup folders**

Each entry includes: hash, digital signature, user, and binary path.

</details>

<details>
<summary><strong>🌐 Network Module</strong></summary>

<br/>

- Monitor active connections
- Map connections to their owning processes
- Compare against suspicious IP/domain lists
- Flag potentially malicious traffic
- Auto-insert into database

</details>

<details>
<summary><strong>🔎 Manual Analysis Mode</strong></summary>

<br/>

Individually investigate any suspicious element:

- Processes, files, services, scheduled tasks, network connections
- Hash calculation + digital signature verification
- VirusTotal lookup
- Blacklist comparison
- Environment variable expansion and path normalization

</details>

---

## ⚡ Defensive Actions

Holmes isn't just passive — when a suspicious item is found, you can act directly from the interface:

| Target | Available Actions |
|---|---|
| 🔍 **Process** | Terminate suspicious process |
| 🧷 **Registry** | Remove persistence entry |
| ⚙️ **Service** | Disable service |
| 📅 **Scheduled Task** | Disable task |
| 🌐 **Network** | Terminate process tied to connection |

---

## 🧩 Modules

```
Holmes/
├── 🔬 processes/       → Process analysis & detection
├── 🧷 persistence/     → Registry, services, tasks, startup
├── 🌐 network/         → Connection monitoring & mapping
├── 🔎 manual/          → Manual investigation interface
├── 🖥️ interface/       → Terminal menu & navigation
├── 🗄️ database/        → SQLite auto-init & logging
```

---

## 🗄️ Database (Auto-Initialized)

Holmes manages its own SQLite database with zero manual configuration:

- ✅ Created automatically on first run
- ✅ Tables initialized by Holmes itself
- ✅ Auto-populated by each module (processes, persistence, network)
- ✅ Ready for audit history and future expansion

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed and added to `PATH`
- **Administrator privileges** (required for system-level access)

---

### 1. Clone the repository

```bash
git clone https://github.com/your-username/holmes.git
cd holmes
```

---

### 2. Create the `.env` file

In the project root, create a `.env` file:

```env
HOLMES_API_KEY=YOUR_VIRUSTOTAL_API_KEY
```

> 🔑 Get your free API key at [virustotal.com](https://www.virustotal.com/)

---

### 3. Run as Administrator

> ⚠️ Administrator rights are required to read system processes, services, registry, and scheduled tasks.

Right-click **Command Prompt** → *Run as administrator*, then:

```bash
cd C:\Path\To\Holmes
python main.py
```

Holmes handles everything else automatically on first launch.

---

### 4. Main Menu

```
╔══════════════════════════════╗
║        🕵️  HOLMES v1.0       ║
╠══════════════════════════════╣
║  [1] Process Analysis        ║
║  [2] Persistence(HKCU & HKLM)║
║  [3] Network                 ║
║  [4] Manual Analysis         ║         
║  [0] Exit                    ║
╚══════════════════════════════╝
```

---

## 🔧 Current Status

| Module | Status |
|---|---|
| 🔬 Process Analysis | ✅ Implemented |
| 🧷 Persistence Detection | ✅ Implemented |
| 🌐 Network Monitoring | ✅ Implemented |
| 🔎 Manual Analysis | ✅ Operational |
| 🌍 VirusTotal Integration | ✅ Implemented |
| 🗄️ SQLite Auto-init | ✅ Implemented |
| 🔐 Blacklists & Signatures | ✅ Implemented |
| ⚡ Defensive Actions | ✅ Implemented |
| 🖥️ Terminal Interface | ✅ Functional |
| ⚙️ Auto-configuration | ✅ Implemented |

---

## 🗺️ Roadmap

### v2.0

- [ ] 🧠 **Lightweight AI** — Behavioral process analysis without blacklist dependency
- [ ] 📊 **Rich Interface** — Visual dashboards, interactive tables, threat indicators
- [ ] 👁️ **Real-time Monitoring** — Startup folder watchdog, live change detection
- [ ] ⚡ **Performance Optimization** — Reduced overhead across all modules

---

## 🎯 Goal

Holmes is built to evolve into a complete, self-contained Windows security auditing suite:

- **Offline-first** analysis
- **Automatic** configuration and setup
- **Modular** and easily extensible
- **Transparent** and fully auditable
- **Future-ready** for lightweight AI integration

---

<div align="center">

Made with 🔍 for Windows security auditing

⭐ **Star this repo** if Holmes helped you!

</div>
