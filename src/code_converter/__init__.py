"""Tools for converting pseudocode and long-form notes into code plans."""

__all__ = ["LongContextReader", "PseudofileConverter"]


def __getattr__(name):
    """Load implementation symbols lazily so ``python -m`` stays warning-free."""
    if name == "LongContextReader":
        from code_converter.longtext_pseudo_converter import LongContextReader

        return LongContextReader
    if name == "PseudofileConverter":
        from code_converter.pseudofile_converter import PseudofileConverter

        return PseudofileConverter
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))
