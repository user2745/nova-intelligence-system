import asyncio
import os
import psutil
import logging
import subprocess

class NetworkWatchdog:
    """Monitors active network connections for suspicious activity."""
    def __init__(self, queue):
        self.queue = queue
        asyncio.create_task(self._monitor_network())

    async def _monitor_network(self):
        while True:
            try:
                connections = psutil.net_connections(kind='inet')
                active_conns = [c for c in connections if c.status == 'ESTABLISHED']
                
                # Simple anomaly detection: Too many connections?
                if len(active_conns) > 50:
                    alert = {
                        "type": "security_alert",
                        "severity": "medium",
                        "message": f"High network activity detected: {len(active_conns)} active connections."
                    }
                    await self.queue.enqueue(alert)
                    logging.warning(f"[NetworkWatchdog] {alert['message']}")
                
                # Log stats occasionally
                net_stats = {
                    "type": "network_stats",
                    "active_connections": len(active_conns),
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
                await self.queue.enqueue(net_stats)
                
            except Exception as e:
                logging.error(f"[NetworkWatchdog] Error: {e}")
                
            await asyncio.sleep(10)

class SystemSnitch:
    def __init__(self, queue):
        # Emit system stats every 2 seconds
        self.queue = queue
        
        # Initialize sub-modules
        self.network_watchdog = NetworkWatchdog(queue)
        
        asyncio.create_task(self._snitch_loop())

    async def _snitch_loop(self):
        process = psutil.Process(os.getpid())
        while True:
            system = {
                "type": "system_stats",
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "my_cpu_usage": process.cpu_percent(interval=1),
                "my_memory_usage": process.memory_percent(),
                }
            await self.queue.enqueue(system)
            await asyncio.sleep(5)

