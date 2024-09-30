from django.db import models

class Nation(models.Model):
    name = models.CharField(max_length=100)
    #name = models.CharField(max_length=100)
    #name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Player(models.Model):
    username = models.CharField(max_length=100)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='players')
    un_rep = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    def num_buildings_built(self):
        return self.main_builds.count()


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
    year_completed = models.IntegerField()
    x_coordinate = models.CharField(max_length=50)
    z_coordinate = models.CharField(max_length=50)
    historic_site = models.BooleanField(default=False)
    architectural_genius = models.BooleanField(default=False)
    moPQ_award = models.BooleanField(default=False)
    architectural_style = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def height(self):
        return self.y_level_high_pt - self.y_level_ground
    
    @property
    def coordinates(self):
        return f"{self.x_coordinate}/~/ {self.z_coordinate}"