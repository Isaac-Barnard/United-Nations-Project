from django.db import models

class CartographyMap(models.Model):
    MAP_TYPES = [
        ('Official', 'Official UN Map'),
        ('Territory', 'UN Territory Map'),
        ('Infastructure', 'Infastructure Map'),
        ('Evaluation', 'Evaluation Map')
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    map_date = models.DateField(db_index=True)
    type = models.CharField(max_length=100, choices=MAP_TYPES)
    description = models.TextField(blank=True)

    map_a = models.ImageField(upload_to="cartography/maps/")
    map_b = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)
    map_c = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)
    map_d = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)
    map_e = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.map_date})"

    @property
    def default_map(self):
        return self.map_a