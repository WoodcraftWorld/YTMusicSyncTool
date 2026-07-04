# YTMusicSyncTool
A tool to sync a YouTube or YouTube Music playlist to MP3 files on an MP3 player or iPod*

_*iPod support is in beta. most iPods are supported, but not the iPod nano 6th gen or 7th gen. iPhone, iPad, and iPod touch are not supported. For unsupported models, you can sync to a folder on your local drive, then sync the songs to your iPod with an iTunes/Finder or an alternative like iOpenPod._

# Installation Instructions

Latest version of Python 3 must be installed from http://python.org on macOS or Windows\
Python must be installed to PATH on Windows\
On linux only you will need to install TKINTER with these commands\
Debian/Ubuntu based distros:\
`sudo apt install python3-tk`\
Fedora/CentOS based distros:\
`sudo dnf install python3-tkinter`\
Arch based distros:\
`sudo pacman -S tk`

After python is installed, you must open terminal or PowerShell and run:\
`pip install -r /path/to/requirements.txt`

You also need to install FFMpeg, which can be done by\
Windows:\
Open powershell as administrator and run:\
`winget install ffmpeg`\
macOS (10.15+, precompiled binaries):\
Install homebrew from http://brew.sh \
Open Terminal and run:\
`brew install ffmpeg`\
macOS (10.5+, compiles on your Mac):\
Install MacPorts from https://macports.org/install.php#installing \
_NOTE: App requires Python 3.11, which still needs OS X 10.9, even if FFMpeg can run on 10.5._ \
Open Terminal and run:\
`sudo port install ffmpeg`\
Linux:\
Install FFMpeg from your distro's package manager\
Debian/Ubuntu based distros:\
`sudo apt install ffmpeg`\
Fedora/CentOS based distros:\
`sudo dnf install ffmpeg`\
Arch based distros:\
`sudo pacman -S ffmpeg`

How to open\
On Linux open terminal and run:\
`chmod +x ./run_linux.sh`\
then double click `run_linux.sh` or run:\
`./run_linux.sh`\
How to open\
On macOS open terminal and run:\
`chmod +x ./run_osx`\
then double click `run_osx` or run:\
`./run_osx`\
On Windows, double click `run_windows.cmd` or open PowerShell and run:\
`./run_windows.cmd`
