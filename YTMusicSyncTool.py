import yt_dlp
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import ssl
import os
from mutagen.easyid3 import EasyID3
ssl._create_default_https_context = ssl._create_unverified_context


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
        info_dict = ydl.extract_info(url, download=True)  # Extract info and download
        filename = ydl.prepare_filename(info_dict)  # Get the original filename
        filename = filename.rsplit('.', 1)[0] + '.mp3'  # Ensure MP3 extension
        video_name = info_dict.get('title', 'Unknown Title')
        uploader = info_dict.get('uploader', 'Unknown Uploader')
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
    prefs= open("prefs", "r")
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
        prefs=open("prefs","w")
        prefs.writelines([newpl+"\n", folder])
        prefs.close()
    else:
        messagebox.showwarning("Application","Cancel button pressed or text box left empty. No changes made.")
def updatedir():
    prefs= open("prefs", "r")
    prefs1=prefs.readlines()
    print(prefs1[0])
    playlist=prefs1[0]
    folder=prefs1[1]
    prefs.close()
    print(playlist)
    newdir=filedialog.askdirectory(parent=root, initialdir=folder)
    print(newdir)
    if newdir != "":
        prefs=open("prefs","w")
        prefs.writelines([playlist, newdir])
        prefs.close()
        try:
            os.mkdir(newdir+"/db/")
        except:
            print("db exists!")
    else:
        messagebox.showwarning("Application","Cancel button pressed. No changes made.")
    
def sync():
    prefs= open("prefs", "r")
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
        mp3 = download_audio(i,folder)
        os.mkdir(folder+"/db/"+i)
        tag_mp3(mp3[0],mp3[1],mp3[2])
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