import yt_dlp
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import scrolledtext
from platformdirs import user_config_dir
from pathlib import Path
import tempfile
import pygpod
from PIL import Image
import ssl
import fixiTunes
import os
from typing import Any
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC, TCOM
from mutagen.id3._util import error
import threading
config_dir = Path(user_config_dir("YouTube Music Sync Tool", "WoodcraftWorld"))
config_dir.mkdir(parents=True, exist_ok=True)
prefs_file=Path.joinpath(config_dir, "prefs.txt")
if not prefs_file.exists():
    prefs_file.touch()
    prefs=open(prefs_file,"w")
    prefs.writelines(["https://music.youtube.com/playlist?list=PLcWIVMUpeHEvwq5M3qkZf9QIOBFI2wjeO\n", "C:\\Music\n", "0"])
    prefs.close()
#PROGRAM LOGIC
print('VERBOSE OUTPUT')
def add_log_text(log_text):
    textarea.config(state=tk.NORMAL)
    textarea.insert(tk.END, str(log_text)+"\n")
    textarea.see(tk.END)
    textarea.config(state=tk.DISABLED)
def tag_mp3(file_path, artist, title, album, videoid):
    try:
        audio = EasyID3(file_path)
    except Exception:
        audio = EasyID3()
    EasyID3.RegisterKey("composer","TCOM")
    audio["artist"] = artist
    audio["title"] = title
    audio["album"] = album
    audio["composer"] = videoid
    audio.save(file_path)

    add_log_text(f"Tagged '{file_path}' with Artist: '{artist}' and Title: '{title}'")

def download_and_crop_thumb(video_id: str, output_jpg_path: str):

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts: dict[str, Any] = {
            'skip_download': True,
            'writethumbnail': True,  
            'outtmpl': os.path.join(tmpdir, 'thumb'), 
            'quiet': True,                   
            'no_warnings': True
        }
        
        add_log_text(f"Downloading {video_id} Thumbnail")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
            ydl.download([video_url])
        downloaded_files = os.listdir(tmpdir)
        thumb_file = None
        for file in downloaded_files:
            if file.startswith('thumb.'):
                thumb_file = os.path.join(tmpdir, file)
                break
                
        if not thumb_file:
            raise FileNotFoundError("Could not download thumbnail")
        add_log_text("Cropping image to a square")
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
            add_log_text(f"Successfully saved thumbnail {output_jpg_path}")

def add_album_art(mp3_path, image_path, keepImage):
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
        if audio.tags is None:
            audio.add_tags()
        assert audio.tags is not None
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
        if keepImage != 0:
            os.remove(image_path)
        add_log_text(f"Successfully added album art to {os.path.basename(mp3_path)}")

    except Exception as e:
        add_log_text(f"An error occurred while tagging the file: {e}")

