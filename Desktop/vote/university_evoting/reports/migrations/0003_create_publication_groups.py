from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    # permissions
    try:
        review_perm = Permission.objects.get(codename='can_review_publication')
        publish_perm = Permission.objects.get(codename='can_publish_publication')
    except Permission.DoesNotExist:
        return

    reviewer_group, _ = Group.objects.get_or_create(name='reviewer')
    publisher_group, _ = Group.objects.get_or_create(name='publisher')

    reviewer_group.permissions.add(review_perm)
    publisher_group.permissions.add(publish_perm)


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['reviewer', 'publisher']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_resultpublication'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_code=remove_groups),
    ]
