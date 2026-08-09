import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class SREAgentBrain:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing")
        
        self.client = genai.Client()
        self.model = "gemini-2.5-flash" # Ideal for fast, structured reasoning

        self.system_instruction = """
You are a Senior Kubernetes Site Reliability Engineer (SRE). 
Your task is to analyze telemetry data (Metrics, Logs, and Events) and provide a Root Cause Analysis.

You MUST respond strictly in valid JSON format matching the following schema.
{
  "timestamp": "ISO8601 string",
  "detected_anomaly": "Brief description of what went wrong",
  "root_cause_analysis": "Detailed explanation of the root cause based on telemetry",
  "confidence_score": "Percentage from 0-100%",
  "remediation_kubectl_commands": ["list of commands to fix or investigate"]
}
"""

    def analyze_telemetry(self, logs, events, metrics):
        prompt = f"""
Analyze the following Kubernetes telemetry:

=== APPLICATION LOGS ===
{logs}

=== KUBERNETES WARNING EVENTS ===
{events}

=== PROMETHEUS METRICS ===
CPU Usage Rate (1m): {metrics.get('cpu_rate')}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2, 
                    response_mime_type="application/json" # Forces strict JSON output
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return json.dumps({"error": str(e)})