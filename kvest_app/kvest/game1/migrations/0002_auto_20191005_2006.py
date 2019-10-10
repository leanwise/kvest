# Generated by Django 2.2.5 on 2019-10-05 20:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game1', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='created_at',
            new_name='start',
        ),
        migrations.AlterField(
            model_name='mission',
            name='img',
            field=models.ImageField(default='game1/static/game1/img/None/no-img.jpg', upload_to='game1/static/game1/img/pic'),
        ),
        migrations.AlterField(
            model_name='team',
            name='finish',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='progress',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='Gamer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game1.Team')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]