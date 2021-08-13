import random
from typing import Any, Optional

from django.core.management.base import BaseCommand

from ....core.constants import TAGS
from ...factories import RecipeFactory, RecipeTagFactory


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        for name, slug in TAGS.items():
            RecipeTagFactory(
                name=name,
                slug=slug,
            )

        for _ in range(50):
            num_ingredients = random.randint(1, 10)
            num_tags = random.randint(1, 3)
            RecipeFactory(
                ingredients__num=num_ingredients,
                tags__num=num_tags,
            )
