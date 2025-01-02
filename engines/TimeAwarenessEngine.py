import datetime

class TimeAwarenessEngine:
    def get_time_block(self):
        """
        Returns the current time block.
        """
        current_hour = datetime.datetime.now().hour

        if 0 <= current_hour < 4:
            return "Asia Time (12am-4am)"
        elif 4 <= current_hour < 8:
            return "Early Bird (4am-8am)"
        elif 8 <= current_hour < 12:
            return "Morning (8am-12pm)"
        elif 12 <= current_hour < 16:
            return "Afternoon (12pm-4pm)"
        elif 16 <= current_hour < 20:
            return "Evening (4pm-8pm)"
        else:
            return "Midnight (8pm-12am)"

    def gather_context(self):
        """
        Gathers time-based context.
        """
        time_block = self.get_time_block()
        context = {
            "time_block": time_block
        }
        return context