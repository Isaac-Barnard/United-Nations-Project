import os
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.conf import settings


# Create your views here.
def home(request):
    return render(request, 'wss_home.html')

def about(request):
    return render(request, 'about.html')

def Axeman_76(request):
    return render(request, 'Axeman_76.html')

def OldManReid(request):
    return render(request, 'Old_Man_Reid.html')

def PapoQuim(request):
    return render(request, 'Papo_Quim.html')

def Grum(request):
    return render(request, 'Grum.html')

def UngleNelton(request):
    return render(request, 'Ungle_Nelton.html')

def minecraft(request):
    return render(request, 'minecraft.html')

def players(request):
    return render(request, 'players.html')

def discord(request):
    return render(request, 'discord.html')

def storytime(request):
    template = loader.get_template('storytime.html')

    dirlist = [file for file in os.listdir(settings.STATIC_ROOT / 'stories') if len(file.split(".txt")) == 2]
    dirlist.sort()

    # Cool one-liner to get the filename and title of the story text files
    storylist = [{'filename' : filename.split(".txt")[0], 'title' : ' '.join([word.capitalize() for word in filename.split(".txt")[0].split("_")])} for filename in dirlist]

    context = {
        'story_list': storylist
    }
    
    return HttpResponse(template.render(context, request))