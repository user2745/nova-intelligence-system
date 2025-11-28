import logging
from enum import Enum, auto

class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTION = auto()
    SLEEP = auto()

class StateMachine:
    def __init__(self):
        self._state = AgentState.IDLE
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"State Machine initialized in {self._state.name} state.")

    def set_state(self, state: AgentState):
        if not isinstance(state, AgentState):
            raise ValueError(f"Invalid state: {state}")
        
        if self._state != state:
            self.logger.info(f"Transitioning from {self._state.name} to {state.name}")
            self._state = state
        else:
            self.logger.debug(f"Already in {state.name} state.")

    def get_state(self) -> AgentState:
        return self._state
