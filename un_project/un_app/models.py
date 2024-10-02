from django.db import models

class Nation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation  = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.abbreviation


class Player(models.Model):
    username = models.CharField(max_length=100, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='players')
    un_rep = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    def num_buildings_built(self):
        return self.main_builds.count()


class Territory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    #nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='territories')

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=100, unique=True)
    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, related_name='buildings', null=True)
    owner = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='owned_buildings')
    main_builders = models.ManyToManyField(Player, related_name='main_builds')
    y_level_high_pt = models.FloatField(null=True)
    y_level_ground = models.FloatField(null=True)
    year_completed = models.IntegerField(null=True)
    completed = models.BooleanField(default=True)
    x_coordinate = models.CharField(max_length=50)
    z_coordinate = models.CharField(max_length=50)
    historic_site = models.BooleanField(default=False) 
    architectural_genius = models.BooleanField(default=False) 
    mopq_award = models.CharField(max_length=50, null=True, blank=True)
    architectural_style = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def height(self):
        if self.y_level_high_pt is None or self.y_level_ground is None:
            return 0
        return self.y_level_high_pt - self.y_level_ground
    
    @property
    def coordinates(self):
        return f"{self.x_coordinate}/~/ {self.z_coordinate}"