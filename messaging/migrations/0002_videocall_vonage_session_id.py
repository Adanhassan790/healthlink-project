# Generated migration for Vonage session ID field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),  # or the latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='videocall',
            name='vonage_session_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
