# ucp_response.py
import json
from ucp import UCPClient  # Your existing UCP client

class UCPResponseExecutor:
    def __init__(self, client):
        self.client = client
        self.client.connect()
    
    async def run(self, task_data):
        """Publish structured responses to UCP"""
        session_id, response_data = task_data["session_id"], task_data["response_data"] # Extract session ID and response data
        response_topic = f"ucl/chat/responses/{session_id}"
        try:
            await self.client.publish(
                response_topic,
                json.dumps({
                    "text": response_data.get("text", ""),
                    "actions": response_data.get("actions", []),
                    "context": response_data.get("context", {}),
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
            logging.info(f"Response published to {response_topic}")
            return {"status": "success", "message": "Response published"}
        except Exception as e:
            logging.error(f"Failed to publish response: {str(e)}")
            return {"status": "error", "message": str(e)}
