class UnavailableFeatureError(Exception):
    def __init__(self, feature_name: str) -> None:
        super().__init__(f"Feature '{feature_name}' is unavailable")
        self.feature_name = feature_name
