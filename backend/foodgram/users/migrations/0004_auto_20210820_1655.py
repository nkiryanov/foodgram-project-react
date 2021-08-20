# Generated by Django 3.2.6 on 2021-08-20 16:55

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210815_2353'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['id'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AddConstraint(
            model_name='usersubscription',
            constraint=models.CheckConstraint(check=models.Q(('follower', django.db.models.expressions.F('following')), _negated=True), name='Unique subscription - prevent user follow himself'),
        ),
    ]
