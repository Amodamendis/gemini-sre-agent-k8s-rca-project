import requests
import logging

logger = logging.getLogger(__name__)

class PrometheusClient:
    def __init__(self):
        # The internal DNS name of the Prometheus service in your cluster
        self.base_url = "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"

    def query_metric(self, query):
        try:
            response = requests.get(f"{self.base_url}/api/v1/query", params={'query': query}, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success' and data['data']['result']:
                return data['data']['result'][0]['value'][1]
            return "0"
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
            return "0"

    def get_cpu_spike(self, job_name):
        query = f'rate(process_cpu_seconds_total{{job="{job_name}"}}[1m])'
        return self.query_metric(query)