import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class K8sClient:
    def __init__(self):
        try:
            # Authenticate using the Pod's injected ServiceAccount token
            config.load_incluster_config()
            self.v1 = client.CoreV1Api()
            self.events_v1 = client.EventsV1Api()
            logger.info("Successfully loaded in-cluster Kubernetes config.")
        except Exception as e:
            logger.error(f"Failed to load K8s config. Error: {e}")
            raise

    def get_pod_logs(self, namespace, label_selector, tail_lines=50):
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
            if not pods.items:
                return "No pods found matching the selector."
            
            pod_name = pods.items[0].metadata.name
            logs = self.v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=tail_lines)
            return logs
        except ApiException as e:
            logger.error(f"Error fetching logs: {e}")
            return str(e)

    def get_warning_events(self, namespace):
        try:
            events = self.v1.list_namespaced_event(namespace=namespace)
            warnings = [
                f"{e.involved_object.kind} {e.involved_object.name}: {e.message}"
                for e in events.items if e.type == "Warning"
            ]
            return "\n".join(warnings) if warnings else "No warning events."
        except ApiException as e:
            logger.error(f"Error fetching events: {e}")
            return str(e)