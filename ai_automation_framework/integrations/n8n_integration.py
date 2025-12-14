"""n8n workflow integration."""

import requests
from typing import Dict, Any, List, Optional
import json


class N8NIntegration:
    """
    n8n workflow automation integration.

    n8n is an open-source workflow automation tool that can be self-hosted.
    This integration allows triggering n8n workflows from the framework.
    """

    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize n8n integration.

        Args:
            base_url: n8n instance URL (e.g., "https://n8n.yourdomain.com")
            api_key: n8n API key
        """
        self.base_url = base_url
        self.api_key = api_key

    def trigger_webhook(
        self,
        webhook_path: str,
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Trigger n8n webhook.

        Args:
            webhook_path: Webhook path (e.g., "/webhook/my-workflow")
            data: Data to send
            method: HTTP method

        Returns:
            Result dictionary

        Example:
            >>> n8n = N8NIntegration("https://n8n.example.com")
            >>> result = n8n.trigger_webhook("/webhook/process-data", {"key": "value"})
        """
        try:
            url = f"{self.base_url}{webhook_path}"

            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['X-N8N-API-KEY'] = self.api_key

            response = requests.request(
                method=method.upper(),
                url=url,
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.text else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_workflows(self) -> Dict[str, Any]:
        """Get list of workflows from n8n."""
        try:
            url = f"{self.base_url}/api/v1/workflows"
            headers = {}

            if self.api_key:
                headers['X-N8N-API-KEY'] = self.api_key

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "workflows": response.json()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a workflow directly via API."""
        try:
            url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
            headers = {'Content-Type': 'application/json'}

            if self.api_key:
                headers['X-N8N-API-KEY'] = self.api_key

            payload = {"data": data} if data else {}

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "execution_id": response.json().get('id'),
                "result": response.json()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_workflow_template(self, name: str) -> Dict[str, Any]:
        """
        Generate n8n workflow template as JSON.

        Args:
            name: Workflow name

        Returns:
            Workflow template

        Example:
            Use this template to import into n8n
        """
        template = {
            "name": name,
            "nodes": [
                {
                    "parameters": {},
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                    "webhookId": "auto-generated"
                },
                {
                    "parameters": {
                        "functionCode": "// Process webhook data\nreturn items;"
                    },
                    "name": "Function",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [450, 300]
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Function", "type": "main", "index": 0}]]
                }
            },
            "active": True,
            "settings": {},
            "tags": []
        }

        return {
            "success": True,
            "template": template,
            "usage": "Import this JSON into n8n to create the workflow"
        }


# Example n8n workflow use cases:
"""
Example n8n Workflows:

1. Data Processing Pipeline:
   - Webhook Trigger → Function Node → HTTP Request → Database Insert

2. Email Processing:
   - Webhook → Extract Data → Send Email → Log to Sheet

3. Multi-Service Integration:
   - Webhook → Split in Batches → [API Call, Database Update, Notification]

4. Scheduled Data Sync:
   - Cron Trigger → Fetch API → Transform Data → Update Database

5. Conditional Routing:
   - Webhook → If/Switch → Route to Different Actions
"""
