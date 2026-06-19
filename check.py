# # # # # # # from flask import Flask, jsonify, request
# # # # # # # from pydantic import BaseModel, Field
# # # # # # # from typing import List
# # # # # # # from droidrun import DroidAgent, DroidrunConfig
# # # # # # # import asyncio

# # # # # # # app = Flask(__name__)
# # # # # # # latest_result = {"status": "no_data"}

# # # # # # # class AppAudit(BaseModel):
# # # # # # #     app_name: str = Field(description="Name of the application")
# # # # # # #     permission_state: str = Field(description="Android state: 'Always', 'While using app', or 'Ask every time'")
# # # # # # #     risk_level: str = Field(description="Classification: 'Safe', 'Normal', or 'Risky'")
# # # # # # #     reason: str = Field(description="Why this risk level was assigned")

# # # # # # # class SecurityReport(BaseModel):
# # # # # # #     category: str = Field(description="Audited category (e.g., Camera)")
# # # # # # #     apps: List[AppAudit] = Field(description="List of all allowed apps found")
# # # # # # #     summary: str = Field(description="Overall safety conclusion")

# # # # # # # AUDIT_GOALS = {
# # # # # # #     "camera": """Act as Fortress AI Security Auditor.
# # # # # # #     1. NAVIGATE: Open Settings. Use the search bar to find and enter 'Permission manager'.
# # # # # # #     2. VERIFY MANAGER: Confirm the screen header is 'Permission manager' and shows a list of permission types.
# # # # # # #     3. SELECT: Find and tap 'Camera' to enter its global settings.
# # # # # # #     4. VALIDATE PERMISSION: Confirm the header now says 'Camera' or 'Camera permission'. If not, go back and correct.
# # # # # # #     5. INSPECT: Review ONLY the 'Allowed' sections. 
# # # # # # #     6. CLASSIFY: Group every allowed app based on its state:
# # # # # # #        - 'Always' -> Risk: 'Risky'.
# # # # # # #        - 'While using app' -> Risk: 'Normal'.
# # # # # # #        - 'Ask every time' -> Risk: 'Safe'.
# # # # # # #     7. SAFETY: Do NOT click any toggles, switches, or individual apps to change settings.
# # # # # # #     8. RETURN: Jump back instantly by calling open_app("droidsecurity").
# # # # # # #     9. REPORT: Use complete(success=True, reason="Findings: [List apps with state and risk]")""",

# # # # # # #     "microphone": """Act as Fortress AI Security Auditor.
# # # # # # #     1. NAVIGATE: Open Settings. Search for and enter 'Permission manager'.
# # # # # # #     2. VERIFY MANAGER: Ensure you are on the main 'Permission manager' screen.
# # # # # # #     3. SELECT: Find and tap 'Microphone'.
# # # # # # #     4. VALIDATE PERMISSION: Verify the header is 'Microphone' or 'Microphone permission'.
# # # # # # #     5. INSPECT: Review apps under 'Allowed' sections.
# # # # # # #     6. CLASSIFY: Map to Always (Risky), While using (Normal), or Ask (Safe).
# # # # # # #     7. SAFETY: Read-only mode. Do not modify any settings.
# # # # # # #     8. RETURN: Jump back instantly via open_app("droidsecurity").
# # # # # # #     9. REPORT: Use complete() with 'Findings:' in the reason field.""",

# # # # # # #     "location": """Act as Fortress AI Security Auditor.
# # # # # # #     1. NAVIGATE: Open Settings. Search and select 'Permission manager'.
# # # # # # #     2. VERIFY MANAGER: Confirm you see the full list of system permissions.
# # # # # # #     3. SELECT: Tap 'Location'.
# # # # # # #     4. VALIDATE PERMISSION: Ensure the header specifically says 'Location'.
# # # # # # #     5. CLASSIFY: Group apps by Always, While using app, and Ask every time.
# # # # # # #     6. SAFETY: Do not change any toggles.
# # # # # # #     7. RETURN: Call open_app("droidsecurity") to finish.
# # # # # # #     8. REPORT: Use complete() and list Findings (App, State, Risk) in the final reason.""",

