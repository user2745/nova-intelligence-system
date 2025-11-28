import asyncio
import logging
import subprocess
from .actuator_manager import Actuator

class NetworkActuator(Actuator):
    """
    Actuator for network and system operations.
    Capable of blocking IPs, killing processes, and scanning ports.
    """
    def __init__(self):
        super().__init__("network")
        self.register_tool("block_ip", self.block_ip, "Block an IP address using iptables")
        self.register_tool("kill_process", self.kill_process, "Terminate a process by PID")
        self.register_tool("get_active_connections", self.get_active_connections, "Get list of active network connections")
        self.register_tool("monitor_network_activity", self.monitor_network_activity, "Summarize current network connections and activity")
        self.register_tool("check_integrity", self.check_integrity, "Run basic system and network integrity checks")

    async def block_ip(self, ip_address: str) -> str:
        """
        Block an IP address using iptables.
        Requires root privileges.
        """
        logging.warning(f"[NetworkActuator] 🛡️ ATTEMPTING TO BLOCK IP: {ip_address}")
        
        # Safety check: Don't block localhost
        if ip_address in ["127.0.0.1", "localhost", "::1"]:
            return "Error: Cannot block localhost."

        cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return f"Successfully blocked IP: {ip_address}"
            else:
                return f"Failed to block IP: {stderr.decode().strip()}"
        except Exception as e:
            return f"Error executing iptables: {str(e)}"

    async def kill_process(self, pid: int) -> str:
        """
        Terminate a process by PID.
        """
        logging.warning(f"[NetworkActuator] 💀 ATTEMPTING TO KILL PID: {pid}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                "kill", "-9", str(pid),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return f"Successfully killed PID: {pid}"
            else:
                return f"Failed to kill PID: {stderr.decode().strip()}"
        except Exception as e:
            return f"Error executing kill: {str(e)}"

    async def get_active_connections(self) -> str:
        """
        Get active connections using 'ss'.
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "ss", "-tunap",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode()
                # Return top 10 lines to avoid flooding context
                lines = output.split('\n')[:10]
                return "\n".join(lines)
            else:
                return f"Failed to get connections: {stderr.decode().strip()}"
        except Exception as e:
            return f"Error executing ss: {str(e)}"

    async def monitor_network_activity(self) -> str:
        """High-level wrapper around get_active_connections with a short summary."""
        raw = await self.get_active_connections()
        if raw.startswith("Error") or raw.startswith("Failed"):
            return raw

        lines = raw.split("\n")
        header = lines[0] if lines else ""
        connections = lines[1:]
        connection_count = max(len(connections), 0)
        preview = "\n".join(connections[:5])
        summary = (
            f"Active network connections: {connection_count}.\n"
            f"Header: {header}\n"
            f"Sample connections:\n{preview}"
        )
        return summary

    async def check_integrity(self) -> str:
        """Run lightweight integrity checks (uptime and failed SSH logins)."""
        results = []

        # Uptime
        try:
            proc = await asyncio.create_subprocess_exec(
                "uptime",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                results.append(f"Uptime: {stdout.decode().strip()}")
            else:
                results.append(f"Uptime check failed: {stderr.decode().strip()}")
        except Exception as e:
            results.append(f"Uptime check error: {str(e)}")

        # Failed SSH logins (if journalctl available)
        try:
            proc = await asyncio.create_subprocess_exec(
                "journalctl",
                "-n",
                "50",
                "-u",
                "ssh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                text = stdout.decode(errors="ignore")
                failed = [
                    line for line in text.split("\n")
                    if "Failed password" in line or "authentication failure" in line
                ]
                results.append(f"Recent failed SSH logins: {len(failed)}")
            else:
                results.append(f"SSH log check failed: {stderr.decode().strip()}")
        except FileNotFoundError:
            results.append("SSH journal not available (journalctl missing or no ssh unit).")
        except Exception as e:
            results.append(f"SSH log check error: {str(e)}")

        return "\n".join(results)
