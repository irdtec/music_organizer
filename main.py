# Python LINQ
# https://viralogic.github.io/py-enumerable/

import os,shutil,pathlib
import mutagen
from mutagen.id3 import ID3
from py_linq import Enumerable


# GLobal vars
folder = r"F:\World"
output_folder = r"F:\World\CUSTOM_PROCESSED"
allowed_extensions = [".mp3",".flac"]

def RemoveSpecialChars(item):
    special_chars= ['\\','/',"\"",";",":",'* . *','*.*','>','<']
    for special in special_chars:
        item = item.replace(special,"")    
    return item

def ScanFolder():
    # Custom class
    from music import Music

    # Config    
    allowed_files = []

    # get file list from folder    
    

    for root, dirs, files in os.walk(folder):
        for name in files:                  
            extension = pathlib.Path(name).suffix
            if extension in allowed_extensions:
                if "ORDERED MUSIC" in name: # Do not process the ordered Music folder
                    print("skipped {}".format(name))                    
                else:
                    allowed_files.append(os.path.join(root,name))
                    # print(os.path.join(root,name))
    print("Files to be processed: {}".format(len(allowed_files)) )
    return allowed_files

def PrepareAttributes(musicFiles):
    from music import Music
    # Scan for tags on each file
    music_files = []

    for f in musicFiles:
        music = Music()
        music.file_path = f
        music.file_name = pathlib.Path(f).name
        # music.folder = folder
        try:
            m = mutagen.File(f)
            if f.endswith(".flac"):            
                music.album = m.tags['ALBUM'][0]
                music.genre = m.tags['GENRE'][0]
                music.artist = m.tags['ARTIST'][0]            
                # print(music.album,music.genre,music.artist)
            else:        
                for key in m.keys():
                    # Don't print CODE for album art
                    if 'apic' in key.lower():
                        continue
                    if 'talb' in key.lower():
                        music.album = str(m.tags.getall(key)[0][0])
                    if 'tcon' in key.lower():
                        music.genre = str(m.tags.getall(key)[0][0])
                    if 'tpe1' in key.lower():
                        music.artist = str(m.tags.getall(key)[0][0])
                
            music_files.append(music)
        except:
            print("No tags found for file {}".format(f))
    return music_files

def PrepareFolders(musicList):
    mlinq = Enumerable(musicList)
    # Loop Every item and begin creating folders
    genres = mlinq.distinct(lambda x: x.genre).select(lambda x: x.genre)
    
    #For each Genre create the folder and begin loop
    for genre in genres:
        # Create folder    
        if  genre == "":
            continue
        # print(genre)
        genre_folder = os.path.join(output_folder,RemoveSpecialChars(genre))
        if not os.path.exists(genre_folder):
            os.makedirs(genre_folder)

        # Search artist
        artist_list = mlinq.where(lambda x: x.genre == genre).select(lambda x: x.artist).distinct(lambda x: x)
        for artist in artist_list:
            artist_folder = os.path.join(genre_folder, RemoveSpecialChars(artist))
            if not os.path.exists(artist_folder):
                os.makedirs(artist_folder)

            # Search album name
            album_list = mlinq.where(lambda x: x.artist == artist and x.genre==genre).select(lambda x: x.album).distinct(lambda x: x)
            for album  in album_list:
                album_folder = os.path.join(artist_folder, RemoveSpecialChars(album))
                if not os.path.exists(album_folder):
                    os.makedirs(album_folder)

                # get files with that album and move to new destination
                file_list = mlinq.where(lambda x: x.album == album and x.artist == artist and x.genre == genre)
                for f in file_list:
                    try:
                        destination = os.path.join(album_folder,f.file_name)
                        shutil.move(f.file_path, destination)
                        # print(destination)
                    except:
                        print("File could not be moved: " + f.album + " > " + f.artist + " > " + f.file_name)
    
    print("Music classification done!")


musicFiles = ScanFolder()
preparedFiles = PrepareAttributes(musicFiles)
PrepareFolders(preparedFiles)