# # # # # # #     "sms": """Act as Fortress AI Security Auditor.
# # # # # # #     1. NAVIGATE: Open Settings. Search and select 'Permission manager'.
# # # # # # #     2. VERIFY MANAGER: Confirm the 'Permission manager' screen is active.
# # # # # # #     3. SELECT: Tap 'SMS'.
# # # # # # #     4. VALIDATE PERMISSION: Verify the header is 'SMS' or 'SMS permission'.
# # # # # # #     5. INSPECT: Review the 'Allowed' list carefully. Mark non-messaging apps as 'Risky'.
# # # # # # #     6. SAFETY: Do not modify any permissions.
# # # # # # #     7. RETURN: Jump back by calling open_app("droidsecurity").
# # # # # # #     8. REPORT: Use complete() with Findings in the reason."""
# # # # # # # }

# # # # # # # @app.route('/run-agent', methods=['GET'])
# # # # # # # def run_agent():
# # # # # # #     global latest_result
# # # # # # #     category = request.args.get('category', 'camera').lower()
# # # # # # #     goal = AUDIT_GOALS.get(category, AUDIT_GOALS['camera'])
    
# # # # # # #     latest_result = {"status": "processing", "category": category}

# # # # # # #     try:
# # # # # # #         async def execute():
# # # # # # #             config = DroidrunConfig()
# # # # # # #             # 2. Pass the SecurityReport model to the agent
# # # # # # #             agent = DroidAgent(
# # # # # # #                 goal=goal, 
# # # # # # #                 config=config, 
# # # # # # #                 output_model=SecurityReport
# # # # # # #             )
# # # # # # #             return await agent.run()
        
# # # # # # #         result = asyncio.run(execute())
        
# # # # # # #         # 3. Access result.structured_output (this is a Pydantic object)
# # # # # # #         report = result.structured_output
        
# # # # # # #         if report:
# # # # # # #             latest_result = {
# # # # # # #                 "status": "success",
# # # # # # #                 "category": report.category,
# # # # # # #                 # Convert Pydantic object to a dictionary for JSON
# # # # # # #                 "data": report.model_dump(),
# # # # # # #                 "steps": result.steps if isinstance(result.steps, list) else []
# # # # # # #             }
# # # # # # #         else:
# # # # # # #             # Fallback if extraction failed
# # # # # # #             latest_result = {"status": "error", "reason": "Failed to extract structured data."}
            
# # # # # # #         return jsonify(latest_result)
# # # # # # #     except Exception as e:
# # # # # # #         latest_result = {"status": "error", "reason": str(e)}
# # # # # # #         return jsonify(latest_result), 500

# # # # # # # @app.route('/get-latest', methods=['GET'])
# # # # # # # def get_latest():
# # # # # # #     return jsonify(latest_result)

# # # # # # # if __name__ == "__main__":
# # # # # # #     app.run(host='0.0.0.0', port=5000)


from flask import Flask, jsonify, request
from pydantic import BaseModel, Field
from typing import List
import asyncio
import json
import re
from droidrun import DroidAgent, DroidrunConfig

app = Flask(__name__)
latest_result = {"status": "no_data"}

# --- MODELS FOR STRUCTURED OUTPUT ---
class AppAudit(BaseModel):
    app_name: str = Field(description="Name of the app")
    risk_level: str = Field(description="Classification: 'Safe', 'Normal', or 'Risky'")
    reason: str = Field(description="Why this risk level was assigned")

class SecurityReport(BaseModel):
    category: str = Field(description="Audited category (e.g., Camera)")
    apps: List[AppAudit] = Field(description="List of allowed apps found")
    summary: str = Field(description="Overall safety conclusion")

# --- ENHANCED AUDIT PROMPT ---
AUDIT_GOAL_TEMPLATE = """Act as Fortress AI Sentinel. 
1. Open 'Settings' > Search for 'Permission manager'.
2. Tap and open permission manager(control app access to your data) > Tap '{category}'. 
3. Review ONLY the 'Allowed' sections (scroll upto not allowded section). 
4. Categorize them: 'Always' access is 'Risky', 'While using' is 'Normal', 'Ask every time' is 'Safe' also put some of your reasoning, and can change the criteria if needed.
5. Do NOT change anything yet.
6. First go back once and then Return to 'DroidSecurity' app using the app opening command if possible and complete task."""

# --- THE "JUDGE-KILLER" FIX PROMPT ---
FIX_GOAL_TEMPLATE = """Act as Fortress AI Sentinel.
1. Open 'Settings' > 'Permission manager' (Search for it if needed).
2. Tap and open permission manager(control app access to your data) > Tap '{permission}'. 
3. Find '{app_name}' and tap it.
4. Select 'Don't allow or ask every time according to the apps usecase'.
5. Verify the selection changed.
6. First go back once and Return to 'DroidSecurity' app using the app opening command if possible and call complete(success=True).
7. GOAL: Revoke {permission} access for '{app_name}'."""

