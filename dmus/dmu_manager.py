import asyncio
import datetime
class DMUManager:
    def __init__(self, mutable_context):
        self.context = mutable_context
        self.baseline = {
            "cpu_threshold": 50,  # Adjust as needed
            "gpu_threshold": 10,  # Adjust as needed
        }
        self.active_decisions = set()

    async def make_decisions(self):
        """
        Continuously evaluate system stats, make decisions, and execute them.
        """
        print("Nova: Starting decision-making loop...")
        try:


            # Observation -> Evaluation -> Execution Pipeline
            observation_task = asyncio.create_task(self.make_observations())
            evaluations = asyncio.create_task(self.evaluate_observations(await observation_task))
            decisions = asyncio.create_task(self.execute_decisions(await evaluations))

            self.active_decisions.add(observation_task)
            self.active_decisions.add(evaluations)
            self.active_decisions.add(decisions)
            return list(self.active_decisions)
        except asyncio.CancelledError:
            print("Nova: Decision-making loop has been cancelled.")
            raise
        except Exception as e:
            print(f"Nova: Error in decision-making loop: {e}")
        finally:
            print("Nova: Decision-making loop ended.")

    async def make_observations(self):
        """
        Continuously monitor system stats and make observations.
        """
        context = self.context.get_current_context()
        time_of_day = context.get("time_of_day", {}).get("time", "")
        print("Nova: Making observations...")
        print(f"Nova: Current context: {context}")
        observations = []
        if context["CPU_usage"] > self.baseline["cpu_threshold"]:
            observations.append("High CPU usage detected.")
            print("Nova: High CPU usage detected.")
        if context["GPU_usage"] > self.baseline["gpu_threshold"]:
            observations.append("GPU usage is elevated.")
        if "12:00" <= time_of_day < "13:00":
            observations.append("It's lunchtime.")
        if "16:00" <= time_of_day < "17:00":
            observations.append("Afternoon slump detected.")

        return observations

    async def evaluate_observations(self, observations):
        """
        Evaluate the observations made and generate a list of evaluations.
        """
        evaluation_map = {
            "High CPU usage detected.": "Propose resource optimization: Freeing up memory.",
            "GPU usage is elevated.": "Recommend pausing GPU-intensive tasks.",
            "It's lunchtime.": "Suggest taking a break and summarizing morning progress.",
            "Afternoon slump detected.": "Encourage a quick stretch or refreshment break.",
        }

        return [evaluation_map[obs] for obs in observations if obs in evaluation_map]

    async def execute_decisions(self, evaluations):
        """
        Execute the decisions made based on the evaluations.
        """
        decisions = []
        for evaluation in evaluations:
            print(f"Nova: Executing decision: {evaluation}")
            if "resource optimization" in evaluation:
                print("Nova: Freeing up memory...")
            elif "pausing GPU-intensive tasks" in evaluation:
                print("Nova: Pausing GPU tasks...")
            elif "taking a break" in evaluation:
                print("Nova: Summarizing morning progress...")
            elif "quick stretch" in evaluation:
                print("Nova: Suggesting a quick stretch break...")

            decisions.append(evaluation)

        return decisions