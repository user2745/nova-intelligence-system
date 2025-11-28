import unittest
import logging
from nova_core.DGOP.state_machine import StateMachine, AgentState

# Configure logging to avoid "No handlers could be found for logger" warnings
logging.basicConfig(level=logging.DEBUG)

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.sm = StateMachine()

    def test_initial_state(self):
        self.assertEqual(self.sm.get_state(), AgentState.IDLE)

    def test_transitions(self):
        # Test transition to PLANNING
        self.sm.set_state(AgentState.PLANNING)
        self.assertEqual(self.sm.get_state(), AgentState.PLANNING)

        # Test transition to EXECUTION
        self.sm.set_state(AgentState.EXECUTION)
        self.assertEqual(self.sm.get_state(), AgentState.EXECUTION)

        # Test transition to SLEEP
        self.sm.set_state(AgentState.SLEEP)
        self.assertEqual(self.sm.get_state(), AgentState.SLEEP)

        # Test transition back to IDLE
        self.sm.set_state(AgentState.IDLE)
        self.assertEqual(self.sm.get_state(), AgentState.IDLE)

    def test_invalid_state_type(self):
        with self.assertRaises(ValueError):
            self.sm.set_state("INVALID_STATE")

    def test_same_state_transition(self):
        self.sm.set_state(AgentState.PLANNING)
        # Should not raise error or change state
        self.sm.set_state(AgentState.PLANNING)
        self.assertEqual(self.sm.get_state(), AgentState.PLANNING)

if __name__ == '__main__':
    unittest.main()
