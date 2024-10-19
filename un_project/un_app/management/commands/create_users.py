from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from un_app.models import Player, UserProfile

class Command(BaseCommand):
    help = 'Create predefined users and link them to existing players via UserProfile'

    def handle(self, *args, **kwargs):
        # List of predefined users to create
        users_data = [
            {'username': 'Axeman_76', 'email': 'bigike@werespecialstudios.com', 'password': 'changeme123', 'is_superuser': False, 'is_staff': False},
            {'username': 'OldManReidGaming', 'email': 'oldmanreid@werespecialstudios.com', 'password': 'changeme123', 'is_superuser': False, 'is_staff': False},
            {'username': 'Cowman7', 'email': 'unglenelton@werespecialstudios.com', 'password': 'changeme123', 'is_superuser': False, 'is_staff': False},
            {'username': 'Tallerfiber1', 'email': 'grum@werespecialstudios.com', 'password': 'changeme123', 'is_superuser': False, 'is_staff': False},
            {'username': 'vlueban', 'email': 'papoquim@werespecialstudios.com', 'password': 'changeme123', 'is_superuser': False, 'is_staff': False},
        ]

        # Iterate through the list and create users, UserProfiles, and link to Players
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                # Create the User
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    is_superuser=user_data['is_superuser'],
                    is_staff=user_data['is_staff']
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {user.username}'))

                # Try to find the corresponding Player
                try:
                    player = Player.objects.get(username=user.username)
                except Player.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Player with username {user.username} does not exist'))
                    continue
                
                # Create the UserProfile and link it to the Player
                UserProfile.objects.create(user=user, player=player)
                self.stdout.write(self.style.SUCCESS(f'Successfully linked UserProfile for user: {user.username} to player: {player.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {user_data["username"]} already exists'))

        self.stdout.write(self.style.SUCCESS('Predefined users and UserProfiles creation complete'))
