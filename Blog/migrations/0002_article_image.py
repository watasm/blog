# Generated by Django 3.0.2 on 2020-01-10 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='image',
            field=models.ImageField(blank=True, upload_to='blog/articles/images', verbose_name='image'),
        ),
    ]
