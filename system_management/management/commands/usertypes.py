from django.core.management.base import BaseCommand
from system_management.models import UserType

class Command(BaseCommand):
    """
    Management command to load predefined statuses into the DocumentStatus model.

    Usage:
        python manage.py load_usertypes

    This command adds predefined usertypes to the UserType model if they do not already exist.

    """

    help = 'Loads predefined usertypes into the UserType model'

    def handle(self, *args, **kwargs):

        self.stdout.write('Starting to load usertypes...')
        names = ['ADMIN', 'LOGISITCS_PROVIDER', 'EXPORTER']

        # Iterate through usertypes
        for name in names:
            _, created = UserType.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added new usertype: {name}'))
            else:
                self.stdout.write(f'Usetype already exists: {name}')

        self.stdout.write(self.style.SUCCESS('Finished adding usertypes'))
        print("Usertype loaded successfully.")
