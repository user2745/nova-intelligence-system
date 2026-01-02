import logging
import os
import subprocess
import shutil
from datetime import datetime
from typing import Any

from .actuator_manager import Actuator


class SystemActuator(Actuator):
    """
    Actuator for system operations and script execution.
    Provides tools for:
    - OS navigation and file system exploration
    - Creating and executing bash scripts
    - Creating and executing python scripts
    - Running system commands
    """
    
    def __init__(self, memory_manager=None):
        super().__init__("system")
        self.memory_manager = memory_manager
        
        # Register all system tools
        self.register_tool("list_directory", self.list_directory, "List files and directories in a path")
        self.register_tool("read_file", self.read_file, "Read the contents of a file")
        self.register_tool("file_exists", self.file_exists, "Check if a file or directory exists")
        self.register_tool("create_bash_script", self.create_bash_script, "Create and save a bash script")
        self.register_tool("create_python_script", self.create_python_script, "Create and save a python script")
        self.register_tool("execute_bash", self.execute_bash, "Execute a bash command or script")
        self.register_tool("execute_python", self.execute_python, "Execute a python script")
        self.register_tool("get_system_info", self.get_system_info, "Get current working directory and environment info")

        # File System Mastery
        self.register_tool("write_file", self.write_file, "Write content to a file (overwrite)")
        self.register_tool("append_file", self.append_file, "Append content to a file")
        self.register_tool("delete_file", self.delete_file, "Delete a file")
        self.register_tool("move_file", self.move_file, "Move or rename a file")

        # Process Control
        self.register_tool("list_processes", self.list_processes, "List running processes")
        self.register_tool("kill_process", self.kill_process, "Kill a process by PID")

        # Git Integration
        self.register_tool("git_status", self.git_status, "Get git status")
        self.register_tool("git_diff", self.git_diff, "Get git diff")
        self.register_tool("git_commit", self.git_commit, "Commit changes to git")
        self.register_tool("git_push", self.git_push, "Push changes to remote")
        self.register_tool("git_pull", self.git_pull, "Pull changes from remote")
        self.register_tool("git_log", self.git_log, "Show git log")

        # Docker Integration
        self.register_tool("docker_ps", self.docker_ps, "List running docker containers")
        self.register_tool("docker_images", self.docker_images, "List docker images")
        self.register_tool("docker_stop", self.docker_stop, "Stop a docker container")
        self.register_tool("docker_logs", self.docker_logs, "Get logs from a docker container")
    
    async def list_directory(self, path: str) -> str:
        """List all files and directories in the given path."""
        try:
            expanded_path = os.path.expanduser(path)
            if not os.path.isdir(expanded_path):
                return f"Error: {path} is not a valid directory."
            
            items = []
            for item in sorted(os.listdir(expanded_path)):
                item_path = os.path.join(expanded_path, item)
                if os.path.isdir(item_path):
                    items.append(f"[DIR] {item}")
                else:
                    items.append(f"[FILE] {item}")
            
            result = "\n".join(items) if items else "Directory is empty."
            logging.info(f"[SystemActuator] Listed directory {path}: {len(items)} items")
            return result
        except Exception as e:
            logging.error(f"[SystemActuator] Error listing directory: {e}")
            return f"Error listing directory: {e}"
    
    async def read_file(self, path: str) -> str:
        """Read and return the contents of a file."""
        try:
            expanded_path = os.path.expanduser(path)
            if not os.path.isfile(expanded_path):
                return f"Error: {path} is not a valid file."
            
            with open(expanded_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limit output
            if len(content) > 10000:
                result = f"File is {len(content)} characters (truncated to first 10000):\n\n{content[:10000]}\n\n... (truncated)"
            else:
                result = content
            
            logging.info(f"[SystemActuator] Read file {path}: {len(content)} characters")
            return result
        except Exception as e:
            logging.error(f"[SystemActuator] Error reading file: {e}")
            return f"Error reading file: {e}"
    
    async def file_exists(self, path: str) -> str:
        """Check if a file or directory exists at the given path."""
        try:
            expanded_path = os.path.expanduser(path)
            exists = os.path.exists(expanded_path)
            is_file = os.path.isfile(expanded_path) if exists else False
            is_dir = os.path.isdir(expanded_path) if exists else False
            
            if not exists:
                result = f"Path does not exist: {path}"
            elif is_file:
                result = f"Path is a file: {path}"
            elif is_dir:
                result = f"Path is a directory: {path}"
            
            logging.info(f"[SystemActuator] Checked path {path}: {result}")
            return result
        except Exception as e:
            logging.error(f"[SystemActuator] Error checking path: {e}")
            return f"Error checking path: {e}"
    
    async def create_bash_script(self, filename: str, content: str) -> str:
        """Create a bash script with the given filename and content."""
        try:
            # Ensure shebang
            if not content.strip().startswith("#!"):
                content = "#!/bin/bash\n" + content
            
            filepath = os.path.expanduser(filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make executable
            os.chmod(filepath, 0o755)
            
            result = f"Bash script created successfully: {filepath}"
            logging.info(f"[SystemActuator] {result}")
            return result
        except Exception as e:
            logging.error(f"[SystemActuator] Error creating bash script: {e}")
            return f"Error creating bash script: {e}"
    
    async def create_python_script(self, filename: str, content: str) -> str:
        """Create a python script with the given filename and content."""
        try:
            # Ensure shebang
            if not content.strip().startswith("#!"):
                content = "#!/usr/bin/env python3\n" + content
            
            filepath = os.path.expanduser(filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make executable
            os.chmod(filepath, 0o755)
            
            result = f"Python script created successfully: {filepath}"
            logging.info(f"[SystemActuator] {result}")
            return result
        except Exception as e:
            logging.error(f"[SystemActuator] Error creating python script: {e}")
            return f"Error creating python script: {e}"
    
    async def execute_bash(self, command: str) -> str:
        """Execute a bash command or bash script and return the output."""
        try:
            logging.info(f"[SystemActuator] Executing bash: {command[:100]}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"
            
            if result.returncode != 0:
                output += f"\n[Return code: {result.returncode}]"
            
            # Limit output size
            if len(output) > 5000:
                return f"Output is {len(output)} characters (truncated to first 5000):\n\n{output[:5000]}\n\n... (truncated)"
            
            return output if output else "[Command executed with no output]"
        except subprocess.TimeoutExpired:
            logging.error(f"[SystemActuator] Bash command timed out")
            return "Error: Command execution timed out (30 seconds limit)."
        except Exception as e:
            logging.error(f"[SystemActuator] Error executing bash command: {e}")
            return f"Error executing bash command: {e}"
    
    async def execute_python(self, script_path: str) -> str:
        """Execute a python script and return the output."""
        try:
            expanded_path = os.path.expanduser(script_path)
            if not os.path.isfile(expanded_path):
                return f"Error: {script_path} is not a valid file."
            
            logging.info(f"[SystemActuator] Executing python script: {script_path}")
            result = subprocess.run(
                ["python3", expanded_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"
            
            if result.returncode != 0:
                output += f"\n[Return code: {result.returncode}]"
            
            # Limit output size
            if len(output) > 5000:
                return f"Output is {len(output)} characters (truncated to first 5000):\n\n{output[:5000]}\n\n... (truncated)"
            
            return output if output else "[Script executed with no output]"
        except subprocess.TimeoutExpired:
            logging.error(f"[SystemActuator] Python script execution timed out")
            return "Error: Script execution timed out (30 seconds limit)."
        except Exception as e:
            logging.error(f"[SystemActuator] Error executing python script: {e}")
            return f"Error executing python script: {e}"
    
    async def get_system_info(self) -> str:
        """Get current working directory and environment information."""
        try:
            cwd = os.getcwd()
            user = os.environ.get("USER", "unknown")
            home = os.path.expanduser("~")
            
            info = {
                "current_directory": cwd,
                "user": user,
                "home_directory": home,
                "hostname": os.environ.get("HOSTNAME", "unknown"),
                "shell": os.environ.get("SHELL", "unknown"),
            }
            
            logging.info(f"[SystemActuator] System info retrieved")
            return str(info)
        except Exception as e:
            logging.error(f"[SystemActuator] Error getting system info: {e}")
            return f"Error getting system info: {e}"

    # --- File System Mastery ---
    async def write_file(self, path: str, content: str) -> str:
        """Write content to a file (overwrites existing content)."""
        try:
            expanded_path = os.path.expanduser(path)
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"[SystemActuator] Wrote to file {path}")
            return f"Successfully wrote to {path}"
        except Exception as e:
            logging.error(f"[SystemActuator] Error writing file: {e}")
            return f"Error writing file: {e}"

    async def append_file(self, path: str, content: str) -> str:
        """Append content to a file."""
        try:
            expanded_path = os.path.expanduser(path)
            with open(expanded_path, 'a', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"[SystemActuator] Appended to file {path}")
            return f"Successfully appended to {path}"
        except Exception as e:
            logging.error(f"[SystemActuator] Error appending to file: {e}")
            return f"Error appending to file: {e}"

    async def delete_file(self, path: str) -> str:
        """Delete a file."""
        try:
            expanded_path = os.path.expanduser(path)
            if os.path.isfile(expanded_path):
                os.remove(expanded_path)
                logging.info(f"[SystemActuator] Deleted file {path}")
                return f"Successfully deleted {path}"
            else:
                return f"Error: {path} is not a file"
        except Exception as e:
            logging.error(f"[SystemActuator] Error deleting file: {e}")
            return f"Error deleting file: {e}"

    async def move_file(self, src: str, dest: str) -> str:
        """Move or rename a file."""
        try:
            expanded_src = os.path.expanduser(src)
            expanded_dest = os.path.expanduser(dest)
            shutil.move(expanded_src, expanded_dest)
            logging.info(f"[SystemActuator] Moved {src} to {dest}")
            return f"Successfully moved {src} to {dest}"
        except Exception as e:
            logging.error(f"[SystemActuator] Error moving file: {e}")
            return f"Error moving file: {e}"

    # --- Process Control ---
    async def list_processes(self) -> str:
        """List running processes (top 20 by CPU)."""
        try:
            cmd = "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 21"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error listing processes: {e}"

    async def kill_process(self, pid: int) -> str:
        """Kill a process by PID."""
        try:
            os.kill(int(pid), 9)
            return f"Successfully killed process {pid}"
        except Exception as e:
            return f"Error killing process {pid}: {e}"

    # --- Git Integration ---
    async def git_status(self) -> str:
        """Get git status."""
        return await self.execute_bash("git status")

    async def git_diff(self) -> str:
        """Get git diff."""
        return await self.execute_bash("git diff")

    async def git_commit(self, message: str) -> str:
        """Commit changes to git."""
        return await self.execute_bash(f'git commit -m "{message}"')

    async def git_push(self) -> str:
        """Push changes to remote."""
        return await self.execute_bash("git push")

    async def git_pull(self) -> str:
        """Pull changes from remote."""
        return await self.execute_bash("git pull")
    
    async def git_log(self) -> str:
        """Show git log."""
        return await self.execute_bash("git log -n 10 --oneline")

    # --- Docker Integration ---
    async def docker_ps(self) -> str:
        """List running docker containers."""
        return await self.execute_bash("docker ps")

    async def docker_images(self) -> str:
        """List docker images."""
        return await self.execute_bash("docker images")

    async def docker_stop(self, container_id: str) -> str:
        """Stop a docker container."""
        return await self.execute_bash(f"docker stop {container_id}")

    async def docker_logs(self, container_id: str) -> str:
        """Get logs from a docker container."""
        return await self.execute_bash(f"docker logs --tail 100 {container_id}")
