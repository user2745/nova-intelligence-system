import importlib


class NovaRegistry:
    """
    Registry for managing engines, DMUs, and action executors.
    """

    def __init__(self):
        # Using a dictionary for engines to allow dynamic addition/removal by name
        self.engines = {}



    def add_engine(self, name, module_path):
        """
        Dynamically loads and adds a new engine to the registry.
        """
        if name in self.engines:
            print(f"Engine {name} already exists.")
            return

        try:
            module = importlib.import_module(module_path)
            engine_class = getattr(module, name, None)
            if engine_class is None:
                print(f"Error: Class '{name}' not found in module '{module_path}'.")
                return

            # Initialize the engine and add it to the registry
            self.engines[name] = engine_class()
            print(f"Engine {name} loaded and added successfully.")
        except ModuleNotFoundError:
            print(f"Error: Module '{module_path}' not found.")
        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error adding engine {name}: {e}")

    async def load_engine(self, engine_name, module_path):
        """
        Dynamically load a context engine at runtime.
        """
        try:
            print(f"Loading engine {engine_name} from {module_path}...")
            class_name = to_camel_case(engine_name)
            print(f"Class Name: {class_name}")
            module = importlib.import_module(module_path)
            print(f"Module: {module}")
            engine_class = getattr(module, class_name)  # Use the exact case of `name`
            print(f"Engine Class: {engine_class}")
            engine_instance = engine_class()
            print(f"Engine Instance: {engine_instance}")
            self.add_engine(class_name, module_path)
            print(f"Engine {class_name} loaded and added to registry.")
        except ModuleNotFoundError:
            print(f"Error: Module '{module_path}' not found. Ensure the file exists.")
        except AttributeError:
            print(f"Error: Class '{engine_name}' not found in module '{module_path}'.")
        except Exception as e:
            print(f"Unexpected error loading engine {engine_name}: {e}")

    def remove_engine(self, name):
        """
        Removes an engine from the registry by name.
        """
        if name in self.engines:
            del self.engines[name]
            print(f"Engine {name} removed successfully.")
        else:
            print(f"Engine {name} does not exist.")
