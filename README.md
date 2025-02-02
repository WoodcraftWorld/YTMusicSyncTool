# YTMusicSyncTool
A tool to sync a YouTube or YouTube Music playlist to MP3 files on an MP3 player

# Installation Instructions

Latest version of Python 3 must be installed from http://python.org on MacOS or Windows (you can't use Homebrew on MacOS for this)\
Python must be installed to PATH on Windows\
On linux only you will need to install TKINTER with these commands\
Debian/Ubuntu based distros:\
`sudo apt install python3-tk`\
Fedora/CentOS based distros:\
`sudo dnf install python3-tkinter`\
Arch based distros:\
`sudo pacman -S tk`\

After python is installed, you must open terminal or PowerShell and run:\
`pip install yt_dlp`\
`pip install mutagen`\

You also need to install FFMpeg, which can be done by\
Windows:\
Open powershell as administrator and run:\
`winget install ffmpeg`\
MacOS:\
Install homebrew from http://brew.sh\
Open Terminal and run:\
`brew install ffmpeg`\
Linux:\
Install FFMpeg from your distro's package manager\
Debian/Ubuntu based distros:\
`sudo apt install ffmpeg`\
Fedora/CentOS based distros:\
`sudo dnf install ffmpeg`\
Arch based distros:\
`sudo pacman -S ffmpeg`\

How to open\
On MacOS/Linux open terminal and run:\
`chmod +x ./run_unix.sh`\
then double click `run_unix.sh` or run:\
`./run_unix.sh`\
On Windows, double click `run_windows.cmd` or open PowerShell and run:\
`./run_windows.cmd`\
