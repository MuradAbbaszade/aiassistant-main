from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("businesses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="business",
            name="plan",
            field=models.CharField(
                choices=[("standard", "Standart"), ("business", "Biznes")],
                db_index=True,
                default="standard",
                max_length=32,
            ),
        ),
    ]
