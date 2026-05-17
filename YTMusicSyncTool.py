import yt_dlp
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from platformdirs import user_config_dir
from pathlib import Path
import tempfile
from PIL import Image
import ssl
import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
ssl._create_default_https_context = ssl._create_unverified_context
config_dir = Path(user_config_dir("YouTube Music Sync Tool", "WoodcraftWorld"))
config_dir.mkdir(parents=True, exist_ok=True)
prefs_file=Path.joinpath(config_dir, "prefs.txt")
if not prefs_file.exists():
    prefs_file.touch()
    prefs=open(prefs_file,"w")
    prefs.writelines(["https://music.youtube.com/playlist?list=PLcWIVMUpeHEvwq5M3qkZf9QIOBFI2wjeO\n", "C:\\Music"])
    prefs.close()

#PROGRAM LOGIC
print('VERBOSE OUTPUT')
def tag_mp3(file_path, artist, title):
    try:
        audio = EasyID3(file_path)
    except Exception:
        audio = EasyID3()

    audio["artist"] = artist
    audio["title"] = title
    audio.save(file_path)

    print(f"Tagged '{file_path}' with Artist: '{artist}' and Title: '{title}'")

def download_and_crop_thumb(video_id: str, output_jpg_path: str):

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'skip_download': True,
            'writethumbnail': True,  
            'outtmpl': os.path.join(tmpdir, 'thumb'), 
            'quiet': True,                   
            'no_warnings': True
        }
        
        print(f"Downloading thumbnail for video ID: {video_id}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        downloaded_files = os.listdir(tmpdir)
        thumb_file = None
        for file in downloaded_files:
            if file.startswith('thumb.'):
                thumb_file = os.path.join(tmpdir, file)
                break
                
        if not thumb_file:
            raise FileNotFoundError("Could not download or locate the thumbnail from YouTube.")
        print("Cropping image to a center-focused square...")
        with Image.open(thumb_file) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            width, height = img.size
            min_dimension = min(width, height)
            left = (width - min_dimension) / 2
            top = (height - min_dimension) / 2
            right = (width + min_dimension) / 2
            bottom = (height + min_dimension) / 2
            
            cropped_img = img.crop((left, top, right, bottom))
            output_dir = os.path.dirname(output_jpg_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            cropped_img.save(output_jpg_path, 'JPEG', quality=95)
            print(f"Successfully saved square thumbnail to: {output_jpg_path}")

def add_album_art(mp3_path, image_path):
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"MP3 file not found at: {mp3_path}")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at: {image_path}")

    try:
        audio = MP3(mp3_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Front Cover',
                data=img_data
            )
        )
        audio.save()
        print(f"Successfully added album art to {os.path.basename(mp3_path)}")

    except Exception as e:
        print(f"An error occurred while tagging the file: {e}")

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s - %(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = filename.rsplit('.', 1)[0] + '.mp3'
        video_name = info_dict.get('title', 'Unknown Title')
        uploader = info_dict.get('uploader', 'Unknown Uploader')
        uploader = uploader.replace(" - Topic","")
        video_name = video_name.replace(uploader+" - ", "")
        video_name = video_name.replace(" - "+uploader,"")
        return [filename, uploader, video_name]

def get_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def get_folders(directory):
    return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def get_video_ids(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        return [entry['id'] for entry in info.get('entries', []) if 'id' in entry]
        

def updatelist():
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    print(prefs1[1])
    folder=prefs1[1]
    prefs.close()

    newpl=simpledialog.askstring("Change Playlist","Enter the URL of your playlist", parent=root)
    if newpl is not None:
        if "youtube.com/playlist?list=" not in newpl:
            messagebox.showerror("Information","Link is not to a YouTube or YouTube Music playlist, please enter the URL of a YouTube or YouTube Music playlist")
            updatelist()
            return("ok")
        prefs=open(prefs_file,"w")
        prefs.writelines([newpl+"\n", folder])
        prefs.close()
    else:
        messagebox.showwarning("Application","Cancel button pressed or text box left empty. No changes made.")
def updatedir():
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    print(prefs1[0])
    playlist=prefs1[0]
    folder=prefs1[1]
    prefs.close()
    print(playlist)
    newdir=filedialog.askdirectory(parent=root, initialdir=folder)
    print(newdir)
    if newdir != "":
        prefs=open(prefs_file,"w")
        prefs.writelines([playlist, newdir])
        prefs.close()
        try:
            os.mkdir(newdir+"/db/")
        except:
            print("db exists!")
    else:
        messagebox.showwarning("Application","Cancel button pressed. No changes made.")
    
def sync():
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    print(prefs1[1])
    folder=prefs1[1]
    playlist=prefs1[0]
    prefs.close
    videos=get_video_ids(playlist.removesuffix("\n"))
    download=[]
    delete=[]
    alreadyhave=get_files(folder)
    dbentries=get_folders(folder+"/db/")
    for i in videos:
        if i not in dbentries:
            download.append(i)
    for i in dbentries:
        if i not in videos:
            delete.append(i)
    #stepbar=100/(len(download)+len(delete))
    for i in download:
        os.mkdir(folder+"/db/"+i)
        try:
            mp3 = download_audio(i,folder)
            tag_mp3(mp3[0],mp3[1],mp3[2])
            jpg=Path(mp3[0]).with_suffix('.jpg')
            download_and_crop_thumb(i,jpg)
            add_album_art(mp3[0],jpg)
        except:
            print("Failed to download \""+i+"\", will not attempt to redownload unless the \""+i+"\" folder is deleted from db.")
        #progressbar.step(stepbar)
    for i in delete:
        for j in alreadyhave:
            if i in j:
                os.remove(folder+"/"+j)
                os.rmdir(folder+"/db/"+i)
                #progressbar.step(stepbar)
    print(download)
    print(delete)
#GUI
root = Tk()
root.eval('tk::PlaceWindow . center')
root.title('YouTube Music Sync Tool')
ttk.Button(root,text="Change Folder",command=updatedir).grid(columnspan=2,column=1,row=1)
ttk.Button(root,text="Change Playlist",command=updatelist).grid(columnspan=2,column=3,row=1)
ttk.Button(root,text="Sync",command=sync).grid(columnspan=2,column=2,row=2)
#progressbar = ttk.Progressbar(root,length=255).grid(column=1,row=3,columnspan=4)
root.resizable(False, False)
root.mainloop()
