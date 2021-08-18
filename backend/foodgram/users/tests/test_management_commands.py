from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class FillUsersTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command("fill_users", 5, stdout=out)
        self.assertIn("Пользователи созданы успешно.", out.getvalue())
