from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')

class GenericDrive(ABC, Generic[T]):
    """
    Abstract base class for generic drives in the Nova Core system.
    Drives are responsible for managing cognitive processes and interactions.
    """

    @abstractmethod
    def initialize(self, data: T) -> None:
        """
        Start the drive with the provided data.
        
        :param data: The data to be processed by the drive.
        """
        self.intensity = 0.0
        self.rise_rate = 0.1
        self.decay_rate = 0.05
        self.threshold = 1.0
        pass

    @abstractmethod
    def tick(self, dt: T) -> None:
        """
        Run the drive with the provided data.
        
        :param data: The data to be processed by the drive.
        """
        self.intensity = min(1.0, self.intensity + self.rise_rate * dt)
        pass

    @abstractmethod
    def satisfy(self, data: T) -> None:
        """
        Process the given data and perform necessary actions.
        
        :param data: The data to be processed by the drive.
        """
        self.intensity *= self.decay_on_success
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the drive to its initial state.
        """
        self.intensity = 0.0
        self.rise_rate = 0.1
        self.decay_rate = 0.05
        self.threshold = 1.0
        pass