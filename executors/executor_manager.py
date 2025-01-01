import os

class ExecutorManager:
    def __init__(self):
        self.executed_actions = []

    def run(self, decisions):
        for decision in decisions:
            if decision:
                print(f"Executing: {decision}")
                user_response = self.proactive_message(decision)
                if user_response:
                    self.handle_user_response(user_response, decision)
        print("Actions completed.")
        self.log_executed_actions()

    def proactive_message(self, decision):
        # Debug log to check decision contents
        print(f"[DEBUG] Decision passed to proactive_message: {decision}")

        # Trigger proactive prompts based on decision keywords
        if "umbrella" in decision.lower():
            return input("Proactive Alert: Looks like rain tomorrow. Set a reminder? (yes/no): ")
        elif "energy" in decision.lower():
            return input("Proactive Alert: Energy usage is high. Dim the lights? (yes/no): ")
        elif "stock" in decision.lower():
            return input("Proactive Alert: Stock trend detected. Review portfolio? (yes/no): ")
        return None

    def handle_user_response(self, response, decision):
        if response.lower() == "yes":
            print(f"Action Confirmed: {decision}")
            self.executed_actions.append(f"Confirmed: {decision}")
        elif response.lower() == "no":
            print(f"Action Skipped: {decision}")
            self.executed_actions.append(f"Skipped: {decision}")
        else:
            print("Invalid response. No action taken.")

    def log_executed_actions(self):
        print("\n--- Executed Actions Log ---")
        for action in self.executed_actions:
            print(action)
        print("--- End of Log ---")
    
    def execute(self, decision):
        if "Freeing up resources" in decision:
            user_friendly_response = self.llm.generate_response(
                f"Explain the following system decision to the user: {decision}"
            )
            print(f"Action Response: {user_friendly_response}")
            os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
        elif "Throttling" in decision:
            user_friendly_response = self.llm.generate_response(
            f"Explain the following system decision to the user: {decision}"
            )
            print(f"Action Response: {user_friendly_response}")
            print(f"Executing Action: {decision}")
        with open("actions_log.txt", "a") as log_file:
            log_file.write(f"{decision}\n")