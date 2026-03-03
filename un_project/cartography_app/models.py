from django.db import models

class CartographyMap(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    # Primary chronological sorting
    map_date = models.DateField(db_index=True)

    type = models.TextField(blank=True)

    # Map Variants
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