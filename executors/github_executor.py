import aiohttp

class GitHubExecution:
    def __init__(self, access_token: str):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.inertia-preview+json",
        }

    async def prepare(self, task_data: dict) -> dict:
        """Prepare API request details based on the task."""
        action = task_data.get("action")
        params = task_data.get("params", {})
        
        actions = {
            "update_project": {
                "url": f"{self.base_url}/projects/{params.get('project_id')}",
                "method": "PATCH",
                "payload": {
                    "name": params.get("name"),
                    "body": params.get("body"),
                    "state": params.get("state", "open"),
                },
            },
            "create_project_column": {
                "url": f"{self.base_url}/projects/{params.get('project_id')}/columns",
                "method": "POST",
                "payload": {"name": params.get("name")},
            },
            "create_project_card": {
                "url": f"{self.base_url}/projects/columns/{params.get('column_id')}/cards",
                "method": "POST",
                "payload": {"note": params.get("note")},
            },
        }

        if action not in actions:
            raise ValueError(f"Unsupported action: {action}")
        
        return actions[action]

    async def execute(self, prepared_data: dict) -> dict:
        """Execute the API request."""
        async with aiohttp.ClientSession() as session:
            try:
                method = prepared_data["method"]
                url = prepared_data["url"]
                payload = prepared_data.get("payload", {})

                async with getattr(session, method.lower())(url, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    return {"status": "success", "data": await response.json()}
            except aiohttp.ClientError as e:
                return {"status": "error", "message": str(e)}

    async def report(self, result: dict) -> dict:
        """Report the outcome of the task."""
        if result["status"] == "success":
            logging.info("Action completed successfully.")
        else:
            logging.error(f"Action failed: {result.get('message')}")
        return result

    async def run(self, task_data: dict) -> dict:
        """End-to-end execution: Prepare -> Execute -> Report."""
        prepared_data = await self.prepare(task_data)
        execution_result = await self.execute(prepared_data)
        return await self.report(execution_result)
