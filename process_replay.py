import bz2
import os
import sqlite3
from typing import List
from lxml import etree
import xml.etree.ElementTree as ET
from tqdm import tqdm
import time

from global_helper_functions import *
from matrifixy_replays import gameLogToMatrix


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


out = [convertLog(logs) for logs in game_logs]

def manualTest(gameNum):
    tupl = out[gameNum]
    game = tupl[1]

    game_riichi, game_chi, game_pon, game_kan = gameLogToMatrix(game)

    print("gameid: ", tupl[0])
    for i in game_kan:
        mat=i[0]
        printNice(mat)
        print("label: ", i[1])
        print("last discard:", mat[0][30])
        matprint(i[0])
        print("")


def printStates(states, file = None):
    for i in states:
        mat=i[0]
        printNice(mat, file=file)
        print("label: ", i[1] , file=file )
        print("call tile:", tile_dic[int(mat[0][30])] , file=file)
        #matprint(i[0], file=file)
        print("", file=file)


def printTestToFile(gameNum):
    with open("out.txt" , "w+") as file:
        tupl = out[gameNum]
        game = tupl[1]

        game_riichi, game_chi, game_pon, game_kan = gameLogToMatrix(game)

        print("gameid: ", tupl[0], file=file,)

        print("" , file=file )
        print("" , file=file)
        print("Riichi States" , file=file )
        printStates(game_riichi, file=file)

        print("" , file=file)
        print("" , file=file) 
        print("Chi States" , file=file)
        printStates(game_chi, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Pon States" , file=file )
        printStates(game_pon, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Kan States" , file=file)
        printStates(game_kan, file=file)



#statetype (0-4) 0 - riichi, 1 - chi, 2 - pon, 3- kan
# flattens the state matrices, appends the label, and saves to file
def saveFileForState(game_states: np.ndarray,
                game_id: str,
                statetype: int, 
                year: int):
    
    if len(game_states) == 0:
        return
    
    
    arr_to_be_saved = np.empty((len(game_states), 375))

    for idx, (matrix, label) in enumerate(game_states):
        matrix_flat_with_label = np.append(matrix.flatten(), label)
        arr_to_be_saved[idx] = matrix_flat_with_label
    
    #make sure that states are non empty, before saving to file
    if statetype == 0:
        directory = os.path.join(".", "Data", str(year), "Riichi")
    elif statetype == 1:
        directory = os.path.join(".", "Data", str(year), "Chi")
    elif statetype == 2:
        directory = os.path.join(".", "Data", str(year), "Pon")
    else:
        directory = os.path.join(".", "Data", str(year), "Kan")


    os.makedirs(directory, exist_ok=True)
    
    file_path = os.path.join(directory, f"{game_id}.npz")
    
    # np.savez_compressed(file_path, arr_to_be_saved)
            



def saveToFile(log, year):
    game_id, game = convertLog(log)

    game_riichi, game_chi, game_pon, game_kan = gameLogToMatrix(game)

    saveFileForState(game_riichi, game_id, 0, year)
    saveFileForState(game_chi, game_id, 1 , year)
    saveFileForState(game_pon, game_id, 2 , year) 
    saveFileForState(game_kan, game_id, 3 , year)


def saveFilesPerYear(year, numFiles = None):
    dbfile = 'es4p.db'

    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    res = cur.execute(f"SELECT COUNT(*) FROM logs WHERE year = {year}")

    numGames = res.fetchone()[0]

    print(year)

    res = cur.execute(f"SELECT log_id, log_content FROM logs WHERE year = {year}")

    if numFiles:
        numGames = numFiles

    for _ in tqdm(range(numGames), desc="Processing games"):
        log = res.fetchone()

        try:
            saveToFile(log, year)
        except Exception as e:
            pass
            # print(f"An error occurred with i={i}: {e}")
            # traceback.print_exc()

    con.close()


def saveAll(years: List[int]):
    for year in years:
        #Change this Parameter to change number of games saved per year
        #IMPORTANT - if you don't include this parameter it will save EVERYTHING
        saveFilesPerYear(year)