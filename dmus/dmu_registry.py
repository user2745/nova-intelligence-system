from utils.common import load_module_class

class DMURegistry:
    """
    Registry for managing DMUs
    """

    def __init__(self): 
        # Using a list for DMUs to allow dynamic addition/removal
        self.dmus = [BasicDMU()]

    def get_dmu(self, name):
        """
        Returns the DMU by name.
        """
        for dmu in self.dmus:
            if dmu.name == name:
                return dmu
        return None
    
    def execute_all_dmus(self):
        """
        Executes all registered DMUs.
        """
        print("Executing all DMUs...")
        for dmu in self.dmus:
            try:
                print(f"Executing DMU {dmu.name}...")
                dmu.execute()
            except Exception as e:
                print(f"Error executing DMU {dmu.name}: {e}")

    def add_dmu(self, dmu):
        """
        Adds a new DMU to the registry.
        """
        if dmu in self.dmus:
            print(f"DMU {dmu.name} already exists.")
            return
        self.dmus.append(dmu)
        print(f"DMU {dmu.name} added successfully.")

    def remove_dmu(self, name):
        """
        Removes a DMU from the registry.
        """
        for dmu in self.dmus:
            if dmu.name == name:
                self.dmus.remove(dmu)
                print(f"DMU {name} removed successfully.")
                return
        print(f"DMU {name} not found.")

    async def load_dmu(self, dmu_name, module_path):
        """
        Dynamically loads and adds a new DMU to the registry.
        """
        try:
            dmu_class = load_module_class(module_path, dmu_name)
            self.dmus.append(dmu_class())
            print(f"DMU {dmu_name} loaded and added successfully.")
        except ModuleNotFoundError:
            print(f"Error: Module '{module_path}' not found.")
        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    async def unload_all_dmus(self, dmu_name):
        """
        Asynchronously unloads a DMU from the registry.
        """
        for dmu in self.dmus:
            if dmu.name == dmu_name:
                self.dmus.remove(dmu)
                print(f"DMU {dmu_name} unloaded successfully.")
                return
        print(f"DMU {dmu_name} not found.")