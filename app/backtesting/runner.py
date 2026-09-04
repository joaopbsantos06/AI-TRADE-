class BacktestRunner:
    """Extension point: callers must feed timestamp-bounded historical slices to avoid look-ahead bias."""

    def run(self, historical_slices):
        return [
            slice_ for slice_ in historical_slices
        ]  # intentional placeholder, no look-ahead access
