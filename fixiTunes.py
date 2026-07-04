'''
    This file only exists due a bug in pygpod. This bug results in iTunes not properly being able to access the iPod
    and some iPod models having corrupted iTunesDB files. I have reported these bugs to the developer and will remove
    this dependency when the bugs are fixed.
'''
import os
from iTunesDB_Parser.ipod_library import load_ipod_library
from iTunesDB_Writer import write_itunesdb
from iTunesDB_Writer.mhit_writer import TrackInfo
from SyncEngine._track_conversion import track_dict_to_info
def fix_iTunesDB(IPOD_PATH):
    EXISTING_ITDB = os.path.join(IPOD_PATH, "iPod_Control", "iTunes", "iTunesDB")
    existing_tracks: list[TrackInfo] = []
    if os.path.exists(EXISTING_ITDB):
        library = load_ipod_library(EXISTING_ITDB, merge_playcounts=False)
        if library:
            existing_tracks = [track_dict_to_info(track) for track in library.get("mhlt", [])]

    tracks = existing_tracks

    ok = write_itunesdb(
        IPOD_PATH,
        tracks,
        reference_itdb_path=EXISTING_ITDB,
        backup=True,
    )

    return ("Write succeeded:", ok)