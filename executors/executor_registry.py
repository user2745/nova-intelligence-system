from utils.common import load_module_class

class ExecutorRegistry:
    """
    Registry for managing action executors
    """

    def __init__(self): 
        # Using a dictionary for action executors to allow dynamic addition/removal by name
        self.executors = {}

    def get_action_executor(self, name):
        """
        Returns the action executor by name.
        """
        return self.action_executors.get(name)

    def execute_all_action_executors(self):
        """
        Queries all registered action executors.
        """
        print("Querying all action executors...")
        for name, action_executor in self.action_executors.items():
            try:
                print(f"Querying action executor {name}...")
                action_executor.execute()
            except Exception as e:
                print(f"Error querying action executor {name}: {e}")
    
    def add_executor(self, name, module_path):
        """
        Dynamically loads and adds a new action executor to the registry.
        """
        if name in self.action_executors:
            print(f"Action executor {name} already exists.")
            return

        try:
            executor_class = load_module_class(module_path, name)
            self.action_executors[name] = executor_class()
            print(f"Action executor {name} loaded and added successfully.")
        except ModuleNotFoundError:
            print(f"Error: Module '{module_path}' not found.")
        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def remove_executor(self, name):
        """
        Removes an action executor from the registry.
        """
        if name in self.action_executors:
            del self.action_executors[name]
            print(f"Action executor {name} removed successfully.")
        else:
            print(f"Action executor {name} not found.")

    async def load_executor(self, executor_name, module_path):
        """
        Asynchronously loads and adds a new action executor to the registry.
        """
        try:
            executor_class = await load_module_class(module_path, executor_name)
            self.action_executors[executor_name] = executor_class()
            print(f"Action executor {executor_name} loaded and added successfully.")
        except ModuleNotFoundError:
            print(f"Error: Module '{module_path}' not found.")
        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")


    