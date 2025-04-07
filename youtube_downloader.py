import os
import subprocess
import shutil
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import requests

def check_internet_connection():
    """Vérifie la connexion internet"""
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def merge_video_audio(video_path, audio_path, output_path, subtitle_path=None):
    """Fusionne la vidéo et l'audio, et ajoute les sous-titres si disponibles"""
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if subtitle_path:
        # Si des sous-titres sont disponibles, on les intègre dans le fichier vidéo
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-i', subtitle_path,
            '-c:v', 'copy',  # Copier la vidéo sans recodage
            '-c:a', 'aac',
            '-b:a', '320k',  # Audio en haute qualité
            '-c:s', 'mov_text',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-map', '2:s:0',
            output_path
        ]
    else:
        # Sans sous-titres, on fait une fusion simple
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',  # Copier la vidéo sans recodage
            '-c:a', 'aac',
            '-b:a', '320k',  # Audio en haute qualité
            output_path
        ]
    
    try:
        print("Fusion des fichiers...")
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la fusion : {e}")
        return False

def download_video(url, output_dir="downloads"):
    """Télécharge une vidéo YouTube avec la meilleure qualité disponible"""
    if not check_internet_connection():
        print("Erreur : Pas de connexion Internet")
        return False

    # Créer les dossiers nécessaires
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Connexion à YouTube
        print("Connexion à YouTube...")
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Titre : {yt.title}")

        # Télécharger la vidéo en meilleure qualité H.264
        print("\nTéléchargement de la vidéo...")
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not video_stream:
            print("Erreur : Impossible de trouver un flux vidéo valide")
            return False

        print(f"Qualité vidéo sélectionnée : {video_stream.resolution}")
        video_path = video_stream.download(output_path=temp_dir)

        # Télécharger l'audio en meilleure qualité
        print("\nTéléchargement de l'audio...")
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        if not audio_stream:
            print("Erreur : Impossible de trouver un flux audio valide")
            return False

        print(f"Qualité audio sélectionnée : {audio_stream.abr}kbps")
        audio_path = audio_stream.download(output_path=temp_dir)

        # Télécharger les sous-titres si disponibles
        subtitle_path = None
        try:
            captions = yt.captions
            if captions:
                # Essayer d'abord les sous-titres en français
                subtitle = captions.get('fr') or captions.get('fr-FR')
                if not subtitle:
                    # Si pas de français, prendre le premier sous-titre disponible
                    subtitle = next(iter(captions.values()))
                
                if subtitle:
                    print("\nTéléchargement des sous-titres...")
                    subtitle_path = subtitle.download(title=yt.title, output_path=temp_dir)
                    print("Sous-titres téléchargés avec succès")
        except Exception as e:
            print(f"Note : Impossible de télécharger les sous-titres ({e})")

        # Créer les chemins des fichiers
        temp_output = os.path.join(temp_dir, f"{yt.title}.mp4")
        final_path = os.path.join(output_dir, f"{yt.title}.mp4")
        
        # Fusionner la vidéo, l'audio et les sous-titres
        print("\nFusion des fichiers...")
        if merge_video_audio(video_path, audio_path, temp_output, subtitle_path):
            print("Fusion réussie !")
            
            # Copier le fichier final dans le dossier downloads
            print("Copie du fichier final...")
            shutil.copy2(temp_output, final_path)
            print(f"Fichier final copié : {final_path}")
            
            # Nettoyer le dossier temporaire
            try:
                shutil.rmtree(temp_dir)
                print("Dossier temporaire supprimé")
            except Exception as e:
                print(f"Note : Impossible de supprimer le dossier temporaire ({e})")
            
            return True
        else:
            print("La fusion a échoué, les fichiers temporaires sont conservés dans le dossier 'temp'")
            return False

    except Exception as e:
        print(f"Erreur : {e}")
        return False

def download_playlist(url, output_dir="downloads"):
    """Télécharge toutes les vidéos d'une playlist YouTube"""
    if not check_internet_connection():
        print("Erreur : Pas de connexion Internet")
        return False

    try:
        # Créer le dossier de téléchargement
        os.makedirs(output_dir, exist_ok=True)

        # Récupérer la playlist
        print("Récupération de la playlist...")
        playlist = Playlist(url)
        print(f"Titre de la playlist : {playlist.title}")
        print(f"Nombre de vidéos : {len(playlist.video_urls)}")

        # Télécharger chaque vidéo
        for i, video_url in enumerate(playlist.video_urls, 1):
            print(f"\nTéléchargement de la vidéo {i}/{len(playlist.video_urls)}")
            video = YouTube(video_url)
            output_path = os.path.join(output_dir, f"{video.title}.mp4")
            download_video(video_url, output_dir)

        return True

    except Exception as e:
        print(f"Erreur : {e}")
        return False

def main():
    print("=== YouTube Downloader ===")
    print("1. Télécharger une vidéo")
    print("2. Télécharger une playlist")
    
    choice = input("\nChoix (1 ou 2) : ")
    url = input("URL YouTube : ")
    
    if choice == "1":
        if download_video(url):
            print("\nTéléchargement terminé avec succès !")
        else:
            print("\nÉchec du téléchargement.")
    elif choice == "2":
        if download_playlist(url):
            print("\nTéléchargement de la playlist terminé avec succès !")
        else:
            print("\nÉchec du téléchargement de la playlist.")
    else:
        print("Choix invalide.")

if __name__ == "__main__":
    main() 