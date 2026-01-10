# Generated migration for MFA device models (TOTP + WebAuthn)
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_revokedaccesstoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="MFATOTPDevice",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(blank=True, max_length=100)),
                ("secret", models.CharField(max_length=128)),
                ("confirmed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="totp_devices", to="accounts.profile" if False else "auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="WebAuthnCredential",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("credential_id", models.BinaryField()),
                ("public_key", models.TextField()),
                ("sign_count", models.IntegerField(default=0)),
                ("label", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="webauthn_credentials", to="auth.user")),
            ],
        ),
    ]
