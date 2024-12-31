class BasicDMU:
    """
    Processes context and makes basic decisions.
    """

    def __init__(self, llm):
        self.llm = llm

    def process_context(self, context):
        """
        Makes a decision and refines it using the LLM.
        """
        raw_decision = "System running normally."
        if context["cpu_usage"] > 10:
            raw_decision = "High CPU usage detected! Reduce load."
        elif context["memory_usage"] > 10:
            raw_decision = "High memory usage detected! Monitor closely."

        # Refine decision with LLM
        refined_decision = self.llm.generate_response(
            f"Refine this decision for user communication: {raw_decision}"
        )
        return refined_decision