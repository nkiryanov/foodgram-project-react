from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from ...users.factories import UserFactory


class FillRecipesTest(TestCase):
    def test_command_output(self):
        UserFactory.create_batch(2)
        out = StringIO()
        call_command("fill_recipes", 20, stdout=out)
        self.assertIn("Рецепты созданы успешно.", out.getvalue())
