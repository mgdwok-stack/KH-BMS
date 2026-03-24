"""
ML Package - 머신러닝 모델 레이어
"""

# Lazy imports to avoid requiring tensorflow/torch when not needed
__all__ = [
    "DNBPModel",
    "LSTMModel",
    "EnsemblePredictor",
    "ModelTrainer",
]


def __getattr__(name):
    """Lazy load ML models"""
    if name == "DNBPModel":
        from .dnbp_model import DNBPModel
        return DNBPModel
    elif name == "LSTMModel":
        from .lstm_model import LSTMModel
        return LSTMModel
    elif name == "EnsemblePredictor":
        from .ensemble import EnsemblePredictor
        return EnsemblePredictor
    elif name == "ModelTrainer":
        from .trainer import ModelTrainer
        return ModelTrainer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
