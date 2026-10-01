"""Generate and update documentation in a target project's root ``docs/``."""

__all__ = ["RepoDocumenter", "DocumentationResult"]


def __getattr__(name):
    """Load implementation symbols lazily so ``python -m`` stays warning-free."""
    if name in __all__:
        from .repo_documenter import DocumentationResult, RepoDocumenter

        return {
            "RepoDocumenter": RepoDocumenter,
            "DocumentationResult": DocumentationResult,
        }[name]
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))
