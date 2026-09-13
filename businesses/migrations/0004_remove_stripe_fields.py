from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("businesses", "0003_stripe_billing"),
    ]

    operations = [
        migrations.RemoveField(model_name="business", name="stripe_customer_id"),
        migrations.RemoveField(model_name="business", name="stripe_subscription_id"),
        migrations.RemoveField(model_name="business", name="subscription_status"),
    ]
