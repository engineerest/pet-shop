# Generated by Django 5.0.2 on 2024-02-17 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_alter_post_options_alter_post_is_published_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='likes',
            field=models.IntegerField(blank=True, default=0, verbose_name='Вподобайки'),
        ),
        migrations.AddField(
            model_name='comment',
            name='dislikes',
            field=models.IntegerField(blank=True, default=0, verbose_name='Невподобайки'),
        ),
    ]