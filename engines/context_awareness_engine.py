import os
import psutil
import subprocess
from datetime import datetime

class SystemContextAwarenessEngine:
    """
    Gathers and processes context for the Nova system.
    """

    def gather_context(self):
        """
        Collects system stats and health diagnostics.
        """
        process = psutil.Process(os.getpid())
        context = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "gpu_usage": self.gpu_stats(),
            "my_cpu_usage": process.cpu_percent(interval=1),
            "my_memory_usage": process.memory_percent(),
        }
        return context

    def gpu_stats(self):
        """
        Fetches GPU stats if available.
        """
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,nounits,noheader"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return int(result.stdout.strip())
        except FileNotFoundError:
            print("nvidia-smi not found. Skipping GPU stats.")
            return 0
        except Exception as e:
            print(f"Error fetching GPU stats: {e}")
            return 0
