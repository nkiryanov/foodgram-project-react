# Generated by Django 3.2.5 on 2021-08-06 19:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipefavorite',
            name='unique_recipefavorite_by_user_and_recipe',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4320)], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(200)], verbose_name='Количество'),
        ),
        migrations.AddConstraint(
            model_name='recipefavorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='Unique RecipeFavorite per user and recipe'),
        ),
    ]
