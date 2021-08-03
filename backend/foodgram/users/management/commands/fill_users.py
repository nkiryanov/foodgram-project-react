from typing import Any, Optional

from django.core.management.base import BaseCommand

from ...factories import UserFactory

USERS = 50


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        UserFactory.create_batch(USERS)
