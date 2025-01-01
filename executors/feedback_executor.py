class FeedbackLoop:
    def __init__(self):
        self.log = []

    def log_decisions(self, context, decision):
            # Log context and decisions (same as before)
            print(f"[Feedback Loop] Logged decisions: {decision}")

    def update_memory(self, memory_manager, result):
        """
        Updates long-term memory based on user feedback or results.
        """
        if result == "Resolved":
            memory_manager.store_insight("Action successfully resolved an issue.")
        elif result == "Failed":
            memory_manager.store_insight("Action failed. Consider alternative responses.")