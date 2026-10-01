"""Generate a UI in a target project's root ``ui/`` directory."""

__all__ = ["UIBuilder", "UIBuildResult"]


def __getattr__(name):
    """Load implementation symbols lazily so ``python -m`` stays warning-free."""
    if name in __all__:
        from .ui_builder import UIBuilder, UIBuildResult

        return {"UIBuilder": UIBuilder, "UIBuildResult": UIBuildResult}[name]
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))
