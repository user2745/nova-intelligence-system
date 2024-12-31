class TestEngine:
    def __init__(self):
        self.name = "TestEngine"

    def gather_context(self):
        return {"test_key": "test_value"}

    def run(self):
        return "TestEngine is running!"
