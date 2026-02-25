import griffe


class HideDataclassInit(griffe.Extension):
    """Remove auto-generated __init__ from dataclass documentation."""

    def on_class(self, *, cls: griffe.Class, **kwargs) -> None:
        # griffe labels dataclasses with "dataclass"
        if "dataclass" in cls.labels and "__init__" in cls.members:
            init_member = cls.members["__init__"]
            # Only remove if it has no user-written docstring
            if not init_member.docstring:
                del cls.members["__init__"]
