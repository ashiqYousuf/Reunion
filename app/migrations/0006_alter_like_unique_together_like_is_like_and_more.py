# Generated by Django 4.1.7 on 2023-03-17 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_like'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='like',
            name='is_like',
            field=models.BooleanField(choices=[(True, 'Like'), (False, 'Dislike')], default=True),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'post', 'is_like')},
        ),
        migrations.RemoveField(
            model_name='like',
            name='vote',
        ),
    ]
