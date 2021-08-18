import random
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandError

from ....core.constants import TAGS
from ...factories import (
    RecipeCartFactory,
    RecipeFactory,
    RecipeFavoriteFactory,
    RecipeTagFactory,
)


class Command(BaseCommand):
    help = (
        "Заполняет базу данных тестовыми рецептами и добавляет в "
        "избаранное или корзину.\n"
        "Принимает в качестве аргумента число. Столько рецептов будет "
        "создано. Подписок и добавлений в избранное в 3 раза меньше."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "recipes_amount",
            type=int,
            help=(
                "Сколько рецептов создать. Также будут созданы связанные "
                "объекты."
            ),
        )

        parser.add_argument(
            "--realimages",
            action="store_true",
            help=(
                "Если задан, то добавляет в рецепты реальные картинки. "
                "Нужно подключение к интернет. "
            ),
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:

        for name, slug in TAGS.items():
            RecipeTagFactory(
                name=name,
                slug=slug,
            )

        recipes_amount = options.get("recipes_amount", None)
        if recipes_amount <= 0:
            raise CommandError("Количество не может быть отрицательным.")

        related_objects_amount = recipes_amount // 3
        add_real_images = True if options["realimages"] else False

        for _ in range(recipes_amount):
            num_ingredients = random.randint(1, 10)
            num_tags = random.randint(1, 3)
            RecipeFactory(
                ingredients__num=num_ingredients,
                tags__num=num_tags,
                add_real_image=add_real_images,
            )

        RecipeFavoriteFactory.create_batch(related_objects_amount)
        RecipeCartFactory.create_batch(related_objects_amount)

        self.stdout.write(self.style.SUCCESS("Рецепты созданы успешно."))
