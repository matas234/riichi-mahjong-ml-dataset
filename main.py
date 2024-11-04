import bz2
import os
import sqlite3
from lxml import etree
import xml.etree.ElementTree as ET
from tqdm import tqdm
import time

from global_helper_functions import *
from matrifixy_replays import matrixify, matrixifymelds


#redefine numGames so don't cook my computer
NUMGAMES = 300


dbfile = 'es4p.db'
con = sqlite3.connect(dbfile)
cur = con.cursor()
res = cur.execute(f"SELECT log_id, log_content FROM logs")


logs = []
for i in range(NUMGAMES):
    logs.append(res.fetchone())

con.close()



def convertLog(log):
    game = log[0]
    blob = log[1]

    XML = etree.XML

    decompress = bz2.decompress

    content = decompress(blob)

    xml = XML(content, etree.XMLParser(recover=True))
    rough_string = ET.tostring(xml, encoding='unicode')
    root = ET.fromstring(rough_string)

    arr = []
    for element in root:
        header_name = element.tag
        attributes_dict = element.attrib
        arr.append((header_name ,  attributes_dict))

    return game, arr


out = [convertLog(logs) for logs in logs]

def manualTest(gameNum):
    tupl = out[gameNum]
    game = tupl[1]

    game_riichi = matrixify(game)
    game_chi = matrixifymelds(game)[0]
    game_pon = matrixifymelds(game)[1]
    game_kan = matrixifymelds(game)[2]

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
    with open("out2.txt" , "w+") as file:
        tupl = out[gameNum]
        game = tupl[1]

        game_riichi = matrixify(game)
        game_chi = matrixifymelds(game)[0]
        game_pon = matrixifymelds(game)[1]
        game_kan = matrixifymelds(game)[2]

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
def flatformat(states, logid, statetype, year):
    arr = []
    for i in states:
        mat = i[0]
        label = i[1]
        flat = mat.flatten()
        flat = np.append(flat, label)
        arr.append(flat)
    
    #make sure that states are non empty, before saving to file
    if arr:

        arr_np = np.array(arr)
        
        if statetype == 0:
            directory = os.path.join(".", "Data", str(year), "Riichi")
        elif statetype == 1:
            directory = os.path.join(".", "Data", str(year), "Chi")
        elif statetype == 2:
            directory = os.path.join(".", "Data", str(year), "Pon")
        else:
            directory = os.path.join(".", "Data", str(year), "Kan")


        os.makedirs(directory, exist_ok=True)
        
        file_path = os.path.join(directory, f"{logid}.npz")
        
        np.savez_compressed(file_path, arr_np)
            



def saveToFile(log, year):

    tupl = convertLog(log)

    game = tupl[1]
    gameid = tupl[0]

    game_riichi = matrixify(game)

    game_chi, game_pon, game_kan = matrixifymelds(game)

    flatformat(game_riichi, gameid, 0, year)
    flatformat(game_chi, gameid, 1 , year)
    flatformat(game_pon, gameid, 2 , year) 
    flatformat(game_kan, gameid, 3 , year)


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
        

    for i in tqdm(range(numGames), desc="Processing games"):
        log = res.fetchone()

        try:
            saveToFile(log, year)
        except Exception as e:
            pass
            # print(f"An error occurred with i={i}: {e}")
            # traceback.print_exc()

    con.close()

def saveAll():
    for year in range(2018, 2021):
        #Change this Parameter to change number of games saved per year
        #IMPORTANT - if you don't include this parameter it will save EVERYTHING
        saveFilesPerYear(year)

printTestToFile(0)


start_time = time.time()

start_time = time.time()

saveAll()

end_time = time.time()

duration = end_time - start_time

print(f"saveAll() took {duration:.4f} seconds")
