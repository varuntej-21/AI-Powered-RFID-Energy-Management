# AI-Powered RFID Energy Management System

An intelligent IoT-based energy management and access-control system that combines RFID authentication, ESP32 hardware, a FastAPI backend, device simulation, and a monitoring dashboard.

The system is designed to provide centralized control, monitoring, and data management for RFID-enabled energy systems.

## 🚀 Overview

The project connects physical RFID-based identification with a backend API and monitoring interface.

It consists of four major components:

- **RFID / ESP32 firmware** – handles RFID-based device interaction
- **FastAPI backend** – provides APIs and manages system data
- **Device simulator** – enables development and testing without physical hardware
- **Dashboard** – provides a user-facing interface for monitoring and management

### System Architecture

```text
                    ┌─────────────────────┐
                    │     RFID Reader     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     ESP32 Device    │
                    │   RFID + Controller  │
                    └──────────┬──────────┘
                               │
                               │ API / Data
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │                     │
                    │  API / Data Models  │
                    │  Business Logic     │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │    Dashboard    │       │  Device Simulator│
        │                 │       │                 │
        │ Monitoring/UI   │       │ Testing/Debugging│
        └─────────────────┘       └─────────────────┘

✨ Key Features
RFID-based identification
ESP32-based device integration
FastAPI REST backend
Device simulation for development and testing
Real-time system monitoring
Dashboard-based visualization
Structured backend data models
Hardware-to-backend communication
Modular architecture for future expansion
🛠️ Technology Stack
Backend
Python
FastAPI
REST APIs
Hardware / Embedded
ESP32
RFID
Embedded C/C++
Frontend / Dashboard
Python-based dashboard
Development & Testing
Device simulation
Git
GitHub
📁 Project Structure
AI-Powered-RFID-Energy-Management/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── dashboard/
│   └── app.py
│
├── device_sim/
│   └── sim_client.py
│
├── esp32_firmware/
│   └── esp32_rfid_energy.ino
│
├── requirements.txt
├── README.md
└── .gitignore
⚙️ Getting Started
1. Clone the repository
git clone https://github.com/varuntej-21/AI-Powered-RFID-Energy-Management.git
cd AI-Powered-RFID-Energy-Management
2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

Linux / macOS:

python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
▶️ Running the Backend

Start the FastAPI application using:

uvicorn backend.main:app --reload

The API will be available at:

http://127.0.0.1:8000

FastAPI's interactive API documentation can be accessed at:

http://127.0.0.1:8000/docs
🧪 Device Simulation

The project includes a device simulator that can be used to test the backend without requiring the physical ESP32/RFID hardware.


python device_sim/sim_client.py

This allows the software components to be developed and tested independently from the physical device.

<img width="1917" height="910" alt="image" src="https://github.com/user-attachments/assets/61123329-dff8-4594-91a8-f09b395fdaec" />


The dashboard provides a user-facing interface for interacting with and monitoring the system.

Run:

python dashboard/app.py

The exact command may vary depending on the dashboard framework and configuration.

🔌 Hardware

The embedded component is located in:

esp32_firmware/esp32_rfid_energy.ino

The ESP32 is responsible for interfacing with the RFID hardware and communicating system information to the backend.

🔐 Security

Sensitive credentials and local configuration should not be committed to the repository.

The project .gitignore excludes:

Environment variables
Virtual environments
Local databases
Logs
IDE-specific files
Python cache files
🔮 Future Enhancements

Potential future improvements include:

AI-based energy consumption prediction
Intelligent anomaly detection
Automated energy optimization
Advanced analytics
Role-based access control
Cloud deployment
Real-time notifications
IoT device fleet management
Predictive maintenance
🎯 Project Goals

The project demonstrates how embedded hardware, RFID identification, backend APIs, device simulation, and monitoring interfaces can be integrated into a single IoT platform.

It is structured to support future development toward intelligent, data-driven energy management.

👨‍💻 Author

Varuntej Kurakula

AI/ML Engineer | Embedded & IoT Systems

GitHub:
https://github.com/varuntej-21

📄 License

This project is available for educational and development purposes.
