import os
import shutil
from pathlib import Path
from iTunesDB_Writer import write_itunesdb
from iTunesDB_Writer.mhit_writer import TrackInfo
from iTunesDB_Writer.mhbd_writer import extract_db_info
from SyncEngine._db_io import read_existing_database
from SyncEngine._track_conversion import track_dict_to_info

IPOD_PATH = "/Volumes/EYEPOD NANO"
EXISTING_ITDB = os.path.join(IPOD_PATH, "iPod_Control", "iTunes", "iTunesDB")

# Example: copy a file to the iPod first
src = "/Users/woodcraftworld/Documents/436814_Phobos.mp3"
dst = os.path.join(IPOD_PATH, "iPod_Control", "Music", "F00", "phobos.mp3")
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copy2(src, dst)

# Create a TrackInfo for the new track
new_track = TrackInfo(
    title="My Song",
    location=":iPod_Control:Music:F00:phobos.mp3",
    size=os.path.getsize(dst),
    filetype="mp3",
    bitrate=320,
    sample_rate=44100,
    artist="Artist Name",
    album="Album Name",
    year=2024,
    track_number=1,
    total_tracks=10,
)

# Parse the existing database and convert parsed tracks into TrackInfo objects
existing_tracks = []
master_playlist_name = "MyEyePod"
master_playlist_id = None
podcast_master_playlist_name = None
podcast_master_playlist_id = None
if os.path.exists(EXISTING_ITDB):
    existing_data = read_existing_database(Path(IPOD_PATH))
    existing_tracks = [track_dict_to_info(track) for track in existing_data.get("tracks", [])]

    # Preserve the original master playlist name and IDs if present
    for pl in existing_data.get("dataset2_standard_playlists", []):
        if pl.get("master_flag"):
            master_playlist_name = pl.get("Title", master_playlist_name)
            master_playlist_id = pl.get("playlist_id")
            break

    for pl in existing_data.get("dataset3_podcast_playlists", []):
        if pl.get("master_flag"):
            podcast_master_playlist_name = pl.get("Title")
            podcast_master_playlist_id = pl.get("playlist_id")
            break

# Build the final track list; include existing tracks and the new one
tracks = existing_tracks + [new_track]

# Preserve device-specific IDs and hash settings from current database
reference_info = None
if os.path.exists(EXISTING_ITDB):
    reference_info = extract_db_info(EXISTING_ITDB)

ok = write_itunesdb(
    IPOD_PATH,
    tracks,
    reference_itdb_path=EXISTING_ITDB,
    master_playlist_name=master_playlist_name,
    master_playlist_id=master_playlist_id,
    podcast_master_playlist_name=podcast_master_playlist_name,
    podcast_master_playlist_id=podcast_master_playlist_id,
    backup=True,
)

print("Write succeeded:", ok)