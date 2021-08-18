# Generated by Django 3.2.6 on 2021-08-18 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20210815_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='measurementunit',
            name='name',
            field=models.CharField(db_index=True, max_length=50, unique=True, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(db_index=True, max_length=200, verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='name',
            field=models.CharField(db_index=True, max_length=30, unique=True, verbose_name='Тэг рецепта'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='Unique ingredient per recipe'),
        ),
    ]
