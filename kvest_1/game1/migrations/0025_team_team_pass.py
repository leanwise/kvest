# Generated by Django 2.2.5 on 2019-10-08 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game1', '0024_auto_20191006_0225'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='team_pass',
            field=models.CharField(default='xxxxxxxxxxxxxxxxxxxxxxxxxx1111111111111', max_length=50, verbose_name='pass'),
        ),
    ]
