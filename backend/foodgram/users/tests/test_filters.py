from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from ...recipes.factories import RecipeFactory
from ..factories import UserFactory, UserSubscriptionFactory

URL_USERS_LIST = reverse("users-list")
URL_SUBSRIPRIONS_LIST = reverse("subscriptions-list")
URL_USER_DETAIL = reverse("users-detail", args=[1])


class UsersFilterTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = UserFactory()

        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    def test_authorized_user_subscriptions_recipes_limit_filter(self):
        """
        Counts recipes in user object response. If "recipe_limit" filter was
        used the number of user's recipes should be limited.
        """
        other_user = UserFactory()
        RecipeFactory.create_batch(20, author=other_user)
        user = UsersFilterTests.user
        UserSubscriptionFactory(
            follower=user,
            following=other_user,
        )
        client = UsersFilterTests.authorized_client

        response_data = client.get(URL_SUBSRIPRIONS_LIST).data
        other_user_data = response_data.get("results")[0]
        other_user_recipes_list = other_user_data.get("recipes")

        self.assertEqual(
            len(other_user_recipes_list),
            20,
            msg="Без фильтра должны возвращать все рецепты. Их 20.",
        )

        query_params = {"recipes_limit": 5}
        response_data = client.get(URL_SUBSRIPRIONS_LIST, query_params).data
        other_user_data = response_data.get("results")[0]
        other_user_recipes_list = other_user_data.get("recipes")

        self.assertEqual(
            len(other_user_recipes_list),
            5,
            msg=(
                "С фильтром количество рецептов пользователей должно быть "
                "ограничено. Должно быть 5.",
            ),
        )
