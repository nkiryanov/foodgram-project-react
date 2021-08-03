from django.template.defaultfilters import slugify as django_slugify

from .constants import CYRILLIC_ALPHABET


def cyrillic_slugify(name):
    """Support cyrillic alphabet."""
    name = name.lower()
    transliterated_name = "".join(
        CYRILLIC_ALPHABET.get(character, character) for character in name
    )
    return django_slugify(transliterated_name)
