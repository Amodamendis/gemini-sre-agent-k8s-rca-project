import time
import logging
import json
from k8s_client import K8sClient
from telemetry import PrometheusClient
from llm_engine import SREAgentBrain

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting AI SRE Agent...")
    
    k8s = K8sClient()
    prom = PrometheusClient()
    brain = SREAgentBrain()
    
    target_namespace = "bait-app"
    label_selector = "app=chaos-bait-app"
    job_name = "chaos-bait-app-monitor"
    
    # NEW: State flag to prevent API spamming
    anomaly_already_reported = False 

    while True:
        logger.info("Scanning Cluster Telemetry...")
        
        logs = k8s.get_pod_logs(target_namespace, label_selector, tail_lines=20)
        events = k8s.get_warning_events(target_namespace)
        cpu_rate = prom.get_cpu_spike(job_name)
        
        metrics = {"cpu_rate": cpu_rate}
        
        try:
            cpu_val = float(cpu_rate)
        except ValueError:
            cpu_val = 0.0

        # Check if cluster is currently failing
        is_anomalous = "Error" in logs or "Exception" in logs or "Timeout" in logs or cpu_val > 0.5 or events != "No warning events."

        # Only call Gemini if it is broken AND we haven't already reported it
        if is_anomalous and not anomaly_already_reported:
            logger.warning("Anomaly detected! Engaging Gemini AI for RCA...")
            rca_json_str = brain.analyze_telemetry(logs, events, metrics)
            
            try:
                rca_data = json.loads(rca_json_str)
                logger.info("\n=== AI ROOT CAUSE ANALYSIS REPORT ===")
                print(json.dumps(rca_data, indent=2))
                logger.info("=====================================\n")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI output: {rca_json_str}")
            
            # Set flag to True so we don't spam the API on the next 15s loop
            anomaly_already_reported = True 
            
        elif not is_anomalous:
            # If the logs clear up and the cluster is healthy, reset the flag
            anomaly_already_reported = False
            
        time.sleep(15)

if __name__ == "__main__":
    main()