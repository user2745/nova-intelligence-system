# nova_core.py
from rx import operators as ops
from .core_identity import CoreIdentity  # Fixed import
from .emotional_model import EmotionalPhysics  # Fixed import
from .autonomous_engine import AutonomyEngine  # Fixed import
from .llm_mafia import DeepThinkMafia  # Add missing import
from .intent_processing_engine import IntentProcessingEngine
import logging
import time

logging.basicConfig(level=logging.INFO)

class NovaCore:
    def __init__(self, ucp):
        self.ucp = ucp
        self.identity = CoreIdentity()
        self.emotions = EmotionalPhysics(self.ucp, self.identity)
        self.autonomy = AutonomyEngine(self.identity)
        self.llm = DeepThinkMafia(self.ucp, self.identity)
        self.metrics = {
            "response_times": [],
            "success_rate": 0,
            "total_requests": 0,
            "failed_requests": 0
        }
        self.warning_thresholds = {
            'cpu': 80.0,  # Warn if CPU > 80%
            'memory': 90.0,  # Warn if Memory > 90%
            'disk': 95.0,  # Warn if Disk > 95%
            'balance': 0.0001,  # Warn if balance < 0.0001 ETH
        }

        # Subscribe to context updates
        # Decision loop
        self.ucp.context_stream.pipe(
            ops.throttle_first(1)
        ).subscribe(self._process_context)

    def _process_state_update(self, state):
        """Ensure all devices receive and apply the state update instantly."""
        print(f"🚀 [STATE UPDATE] on {self.ucp.ucp_client.device_id}: {state}")

        # Store the last state (to detect changes)
        last_state = getattr(self, "_last_state", {})

        # Prevent recursive re-emission by checking if the state actually changed
        if state != last_state:
            self.ucp.emit_state(state)  # Publish updated state to all connected devices

        # Update local state tracking
        self._last_state = state

    def _process_context(self, context):
        """Process context updates with proper thresholds and debouncing"""
        try:
            warnings = []
            
            # Check system resources
            sys = context.get('system', {})
            if sys.get('cpu_usage', 0) > self.warning_thresholds['cpu']:
                warnings.append(f"High CPU usage: {sys.get('cpu_usage')}%")
            if sys.get('memory_usage', 0) > self.warning_thresholds['memory']:
                warnings.append(f"High Memory usage: {sys.get('memory_usage')}%")
            if sys.get('disk_usage', 0) > self.warning_thresholds['disk']:
                warnings.append(f"High Disk usage: {sys.get('disk_usage')}%")
                
            # Check wallet with proper number comparison
            wallet = context.get('wallet', {})
            balance = wallet.get('balance', 0)
            if isinstance(balance, (int, float)) and balance < self.warning_thresholds['balance']:
                warnings.append(f"Low balance: {balance} ETH")
                
            # Only emit response if there are actual warnings and they're different from last time
            if warnings and warnings != getattr(self, '_last_warnings', None):
                self._last_warnings = warnings
                warning_msg = "🚨 [WARNING] System Alert:\n"
                warning_msg += "\n".join(warnings)
                self.ucp.emit_response(warning_msg)
                
                self.ucp.emit_intent({
                    "intent": "ResourceAlert",
                    "parameters": {
                        "warnings": warnings,
                        "severity": "high" if len(warnings) > 1 else "medium"
                    }
                })
                
        except Exception as e:
            print(f"Error processing context: {e}")

    def _build_warning_prompt(self, context):
        return f"""
        [Warning Context]
        - CPU: {context.get('system', {}).get('cpu_usage', 0)}%
        - Balance: {context.get('wallet', {}).get('balance', 0)} ETH
        - Gas Fee: {context.get('gas_fee', 'unknown')}
        [Action Request]
        Compose urgent warning about these conditions
        """

    def _calculate_reward(self, action, context):
        """Simplified reward function with safe context access"""
        try:
            wallet = context.get('wallet', {})
            if action == 'speak_warning' and wallet.get('balance', 0) < 0.1:
                return 1.0  # Good catch
            elif action == 'execute_transaction' and wallet.get('gas_fee', 0) > 100:
                return -0.5  # Bad timing
            return 0.0
        except Exception as e:
            print(f"Warning: Error calculating reward: {e}")
            return 0.0  # Default reward on error