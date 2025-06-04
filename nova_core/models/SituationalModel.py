

class SituationalModel:
    """
    A representational model capturing the current situation in Nova Core.
    It structures the situation into three parts:
    1. Perceived facts ('what’s here right now')
    2. Interpreted meaning ('what does it mean')
    3. Projected implications ('what happens next')
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
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

    def add_model(self, model: SituationalModel):
        """Add a new situational model."""
        self.models[model.name] = model

    def get_model(self, name: str) -> SituationalModel:
        """Retrieve a situational model by name."""
        return self.models.get(name, None)

    def __repr__(self):
        return "\n\n".join(str(model) for model in self.models.values())