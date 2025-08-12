from typing import Any, Dict, List, Optional, Tuple
import logging

class SituationalModel:
    """
    A representational model capturing the current situation in Nova Core.
    It structures the situation into three parts:
    1. Perceived facts ('what’s here right now')
    2. Interpreted meaning ('what does it mean')
    3. Projected implications ('what happens next')
    """

    def __init__(self):
        self.name = ""
        self.present = {}
        self.meaning = {}
        self.predictions = {}

    def set_present(self, key: str, value: any):
        self.present[key] = value

    def set_meaning(self, key: str, value: any):
        self.meaning[key] = value

    def set_prediction(self, key: str, value: any):
        self.predictions[key] = value

    def get_present(self, key: str):
        return self.present.get(key)

    def get_meaning(self, key: str):
        return self.meaning.get(key)

    def get_prediction(self, key: str):
        return self.predictions.get(key)

    def __repr__(self):
        return (
            f"SituationalModel(name={self.name})\n"
            f"  Present: {self.present}\n"
            f"  Meaning: {self.meaning}\n"
            f"  Predictions: {self.predictions}"
        )
class SituationalAwareness:
    """
    A class representing situational awareness in the Nova Core system.
    This class manages multiple situational models and provides methods
    to analyze and retrieve situational data.
    """

    def __init__(self):
        self.models = {}
        self.current_situation = {
            "external_context": {},  # What's happening outside
            "internal_context": {},  # NOVA's internal state
            "temporal_context": {},  # Time-based patterns
            "social_context": {}     # User state/needs
        } # Each is its own situational model

    def add_model(self, model: SituationalModel):
        """Add a new situational model."""
        self.models[model.name] = model

    def add_event(self, name: str, payload: Dict[str, Any] | None = None) -> None:
        """Add an event to the situational model by name or to the external_context."""
        if name == "external_context":
            if payload:
                for key, value in payload.items():
                    self.current_situation["external_context"][key] = value
            logging.info(f"Event added to external_context: {payload}")
        else:
            if name not in self.models:
                self.models[name] = SituationalModel()
                self.models[name].name = name
            model = self.models[name]
            if payload:
                for key, value in payload.items():
                    model.set_present(key, value)
            logging.info(f"Event added to situational model '{name}': {payload}")

    def remove_event(self, name: str, key: str) -> None:
        """Remove an event (by key) from a named sub-model or from external_context."""
        if name == "external_context":
            if key in self.current_situation.get("external_context", {}):
                del self.current_situation["external_context"][key]
                logging.info(f"Event '{key}' removed from external_context")
            else:
                logging.warning(f"Key '{key}' not found in external_context")
        elif name in self.models:
            model = self.models[name]
            if key in model.present:
                del model.present[key]
                logging.info(f"Event '{key}' removed from situational model '{name}'")
            else:
                logging.warning(f"Key '{key}' not found in situational model '{name}'")
        else:
            logging.warning(f"Model '{name}' not found")

    def pop_latest_event(self, name: str) -> dict | None:
        """
        Remove and return the most recently added event from the given context or model.
        Returns a dict {key: value} of the popped item, or None if empty or not found.
        """
        # External context is an ordered dict in Python 3.7
        if name == "external_context":
            ctx = self.current_situation.get("external_context", {})
            if ctx:
                key, val = ctx.popitem()  # removes last inserted item
                logging.info(f"Popped event '{key}' from external_context")
                return {key: val}
            else:
                logging.warning("No events to pop in external_context")
                return None
        # Named SituationalModel instances
        if name in self.models:
            model = self.models[name]
            if model.present:
                # remove last inserted present key
                key, val = model.present.popitem()
                logging.info(f"Popped event '{key}' from situational model '{name}'")
                return {key: val}
            else:
                logging.warning(f"No events to pop in situational model '{name}'")
                return None
        logging.warning(f"Model '{name}' not found")
        return None    


    def get_model(self, name: str) -> SituationalModel:
        """Retrieve a situational model by name."""
        return self.models.get(name, None)
    
    def merge_event(self, payload: dict):
        """
        Shallow‐merge incoming payload into current_situation.
        You could route keys to different sub‐contexts if you like.
        """
        for k, v in payload.items():
            # you might want more sophisticated routing logic here
            self.current_situation.setdefault("external_context", {})[k] = v

    def __repr__(self):
        return "\n\n".join(str(model) for model in self.models.values())