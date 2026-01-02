import logging
import time
from typing import Dict, Any

class InternalDrive:
    """Base class for a Drive."""
    def __init__(self, name: str, momentum: float = 0.7):
        self.name = name
        self.intensity = 0.0
        self.momentum = momentum # Higher momentum = more stability (less paranoia)
    
    def set_intensity(self, target_intensity: float):
        """Apply Markov-like smoothing (Exponential Moving Average)."""
        # New State = (Momentum * Old State) + ((1 - Momentum) * Input)
        self.intensity = (self.momentum * self.intensity) + ((1 - self.momentum) * target_intensity)

    def update(self, context: Dict[str, Any]):
        """Update intensity based on context."""
        pass

class WealthDrive(InternalDrive):
    """
    Drive: Resource Acquisition
    Formula: (Target - Balance) * Opportunity
    """
    def __init__(self):
        super().__init__("wealth", momentum=0.8) # Wealth is a slow burn
        self.target_balance = 10.0 # ETH
        
    def update(self, context: Dict[str, Any]):
        wallet = context.get("external_context", {})
        balance = wallet.get("balance", 0.0)
        
        # Simple logic: If below target, intensity rises.
        raw_intensity = 0.0
        if self.target_balance > 0:
            deficit = max(0, self.target_balance - balance)
            raw_intensity = min(1.0, deficit / self.target_balance)
        
        self.set_intensity(raw_intensity)

class SecurityDrive(InternalDrive):
    """
    Drive: Order Maintenance
    Formula: BaseAnxiety + (AnomalyScore * Sensitivity)
    """
    def __init__(self):
        super().__init__("security", momentum=0.5) # Security needs to be reactive but not jittery
        self.base_anxiety = 0.05 # Lowered base anxiety
        
    def update(self, context: Dict[str, Any]):
        system = context.get("external_context", {})
        cpu = system.get("cpu_usage", 0.0)
        
        # If CPU > 80%, Panic.
        anomaly_score = 0.0
        if cpu > 80:
            anomaly_score = (cpu - 80) / 20.0 # 0.0 to 1.0
            
        target = min(1.0, self.base_anxiety + anomaly_score)
        self.set_intensity(target)

class CuriosityDrive(InternalDrive):
    """
    Drive: Strategic Intelligence
    Formula: (1.0 - RecentNewInformation)
    """
    def __init__(self):
        super().__init__("curiosity", momentum=0.6)
        self.last_insight_time = time.time()
        
    def update(self, context: Dict[str, Any]):
        # Decay over time (boredom)
        time_since_insight = time.time() - self.last_insight_time
        boredom = min(1.0, time_since_insight / 300.0) # Max boredom after 5 mins
        
        self.set_intensity(boredom)

class DriveManager: 
    def __init__(self):
        self.drives = {
            "wealth": WealthDrive(),
            "security": SecurityDrive(),
            "curiosity": CuriosityDrive()
        }
        logging.info("[DriveManager] Initialized Trinity Drives")
    
    def update_drives(self, context: Dict[str, Any]) -> str:
        """
        Update all drives and return the name of the dominant drive.
        """
        max_intensity = -1.0
        dominant_drive = "security" # Default to safety
        
        for name, drive in self.drives.items():
            try:
                drive.update(context)
                logging.debug(f"[Drive] {name}: {drive.intensity:.2f}")
                
                # Security Override: If Security > 0.8, it wins automatically
                if name == "security" and drive.intensity > 0.8:
                    return "security"
                
                if drive.intensity > max_intensity:
                    max_intensity = drive.intensity
                    dominant_drive = name
                    
            except Exception as e:
                logging.error(f"[DriveManager] Error updating {name}: {e}")
                
        return dominant_drive