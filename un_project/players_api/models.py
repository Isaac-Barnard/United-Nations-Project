from django.db import models

# Create your models here.
class User(models.Model):
    username = models.TextField()
    uuid = models.UUIDField(primary_key=True)
    skin_data = models.TextField(blank=True, null=True)
    skin_image = models.BinaryField(blank=True, null=True)
    face_image = models.BinaryField(blank=True, null=True)
    is_slim = models.BooleanField(default=True)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    z = models.IntegerField(blank=True, null=True)
    dimension = models.TextField(blank=True, null=True)
    health = models.IntegerField(blank=True, null=True)
    lastdeathx = models.IntegerField(blank=True, null=True)
    lastdeathy = models.IntegerField(blank=True, null=True)
    lastdeathz = models.IntegerField(blank=True, null=True)
    lastdeathdim = models.TextField(blank=True, null=True)
    xplevel = models.IntegerField(blank=True, null=True)
    xppercent = models.FloatField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'users'

class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)  # SERIAL PRIMARY KEY
    uuid = models.ForeignKey(
        'User',  # Reference the `User` model defined earlier
        on_delete=models.CASCADE,  # ON DELETE CASCADE
        db_column='uuid',  # Match the database column name
    )
    inventory_type_id = models.IntegerField()
    slot = models.IntegerField()
    item_id = models.TextField()
    amount = models.IntegerField()
    name = models.TextField()
    custom_name = models.TextField(blank=True, null=True)
    enchantments = models.TextField(blank=True, null=True)
    book_title = models.TextField(blank=True, null=True)
    book_author = models.TextField(blank=True, null=True)
    arrow_effect = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False  # Prevent Django from managing the schema
        db_table = 'inventory'  # Match the table name in the database
        unique_together = (('uuid', 'inventory_type_id', 'slot'),)  # UNIQUE constraint

class Players_Online(models.Model):
    n = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'players_online'