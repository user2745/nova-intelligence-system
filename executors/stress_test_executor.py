import asyncio

class StressTestModule:
    """
    Module to execute the 'stress' command for testing.
    """
    @staticmethod
    async def run(task_data):
        try:
            # Extract parameters from task_data
            cpu_load = task_data.get("cpu", 1)
            timeout = task_data.get("timeout", 10)

            # Build the stress command
            command = f"stress --cpu {cpu_load} --timeout {timeout}"
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Capture output
            stdout, stderr = await process.communicate()
            return {
                "status": "success" if process.returncode == 0 else "error",
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
