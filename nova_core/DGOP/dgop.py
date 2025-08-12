# Drivers, Goals, Objectives, and Plans (DGOP) module for Nova Intelligence System
# This module handles the cognitive processes of Nova, including speech synthesis, situational awareness, and
# interaction with the Unified Context Pipeline (UCP).

from nova_core.DGOP.drives import DriveManager

class DGOP:
    def __init__(self):
        self.current_focus = None
        self.drives = DriveManager()

    def initialize(self):
        """
        Initialize the DGOP system.
        This method should be called at the start of the Nova system.
        """
        self.drives.tickAllDrivers()
        self.current_focus = 'sleep'  # Default focus
        logging.info("[DGOP] Initialized")

    def readFocus(self):
        """
        Read the current focus of the DGOP system.
        This method returns the current focus drive.
        """
        return self.current_focus
    
    def updateFocus(self, new_focus: str):
        """
        Update the current focus of the DGOP system.
        
        :param new_focus: The new focus drive to set.
        """
        self.current_focus = new_focus
        logging.info(f"[DGOP] Focus updated to: {new_focus}")