@app.route('/run-agent', methods=['GET'])
def run_agent():
    global latest_result
    category = request.args.get('category', 'camera').lower()
    latest_result = {"status": "processing", "category": category}
    
    async def execute():
        agent = DroidAgent(
            goal=AUDIT_GOAL_TEMPLATE.format(category=category),
            config=DroidrunConfig(),
            output_model=SecurityReport
        )
        return await agent.run()

    try:
        result = asyncio.run(execute())
        latest_result = {
            "status": "success",
            "category": category,
            "data": result.structured_output.model_dump()
        }
        return jsonify(latest_result)
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500

@app.route('/fix-permission', methods=['POST'])
def fix_permission():
    data = request.json
    app_name = data.get('app_name')
    permission = data.get('permission')

    async def execute_fix():
        agent = DroidAgent(
            goal=FIX_GOAL_TEMPLATE.format(app_name=app_name, permission=permission),
            config=DroidrunConfig()
        )
        return await agent.run()

    try:
        asyncio.run(execute_fix())
        return jsonify({"status": "success", "message": f"Revoked {permission} for {app_name}"})
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500

@app.route('/get-latest', methods=['GET'])
def get_latest():
    return jsonify(latest_result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)



# import os
# import time
# import json
# from flask import Flask, jsonify, request
# from mobilerun import Mobilerun

# app = Flask(__name__)
# latest_result = {"status": "no_data"}

# # --- CONFIG ---
# API_KEY = "dr_sk_agqNcnlmCfPSuethZPYcZBtPCsTRsKIKiKQlJfkGyTPdvhgCVIOIeBqkhjLYRgWE"
# DEVICE_ID = "5f99a257-0758-485d-a82f-2f5d17f69706" 
# LLM_MODEL = "google/gemini-3-flash"

# client = Mobilerun(api_key=API_KEY)

# # --- THE STRUCTURED OUTPUT SCHEMA ---
# REPORT_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "category": {"type": "string"},
#         "apps": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "app_name": {"type": "string"},
#                     "risk_level": {"type": "string", "enum": ["Safe", "Normal", "Risky"]},
#                     "reason": {"type": "string"}
#                 },
#                 "required": ["app_name", "risk_level", "reason"]
#             }
#         },
#         "summary": {"type": "string"}
#     },
#     "required": ["category", "apps", "summary"]
# }

# def wait_for_completion(task_id):
#     """Implementation using Mobilerun's suggested get_status/retrieve pattern."""
#     print(f"🚀 Monitoring task {task_id}")
    
#     # 1. Polling loop using get_status
#     while True:
#         print("⏳ Checking status...")
#         status = client.tasks.get_status(task_id) # Official status check method

#         if status in ['completed', 'failed', 'cancelled']:
#             print(f"✅ Task finished with status: {status}")
#             break
            
#         time.sleep(2) # Suggested wait time

#     # 2. Retrieve the full task object once finished
#     task_detail = client.tasks.retrieve(task_id)
#     return task_detail

# @app.route('/run-agent', methods=['GET'])
# def run_agent():
#     global latest_result
#     category = request.args.get('category', 'camera').lower()
#     latest_result = {"status": "processing", "category": category}

#     # Sentinel Prompt
#     goal = f"""Act as Fortress AI Sentinel. 
#     1. Open Settings and Search for 'Permission manager'.
#     2. Go to '{category}' and review 'Allowed' apps.
#     3. Categorize: 'Always'->Risky, 'While using'->Normal, 'Ask every time'->Safe.
#     4. Provide the result in the requested JSON format and finish."""

#     try:
#         # Start the task with the schema
#         task_run = client.tasks.run(
#             llm_model=LLM_MODEL,
#             task=goal,
#             device_id=DEVICE_ID,
#             output_schema=REPORT_SCHEMA # Keep this to ensure JSON output
#         )

#         # Wait using the official pattern
#         task_result = wait_for_completion(task_run.id)

#         if task_result.succeeded:
#             latest_result = {
#                 "status": "success",
#                 "category": category,
#                 "data": task_result.output # Structured data lives here
#             }
#         else:
#             latest_result = {"status": "error", "reason": "Task failed to succeed"}

#         return jsonify(latest_result)

#     except Exception as e:
#         latest_result = {"status": "error", "reason": str(e)}
#         return jsonify(latest_result), 500

# @app.route('/get-latest', methods=['GET'])
# def get_latest():
#     return jsonify(latest_result)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000)