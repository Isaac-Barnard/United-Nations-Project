from django.db import migrations, models

def assign_unique_usernames(apps, schema_editor):
    Player = apps.get_model('un_app', 'Player')
    
    for index, player in enumerate(Player.objects.all(), start=1):
        # Generate a unique username for each player (e.g., player1, player2, etc.)
        player.username = f"player{index}"
        player.save()

class Migration(migrations.Migration):

    dependencies = [
        ('un_app', '0025_remove_buildingevaluation_evaluation_price_and_more'),
    ]

    operations = [
        # Add the username field, allowing NULL temporarily
        migrations.AddField(
            model_name='player',
            name='username',
            field=models.CharField(max_length=100, unique=True, null=True),
        ),
        # Run the function to assign unique usernames
        migrations.RunPython(assign_unique_usernames),
        # Alter the username field to make it non-nullable after values are set
        migrations.AlterField(
            model_name='player',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
