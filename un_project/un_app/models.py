from django.db import models

class Nation(models.Model):
    name = models.CharField(max_length=100)
    #description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    username = models.CharField(max_length=100)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='players')
    un_rep = models.BooleanField(default=False)
    # Temporary field to force a migration
    temp_field = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.username


class Territory(models.Model):
    name = models.CharField(max_length=100)
    #nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='territories')

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=100)
    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='buildings')
    owner = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='owned_buildings')
    main_builder = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='main_builds')
    y_level_high_pt = models.FloatField()
    y_level_ground = models.FloatField()
    height = models.FloatField()
    year_completed = models.IntegerField()
    coordinates = models.CharField(max_length=50)
    historic_site = models.BooleanField(default=False)
    architectural_genius = models.BooleanField(default=False)
    moPQ_award = models.BooleanField(default=False)
    architectural_style = models.CharField(max_length=100, null=True, blank=True)
    y_level_lowest = models.FloatField(null=True, blank=True)
    height_below_ground = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name