import bz2
import os
import sqlite3
from typing import List
import h5py
from lxml import etree
import xml.etree.ElementTree as ET
from tqdm import tqdm
import numpy as np

from gamelog_to_states import gamelogToStates


#redefine numGames so don't cook my computer
NUMGAMES = 300


dbfile = 'es4p.db'
con = sqlite3.connect(dbfile)
cur = con.cursor()
res = cur.execute(f"SELECT log_id, log_content FROM logs")


game_logs = []
for i in range(NUMGAMES):
    game_logs.append(res.fetchone())

con.close()


### takes a game_log from the .db file, decrompresses it, formats the xml, returns (game_id, game_replay)
def convertLog(log):
    game_id = log[0]
    blob = log[1]

    XML = etree.XML

    decompress = bz2.decompress

    content = decompress(blob)

    xml = XML(content, etree.XMLParser(recover=True))
    rough_string = ET.tostring(xml, encoding='unicode')
    root = ET.fromstring(rough_string)

    game_replay = []
    for element in root:
        header_name = element.tag
        attributes_dict = element.attrib
        game_replay.append((header_name ,  attributes_dict))

    return game_id, game_replay



STATE_TYPE_DIRS = {
    0: "Riichi",
    1: "Chi",
    2: "Pon",
    3: "Kan"
}


# appends the label, and saves to file
def saveFileForStateType(states: np.ndarray,
                        labels: np.ndarray,
                        game_id: str,
                        statetype: int,
                        year: int,
                        path_to_save_in: str):

    if len(states) == 0:
        return

    directory = os.path.join(path_to_save_in,
                             "mahjong_dataset",
                             str(year),
                             STATE_TYPE_DIRS[statetype])


    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, f"{game_id}.npz")

    np.savez_compressed(file_path, states)



def saveToFile(log, year, path_to_save_in):
    game_id, game = convertLog(log)

    riichi_states, riichi_labels, chi_states, chi_labels, pon_states, pon_labels, kan_states, kan_labels = gamelogToStates(game)

    saveFileForStateType(riichi_states, riichi_labels game_id, 0, year, path_to_save_in)
    saveFileForStateType(chi_states, chi_labels, game_id, 1 , year, path_to_save_in)
    saveFileForStateType(pon_states, pon_labels, game_id, 2 , year, path_to_save_in)
    saveFileForStateType(kan_states, kan_labels, game_id, 3 , year, path_to_save_in)


def saveFilesPerYear(year,
                     path_to_save_in: str,
                     path_to_db_file: str,
                     numFiles = None
    ):
    dbfile = path_to_db_file

    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM logs")

    numGames = res.fetchone()[0]

    res = cur.execute(f"SELECT log_id, log_content FROM logs WHERE year = {year}")

    if numFiles:
        numGames = numFiles

    for game_num in tqdm(range(numGames), desc=f"Processing {year}"):
        log = res.fetchone()

        try:
            saveToFile(log, year, path_to_save_in)
        except Exception as e:
            print(f"An error occurred with i={game_num}: {e}")


    con.close()



TOTAL_ROWS = 72_000_000
CHUNK_SIZE = 2048
COMPRESSION = "gzip"



def saveAll(years: List[int], path_to_save_in: str, path_to_db_file: str):
    with (open("C:\\Users\\msaba\\Documents\\GitHub\\riichi-dataset\\es4p.db", "r") as db_file,
         h5py.File(r"C:\Users\msaba\Documents\GitHub\actual-dataset\hanchan_hp5\file.h5", "w") as h5_file):

        con = sqlite3.connect(db_file)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM logs")

        datasets_info = [
            ('riichi_states', 374),
            ('riichi_labels', 2),
            ('chi_states', 374),
            ('chi_labels', 2),
            ('pon_states', 374),
            ('pon_labels', 2),
            ('kan_states', 374),
            ('kan_labels', 2)
        ]



        for name, size in datasets_info:
            h5_file.create_dataset(name,
                                   shape=(0, size),
                                   maxshape=(None, size),
                                   compression=COMPRESSION,
                                   chunks=(CHUNK_SIZE, size)
                                   )
