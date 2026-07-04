import plistlib
import tkinter as tk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import scrolledtext
from platformdirs import user_config_dir
from pathlib import Path
import tempfile
from PIL import Image
import ssl
import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import threading
import subprocess

config_dir = Path(user_config_dir("YouTube Music Sync Tool", "WoodcraftWorld"))
config_dir.mkdir(parents=True, exist_ok=True)
prefs_file=Path.joinpath(config_dir, "SyncToolPreferences.plist")
preference_data = {
    'Name':'YouTube Music Sync Tool',
    'Version':'2.0',
    'LastUsed':'D:\\Music\\YTMSTDatabase.plist'
}
if not prefs_file.exists():
    with open(prefs_file, 'wb') as fp:
        plistlib.dump(preference_data, fp)
else:
    with open(prefs_file, 'rb') as fp:
        preference_data = plistlib.load(fp)

def createDatabase(file_path, key, data):
    with open(file_path, 'rb') as fp:
        data = plistlib.load(fp)
    data[key] = data
    data['NewFeatureEnabled'] = False

    # 3. Save the changes back to the file
    with open(file_path, 'wb') as fp:
        plistlib.dump(data, fp)