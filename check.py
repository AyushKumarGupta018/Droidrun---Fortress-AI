from flask import Flask, jsonify, request
from pydantic import BaseModel, Field
from typing import List
from droidrun import DroidAgent, DroidrunConfig
import asyncio

app = Flask(__name__)
latest_result = {"status": "no_data"}

class AppAudit(BaseModel):
    app_name: str = Field(description="Name of the application")
    permission_state: str = Field(description="Android state: 'Always', 'While using app', or 'Ask every time'")
    risk_level: str = Field(description="Classification: 'Safe', 'Normal', or 'Risky'")
    reason: str = Field(description="Why this risk level was assigned")

class SecurityReport(BaseModel):
    category: str = Field(description="Audited category (e.g., Camera)")
    apps: List[AppAudit] = Field(description="List of all allowed apps found")
    summary: str = Field(description="Overall safety conclusion")


AUDIT_GOALS = {
    "camera": """Act as Fortress AI Security Auditor.
    1. NAVIGATE: Open Settings. Use the search bar to find and enter 'Permission manager'.
    2. VERIFY MANAGER: Confirm the screen header is 'Permission manager' and shows a list of permission types.
    3. SELECT: Find and tap 'Camera' to enter its global settings.
    4. VALIDATE PERMISSION: Confirm the header now says 'Camera' or 'Camera permission'. If not, go back and correct.
    5. INSPECT: Review ONLY the 'Allowed' sections. 
    6. CLASSIFY: Group every allowed app based on its state:
       - 'Always' -> Risk: 'Risky'.
       - 'While using app' -> Risk: 'Normal'.
       - 'Ask every time' -> Risk: 'Safe'.
    7. SAFETY: Do NOT click any toggles, switches, or individual apps to change settings.
    8. RETURN: Jump back instantly by calling open_app("droidsecurity").
    9. REPORT: Use complete(success=True, reason="Findings: [List apps with state and risk]")""",

    "microphone": """Act as Fortress AI Security Auditor.
    1. NAVIGATE: Open Settings. Search for and enter 'Permission manager'.
    2. VERIFY MANAGER: Ensure you are on the main 'Permission manager' screen.
    3. SELECT: Find and tap 'Microphone'.
    4. VALIDATE PERMISSION: Verify the header is 'Microphone' or 'Microphone permission'.
    5. INSPECT: Review apps under 'Allowed' sections.
    6. CLASSIFY: Map to Always (Risky), While using (Normal), or Ask (Safe).
    7. SAFETY: Read-only mode. Do not modify any settings.
    8. RETURN: Jump back instantly via open_app("droidsecurity").
    9. REPORT: Use complete() with 'Findings:' in the reason field.""",

    "location": """Act as Fortress AI Security Auditor.
    1. NAVIGATE: Open Settings. Search and select 'Permission manager'.
    2. VERIFY MANAGER: Confirm you see the full list of system permissions.
    3. SELECT: Tap 'Location'.
    4. VALIDATE PERMISSION: Ensure the header specifically says 'Location'.
    5. CLASSIFY: Group apps by Always, While using app, and Ask every time.
    6. SAFETY: Do not change any toggles.
    7. RETURN: Call open_app("droidsecurity") to finish.
    8. REPORT: Use complete() and list Findings (App, State, Risk) in the final reason.""",

    "sms": """Act as Fortress AI Security Auditor.
    1. NAVIGATE: Open Settings. Search and select 'Permission manager'.
    2. VERIFY MANAGER: Confirm the 'Permission manager' screen is active.
    3. SELECT: Tap 'SMS'.
    4. VALIDATE PERMISSION: Verify the header is 'SMS' or 'SMS permission'.
    5. INSPECT: Review the 'Allowed' list carefully. Mark non-messaging apps as 'Risky'.
    6. SAFETY: Do not modify any permissions.
    7. RETURN: Jump back by calling open_app("droidsecurity").
    8. REPORT: Use complete() with Findings in the reason."""
}

@app.route('/run-agent', methods=['GET'])
def run_agent():
    global latest_result
    category = request.args.get('category', 'camera').lower()
    goal = AUDIT_GOALS.get(category, AUDIT_GOALS['camera'])
    
    latest_result = {"status": "processing", "category": category}

    try:
        async def execute():
            config = DroidrunConfig()
            # 2. Pass the SecurityReport model to the agent
            agent = DroidAgent(
                goal=goal, 
                config=config, 
                output_model=SecurityReport
            )
            return await agent.run()
        
        result = asyncio.run(execute())
        
        # 3. Access result.structured_output (this is a Pydantic object)
        report = result.structured_output
        
        if report:
            latest_result = {
                "status": "success",
                "category": report.category,
                # Convert Pydantic object to a dictionary for JSON
                "data": report.model_dump(),
                "steps": result.steps if isinstance(result.steps, list) else []
            }
        else:
            # Fallback if extraction failed
            latest_result = {"status": "error", "reason": "Failed to extract structured data."}
            
        return jsonify(latest_result)
    except Exception as e:
        latest_result = {"status": "error", "reason": str(e)}
        return jsonify(latest_result), 500

@app.route('/get-latest', methods=['GET'])
def get_latest():
    return jsonify(latest_result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
