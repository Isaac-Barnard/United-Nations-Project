from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from un_app.models import Player, UserProfile
from django.db import transaction

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

        for user_data in users_data:
            try:
                with transaction.atomic():
                    # Check if player exists first
                    try:
                        player = Player.objects.get(username=user_data['username'])
                    except Player.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'Player {user_data["username"]} does not exist - skipping user creation')
                        )
                        continue

                    # Check if user already exists
                    user, user_created = User.objects.get_or_create(
                        username=user_data['username'],
                        defaults={
                            'email': user_data['email'],
                            'is_superuser': user_data['is_superuser'],
                            'is_staff': user_data['is_staff']
                        }
                    )

                    if user_created:
                        user.set_password(user_data['password'])
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully created user: {user.username}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'User {user_data["username"]} already exists')
                        )

                    # Create UserProfile if it doesn't exist
                    user_profile, profile_created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={'player': player}
                    )

                    if profile_created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully created UserProfile linking user: {user.username} to player: {player.username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'UserProfile for {user.username} already exists'
                            )
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {user_data["username"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('User and UserProfile creation process complete'))