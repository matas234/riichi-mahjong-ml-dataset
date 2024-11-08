import bz2
import os
import sqlite3
from typing import List
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
def saveFileForStateType(game_states: np.ndarray,
                game_id: str,
                statetype: int,
                year: int,
                path_to_save_in: str):

    if len(game_states) == 0:
        return

    directory = os.path.join(path_to_save_in,
                             "mahjong_dataset",
                             str(year),
                             STATE_TYPE_DIRS[statetype])


    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, f"{game_id}.npz")

    np.savez_compressed(file_path, game_states)



def saveToFile(log, year, path_to_save_in):
    game_id, game = convertLog(log)

    game_riichi, game_chi, game_pon, game_kan = gamelogToStates(game)

    saveFileForStateType(game_riichi, game_id, 0, year, path_to_save_in)
    saveFileForStateType(game_chi, game_id, 1 , year, path_to_save_in)
    saveFileForStateType(game_pon, game_id, 2 , year, path_to_save_in)
    saveFileForStateType(game_kan, game_id, 3 , year, path_to_save_in)


def saveFilesPerYear(year,
                     path_to_save_in: str,
                     path_to_db_file: str,
                     numFiles = None
    ):
    dbfile = path_to_db_file

    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    res = cur.execute(f"SELECT COUNT(*) FROM logs WHERE year = {year}")

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


def saveAll(years: List[int], path_to_save_in: str, path_to_db_file: str):
    for year in years:
        saveFilesPerYear(year = year,
                         path_to_save_in = path_to_save_in,
                         path_to_db_file = path_to_db_file)
        print(f"Finished processing {year}")
