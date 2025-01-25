from datetime import datetime
import pytz

class TimeContextAwarenessEngine:
    """
    Gathers and processes time-based context for the Nova system.
    """

    def gather_context(self):
        """
        Collects the current date, time, and contextual information such as
        timezone, weekday, and part of the day.
        """
        now = self.fetch_current_time()
        current_time = datetime.now()  # Define current_time correctly

        context = {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "datetime": now,
            "date": self.format_date(now),
            "time": self.format_time(now),
            "weekday": self.get_weekday(now),
            "timezone": self.get_timezone(),
            "part_of_day": self.get_part_of_day(now),
        }
        return context

    def fetch_current_time(self):
        """
        Fetches the current date and time.
        Returns:
            datetime object with timezone awareness (if available).
        """
        timezone = self.get_timezone()
        if timezone:
            return datetime.now(pytz.timezone(timezone))
        return datetime.now()

    def format_date(self, dt):
        """
        Formats the date into a readable string.
        Args:
            dt (datetime): The datetime object.
        Returns:
            str: Formatted date string.
        """
        return dt.strftime("%Y-%m-%d")

    def format_time(self, dt):
        """
        Formats the time into a readable string.
        Args:
            dt (datetime): The datetime object.
        Returns:
            str: Formatted time string.
        """
        return dt.strftime("%H:%M:%S")

    def get_weekday(self, dt):
        """
        Retrieves the weekday name.
        Args:
            dt (datetime): The datetime object.
        Returns:
            str: Weekday name.
        """
        return dt.strftime("%A")

    def get_timezone(self):
        """
        Retrieves the system's current timezone.
        Returns:
            str: Timezone name, or None if not available.
        """
        try:
            return datetime.now().astimezone().tzinfo.zone
        except AttributeError:
            return None

    def get_part_of_day(self, dt):
        """
        Determines the part of the day (Morning, Afternoon, Evening, Night).
        Args:
            dt (datetime): The datetime object.
        Returns:
            str: Part of the day.
        """
        hour = dt.hour
        if hour < 6:
            return "Night"
        elif 6 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 18:
            return "Afternoon"
        else:
            return "Evening"
