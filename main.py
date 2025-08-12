# main.py
import core_module as core


if __name__ == "__main__":
    core = core.CoreModule()
    core.run()
    # Start the core module which will handle the cognitive processes
    # and manage the perception and memory components.
    # This will also set up the event bus and UCP for communication.