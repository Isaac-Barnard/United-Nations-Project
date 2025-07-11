import os
import base64
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.conf import settings
from .utilities.youtube import get_latest_video_id
from players_api.models import User

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
    special_players = ["Axeman_76", "Cowman7", "OldManReidGaming", "vlueban", "Tallerfiber1", "YerLoss"]

    players = User.objects.all().values('username', 'face_image')

    players_with_faces = []
    for player in players:
        face_image_data = None
        if player['face_image']:
            # Handle different data types
            if isinstance(player['face_image'], (bytes, memoryview)):
                # Convert binary data to base64
                face_bytes = bytes(player['face_image']) if isinstance(player['face_image'], memoryview) else player['face_image']
                face_b64 = base64.b64encode(face_bytes).decode('utf-8')
                face_image_data = f"data:image/png;base64,{face_b64}"
            elif isinstance(player['face_image'], str):
                # Already a base64 string
                face_image_data = f"data:image/png;base64,{player['face_image']}"

        players_with_faces.append({
            'username': player['username'],
            'face_image': face_image_data,
            'is_special': player['username'] in special_players
        })

    return render(request, 'players.html', {'players': players_with_faces})

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

def home(request):
    video_id = None
    try:
        video_id = get_latest_video_id()
    except Exception as e:
        print(f"Error fetching latest YouTube video: {e}")
    context = {'video_id': video_id}
    return render(request, 'wss_home.html', context)