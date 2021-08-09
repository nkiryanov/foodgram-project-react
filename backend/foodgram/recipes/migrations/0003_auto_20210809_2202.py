# Generated by Django 3.2.5 on 2021-08-09 22:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_auto_20210806_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurementunit',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(max_length=1000, verbose_name='Описание рецепта'),
        ),
        migrations.CreateModel(
            name='RecipeCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='recipes.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Объект корзины покупок',
                'verbose_name_plural': 'Объекты корзины покупок',
            },
        ),
        migrations.AddConstraint(
            model_name='recipecart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='Unique RecipeCart per user and recipe'),
        ),
    ]
