# Generated by Django 3.2.7 on 2023-06-11 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20230522_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='main_image',
            field=models.FileField(upload_to='rocknest/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.FileField(upload_to='rocknest/'),
        ),
    ]
