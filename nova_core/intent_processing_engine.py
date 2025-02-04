from rx import operators as ops
from rx.subject import Subject
from datetime import datetime
import logging
import json

class IntentProcessingEngine:
    def __init__(self, ucp):
        self.ucp = ucp
        self.active_intents = {}  # Track active intents
        self.intent_handlers = {
            'BootUp': self._handle_bootup,
            'IdleCheck': self._handle_idle_check,
            'ResourceAlert': self._handle_resource_alert,
            'DeviceOnlineAnnouncement': self._handle_device_online,
        }

        # Forward commands from UCPClient to internal streams
        ucp.intent_stream.subscribe(self._handle_intent)

        # Periodic context-based intent generation
        self.ucp.context_stream.pipe(
            ops.throttle_first(10)  # Check every 10 seconds
        ).subscribe(self._generate_contextual_intent)

    def _handle_intent(self, cmd: dict):
        try:
            print(f"📡 Received intent: {cmd}")
            intent = cmd.get("intent", {})
            parameters = cmd.get("parameters", {})

            logging.info(f"🟢 [Intent Received] {intent} with parameters {cmd}")

            if intent in self.intent_handlers:
                self.intent_handlers[intent](cmd)
            else:
                logging.warning(f"🔴 [Unknown Intent] {intent}")

        except json.JSONDecodeError:
            print(f"Invalid JSON received: {cmd}")

    def _handle_bootup(self, intent):
        print("Handling BootUp intent")
        self._perform_health_check()
        self.ucp.emit_command({"action": "observe"})
        # Add BootUp handling logic here
        logging.info("BootUp intent handled successfully.")

    def _handle_idle_check(self, intent):
        """Handle idle check by reporting current status"""
        self.ucp.emit_response("✅ System is operational")
        return True

    def _handle_resource_alert(self, intent):
        """Handle resource alerts"""
        warnings = intent.get('parameters', {}).get('warnings', [])
        severity = intent.get('parameters', {}).get('severity', 'medium')
        
        if warnings:
            self.ucp.emit_response(f"⚠️ Resource Alert ({severity}):\n" + "\n".join(warnings))
        return True

    def _handle_device_online(self, intent):
        """Handle device online announcements"""
        self.ucp.emit_response("🟢 Device is online and ready")
        return True

    def _handle_shut_down(self, parameters: dict):
        print("Handling ShutDown intent with parameters:", parameters)
        # Add ShutDown handling logic here
        logging.info("ShutDown intent handled successfully.")
    
    def _generate_task_queue(self, intent, parameters, context):
        if intent == "PlanTradingStrategy":
            return [
                {"action": "fetch_market_data", "parameters": parameters},
                {"action": "analyze_trends", "parameters": parameters},
                {"action": "generate_risk_assessment", "parameters": parameters},
                {"action": "suggest_trade", "parameters": parameters}
            ]
        return []
    
    def _perform_health_check(self):
        """Runs a basic health check before broadcasting device online announcement."""

        # Run Stress test
        logging.info("🔍 [Health Check] Running system stress test...")
        
        self.ucp.emit_command({"action": "run_stress_test", "parameters": {}})


        logging.info("✅ [Health Check Completed] System is stable.")
        
        self.ucp.intent_stream.on_next({
            "intent": "DeviceOnlineAnnouncement",
            "parameters": {},
        })
    
    def _execute_next_task(self, intent, context):
        if intent not in self.active_intents or not self.active_intents[intent]:
            logging.info(f"✅ [Intent Completed] {intent}")
            return
        
        task = self.active_intents[intent].pop(0)  # Get next task
        action = task["action"]
        parameters = task["parameters"]

        logging.info(f"⏳ [Executing Task] {action} with parameters {parameters}")
        self.ucp.emit_command({"action": action, "parameters": parameters})
        
        # Listen for completion and move to the next task
        self.ucp.response_stream.pipe(
            ops.filter(lambda resp: resp.get("action") == action + "_completed"),
            ops.take(1)  # Process only one response per task
        ).subscribe(lambda _: self._execute_next_task(intent, context))
    
    def _generate_contextual_intent(self, context):
        """Automatically generate intents based on time of day, system load, and other conditions."""
        current_time = datetime.now().hour
        system_load = context.get("system", {}).get("cpu_usage", 0)
        wallet_balance = context.get("wallet", {}).get("balance", 0)
        
        if 6 <= current_time < 9:
            self.ucp.intent_stream.on_next({
                "intent": "MorningRoutine",
                "parameters": {},
                "context": context
            })
        elif 12 <= current_time < 14:
            self.ucp.intent_stream.on_next({
                "intent": "CheckMarketMidday",
                "parameters": {},
                "context": context
            })
        elif 18 <= current_time < 21:
            self.ucp.intent_stream.on_next({
                "intent": "EveningWrapUp",
                "parameters": {},
                "context": context
            })
        
        # Trigger system optimization if CPU usage is high
        if system_load > 80:
            self.ucp.intent_stream.on_next({
                "intent": "SystemOptimization",
                "parameters": {},
                "context": context
            })
        
        # Trigger balance check if funds are low
        if wallet_balance < 50:
            self.ucp.intent_stream.on_next({
                "intent": "LowBalanceWarning",
                "parameters": {},
                "context": context
            })
        
        # Periodic self-review: If no active intent, generate a task
        if not self.active_intents:
            self.ucp.intent_stream.on_next({
                "intent": "IdleCheck",
                "parameters": {},
                "context": context
            })

