from django.urls import include, path
from .views import home, about, Axeman_76, OldManReid, PapoQuim, Grum, UngleNelton, minecraft, players, discord, storytime

urlpatterns = [
    path('', home, name='home'),
    
    path('about', about, name='about'),
        path('about/Axeman_76', Axeman_76, name='Axeman_76'),
        path('about/Old_Man_Reid', OldManReid, name='Old Man Reid'),
        path('about/Papo_Quim', PapoQuim, name='Papo Quim'),
        path('about/Grum', Grum, name='Grum'),
        path('about/Ungle_Nelton', UngleNelton, name='Ungle Nelton'),
    
    path('minecraft', minecraft, name='minecraft'),
        path('minecraft/player', players, name='players'),
    
    
    path('discord', discord, name='discord'),
        path('discord/stories', storytime, name='storytime')
]