def download_audio(url, output_path):
    ydl_opts: dict[str, Any] = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s - %(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = filename.rsplit('.', 1)[0] + '.mp3'
        video_name = info_dict.get('title') or 'Unknown Title'
        uploader = info_dict.get('uploader') or 'Unknown Uploader'
        uploader = str(uploader).replace(" - Topic","")
        video_name = str(video_name).replace(uploader+" - ", "")
        video_name = str(video_name).replace(" - "+uploader,"")
        albumname = info_dict.get("album", "Video")
        videoid = info_dict.get('id')
        add_log_text(f"Video {video_name} by {uploader} downloaded")
        return [filename, uploader, video_name, albumname, videoid]

def get_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def get_folders(directory):
    return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def get_video_ids(playlist_url):
    ydl_opts: dict[str, Any] = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
        info = ydl.extract_info(playlist_url, download=False)
        return [entry['id'] for entry in info.get('entries', []) if 'id' in entry]
        
def updateStatus():
    statustext.configure(text=f"Status: {int(progressbar['value'])}/{progressbar['maximum']}")
def updatelist():
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    print(prefs1[1])
    folder=prefs1[1]
    enableStoreImages=prefs1[2]
    prefs.close()

    newpl=simpledialog.askstring("Change Playlist","Enter the URL of your playlist", parent=root)
    if newpl is not None:
        if "youtube.com/playlist?list=" not in newpl:
            messagebox.showerror("Information","Link is not to a YouTube or YouTube Music playlist, please enter the URL of a YouTube or YouTube Music playlist")
            updatelist()
            return("ok")
        prefs=open(prefs_file,"w")
        prefs.writelines([newpl+"\n", folder,enableStoreImages])
        prefs.close()
    else:
        messagebox.showwarning("Application","Cancel button pressed or text box left empty. No changes made.")
def updatedir():
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    print(prefs1[0])
    playlist=prefs1[0]
    folder=prefs1[1]
    enableStoreImages=prefs1[2]
    prefs.close()
    print(playlist)
    newdir=filedialog.askdirectory(parent=root, initialdir=folder)
    print(newdir)
    if newdir != "":
        prefs=open(prefs_file,"w")
        prefs.writelines([playlist, newdir+"\n", enableStoreImages])
        prefs.close()
        try:
            os.mkdir(newdir+"/db/")
            hyperlink = Path(newdir).joinpath("db", "0YouTube Music Sync Tool.url")
            """hyperlink.touch()
            hyperlink_file = open(hyperlink,"w")
            hyperlink_file.writelines(['[InternetShortcut]','URL=https://www.github.com/woodcraftworld/ytmusicsynctool','IconFile=https://woodcraftworld.github.io/image-hosting/ytmsticon.ico','IconIndex=0'])
            hyperlink_file.close()"""
        except:
            print("db exists!")
    else:
        messagebox.showwarning("Application","Cancel button pressed. No changes made.")
def startSync():
    threading.Thread(target=sync, daemon=True).start()
def sync():
    playlistbutton.config(state="disabled")
    folderbutton.config(state="disabled")
    syncbutton.config(state="disabled")
    savethumbs.config(state="disabled")
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    add_log_text(prefs1[1])
    folder=prefs1[1].strip()
    playlist=prefs1[0]
    keepJpegs=int(prefs1[2])
    prefs.close
    if keepJpegs == 2:
        print("Do nothing")
        #messagebox.showwarning("Application", "iPod support is in beta! iTunesDB corruptions may occur.")
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
    progressbar['maximum'] = len(download)+len(delete)
    updateStatus()
    for i in download:
        os.mkdir(folder+"/db/"+i)
        try:
            mp3 = download_audio(i,folder)
            tag_mp3(mp3[0],mp3[1],mp3[2],mp3[3],mp3[4])
            jpg=Path(mp3[0]).with_suffix('.jpg')
            download_and_crop_thumb(i, str(jpg))
            add_album_art(mp3[0],jpg,keepJpegs)
            if keepJpegs == 2:
                #Sync with iPod logic
                iPod=pygpod.Database(folder)
                iPod.add_track(mp3[0],composer=mp3[4])
                iPod.save()
                fixiTunes.fix_iTunesDB(folder)
                os.remove(mp3[0])

        except:
            add_log_text("Failed to download \""+i+"\", will not attempt to redownload unless the \""+i+"\" folder is deleted from db.")
        progressbar.step(1)
        updateStatus()
    for i in delete:
        if keepJpegs==2:
            for j in dbentries:
                if i in j:
                    iPod=pygpod.Database(folder)
                    for Track in iPod.tracks:
                        ##print (i)
                        #print (Track.composer)
                        if i in Track.composer:
                            print("This ran")
                            iPod.remove_track(Track, True)
                            iPod.save()
                            fixiTunes.fix_iTunesDB(folder)
                    os.rmdir(folder+"/db/"+i)
                    progressbar.step(1)
                    updateStatus()
        else:            
            for j in alreadyhave:
                if i in j:
                    os.remove(folder+"/"+j)
                    os.rmdir(folder+"/db/"+i)
                    progressbar.step(1)
                    updateStatus()
    add_log_text(download)
    add_log_text(delete)
    syncbutton.config(state="enabled")
    savethumbs.config(state="enabled")
    playlistbutton.config(state="enabled")
    folderbutton.config(state="enabled")
    '''if keepJpegs==2:
        if messagebox.askyesno("Application", "Do you want to open iOpenPod?"):
            subprocess.Popen(['iopenpod'])'''
def storeimages(event):
    prefs= open(prefs_file, "r")
    prefs1=prefs.readlines()
    playlist=prefs1[0]
    folder=prefs1[1]
    newCheckedState=savethumbs.current()
    prefs.close()
    prefs=open(prefs_file,"w")
    prefs.writelines([playlist, folder,str(newCheckedState)])
    prefs.close()
    folderButtonText()
def folderButtonText():
    if savethumbs.current() == 2:
        folderbutton.config(text="Choose iPod")
    else:
        folderbutton.config(text="Choose folder")

#GUI
root = tk.Tk()
prefs=open(prefs_file,"r")
prefs1=prefs.readlines()
state1=int(prefs1[2])
prefs.close
root.eval('tk::PlaceWindow . center')
root.title('YouTube Music Sync Tool')
icon=tk.PhotoImage(file="icon.png")
root.iconphoto(False,icon)
folderbutton = ttk.Button(root,command=updatedir, width=10)
folderbutton.grid(columnspan=2,column=1,row=1)
playlistbutton = ttk.Button(root,text="Choose Playlist",command=updatelist, width=10)
playlistbutton.grid(columnspan=2,column=3,row=1)
additionalOptions = ['Default option', 'Keep thumbnails', 'Sync with iPod']
#savethumbs = ttk.Checkbutton(root,text="Keep thumbnails",command=storeimages,variable=storeImagesCheck)
savethumbs = ttk.Combobox(root,values=additionalOptions,state="readonly",width=12)
savethumbs.grid(columnspan=2,column=1,row=2)
savethumbs.bind("<<ComboboxSelected>>",storeimages)
savethumbs.current(state1)
folderButtonText()
syncbutton = ttk.Button(root,text="Start sync",command=startSync,width=10)
syncbutton.grid(columnspan=1,column=3,row=2)
statustext = ttk.Label(root, text="Status: 0/0")
statustext.grid(column=3,row=3)
progressbar = ttk.Progressbar(root,length=255)
progressbar.grid(column=1,row=4,columnspan=4)
textarea = scrolledtext.ScrolledText(root,width=35,height=10)
textarea.grid(column=2,row=5,columnspan=2)
textarea.config(state=tk.DISABLED)
root.resizable(False, False)
root.mainloop()
