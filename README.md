# Fortress AI - Agent Backend 🧠
### *The "Brain" behind the Stronghold*

This branch contains the Python backend and the **Droidrun Agent** logic that performs the autonomous security auditing.

## ⚙️ How it Works
The backend hosts a Flask API that triggers a **Droidrun Agent** using the `DroidAgent` class. 

### Key Components:
- **`run-agent` Endpoint:** Receives the audit category (e.g., SMS) and starts the Droidrun task.
- **Autonomous Goals:** The agent is instructed to:
    1. Search for 'Permission Manager'.
    2. Validate the screen context.
    3. Filter out 'Not Allowed' apps to focus purely on active threats.
    4. Return to the Fortress AI app using `open_app()`.
- **Structured Output:** Uses LLM-based reasoning to classify app risks into a JSON report.

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Frameworks:** Droidrun, Flask
- **Communication:** Ngrok (for local-to-mobile tunneling)

## 🚀 Setup Instructions
1. **Install Dependencies:**
   ```bash
   pip install droidrun flask
