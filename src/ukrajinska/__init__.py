from .core import Ukrajinska

ukrajinska = Ukrajinska()

to_latin = ukrajinska.to_latin
to_cyrillic = ukrajinska.to_cyrillic

__all__ = ["to_latin", "to_cyrillic", "Ukrajinska"]
__version__ = "0.1.0"