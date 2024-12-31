def load_module_class(module_path, class_name):
    try:
        module = importlib.import_module(module_path)
        engine_class = getattr(module, class_name, None)
        if not engine_class:
            raise AttributeError(f"Class '{class_name}' not found in module '{module_path}'.")
        return engine_class
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Module '{module_path}' not found.")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
