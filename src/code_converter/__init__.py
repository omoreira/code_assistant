"""Tools for converting notes, examples, and pseudocode into artifacts."""

__all__ = ["AssistantContractBuilder", "LongContextReader", "PseudofileConverter"]


def __getattr__(name):
    """Load implementation symbols lazily so ``python -m`` stays warning-free."""
    if name == "AssistantContractBuilder":
        from code_converter.assistant_contract_builder import AssistantContractBuilder

        return AssistantContractBuilder
    if name == "LongContextReader":
        from code_converter.longtext_pseudo_converter import LongContextReader

        return LongContextReader
    if name == "PseudofileConverter":
        from code_converter.pseudofile_converter import PseudofileConverter

        return PseudofileConverter
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))
