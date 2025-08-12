import logging
import time

from nova_core.DGOP.drives import TimeDrive, SleepDrive, CuriosityDrive


class DriveManager: 
    def __init__(self):
        self.drives = {
            "time": TimeDrive(),
            "sleep": SleepDrive(),
            "curiosity": CuriosityDrive()
        }
        logging.info("[DriveManager] Initialized")
    
    def tickAllDrivers(self):
        """
        Tick all drives to update their state.
        This method should be called periodically to ensure drives are evaluated.
        """
        for drive in self.drives.values():
            try:
                drive.tick()
                logging.info(f"[DriveManager] Ticked drive: {drive.name}")
            except Exception as e:
                logging.error(f"[DriveManager] Error ticking drive {drive.name}: {e}")
    
    def tickDrive(self, drive_name):
        """
        Tick a specific drive by name.
        """
        if drive_name in self.drives:
            try:
                self.drives[drive_name].tick()
            except Exception as e:
                logging.error(f"[DriveManager] Error ticking drive {drive_name}: {e}")
        else:
            logging.warning(f"[DriveManager] Drive {drive_name} not found")