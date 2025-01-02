class ExecutorManager:
    def __init__(self, voice_module):
        self.executed_actions = []
        self.voice = voice_module

    def execute(self, decision):
        print(f"Nova: {decision}")
        if "resource optimization" in decision:
            user_response = input("Nova: I noticed high CPU usage. Shall I free up resources? (yes/no): ").strip().lower()
            if user_response == "yes":
                print("Nova: Optimizing memory...")
                os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
                print("Nova: Resources have been freed up.")
                self.executed_actions.append(decision)
            else:
                print("Nova: Got it, no changes made.")
        elif "pausing GPU-intensive tasks" in decision:
            user_response = input("Nova: GPU usage is high. Would you like me to pause heavy processes? (yes/no): ").strip().lower()
            if user_response == "yes":
                print("Nova: Throttling GPU-intensive tasks.")
                # Add GPU throttling logic
                self.executed_actions.append(decision)
        elif "lunchtime" in decision:
            user_response = input("Nova: It's almost noon. Would you like me to summarize your morning progress? (yes/no): ").strip().lower()
            if user_response == "yes":
                print("Nova: Preparing a summary of your progress...")
                # Add progress summary logic
                self.executed_actions.append(decision)
        else:
            print("Nova: No action required.")

        self.log_executed_actions()

    def log_executed_actions(self):
        print("\n--- Executed Actions Log ---")
        for action in self.executed_actions:
            print(action)
        print("--- End of Log ---")
