from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandError

from ...factories import UserFactory, UserSubscriptionFactory


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми пользователями."

    def add_arguments(self, parser):
        parser.add_argument(
            "users_amount",
            type=int,
            help=(
                "Сколько пользователей создать. Будет созданы подписки "
                "пользователей (в 3 раза меньше чем пользователей)."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        users_amount = options.get("users_amount", None)
        users_subscriptions = users_amount // 3
        if users_amount <= 0:
            raise CommandError("Количество не может быть отрицательным.")

        UserFactory.create_batch(users_amount)
        UserSubscriptionFactory.create_batch(users_subscriptions)

        self.stdout.write(self.style.SUCCESS("Пользователи созданы успешно."))
