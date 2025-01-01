from immutables import Map

class ImmutableContext:
    def __init__(self):
        self._context = Map()
        self.versions = []  # Optional: Keep a history of context versions

    def get_context(self, key):
        return self._context.get(key)

    def snapshot(self, mutable_context):
        """
        Freeze the mutable context into an immutable snapshot.
        """
        self._context = Map(mutable_context)
        self.versions.append(self._context)  # Optional: Store snapshots for rollback or debugging
        print("Snapshot created.")
