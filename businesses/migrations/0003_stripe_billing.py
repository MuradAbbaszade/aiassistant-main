# Generated manually for Stripe billing fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("businesses", "0002_business_plan"),
    ]

    operations = [
        migrations.AddField(
            model_name="business",
            name="stripe_customer_id",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="business",
            name="stripe_subscription_id",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="business",
            name="subscription_status",
            field=models.CharField(
                choices=[
                    ("none", "None"),
                    ("incomplete", "Incomplete"),
                    ("trialing", "Trialing"),
                    ("active", "Active"),
                    ("past_due", "Past due"),
                    ("canceled", "Canceled"),
                    ("unpaid", "Unpaid"),
                ],
                db_index=True,
                default="none",
                max_length=32,
            ),
        ),
    ]
