from django.db import models
from django.utils.text import slugify


class CartographyMap(models.Model):
    MAP_TYPES = [
        ('Official', 'Official UN Map'),
        ('FarColony', 'Official UN Far Colonies Map'),
        ('Territory', 'UN Territory Map'),
        ('Infrastructure', 'Infrastructure Map'),
        ('Evaluation', 'Evaluation Map')
    ]

    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, blank=True, editable=False)

    map_date = models.DateField(db_index=True)
    type = models.CharField(max_length=100, choices=MAP_TYPES)
    description = models.TextField(max_length=200, blank=True)
    changes = models.TextField(blank=True)

    map_a = models.ImageField(upload_to="cartography/maps/")
    map_b = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)
    map_c = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)
    map_d = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)
    map_e = models.ImageField(upload_to="cartography/maps/", blank=True, null=True)

    def __str__(self):
        return f"{self.title or self.type} ({self.map_date})"

    @property
    def default_map(self):
        return self.map_a

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.type}-{self.map_date}")
            slug = base_slug
            counter = 2

            while CartographyMap.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)