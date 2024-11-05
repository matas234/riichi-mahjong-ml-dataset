import sqlite3
from gamelog_to_states import gamelogToStates
from process_replay import convertLog
import numpy as np

NUMGAMES = 100
START_IDX = 0





WIND_DIC = {
        0 : "E",
        1 : "S",
        2: "W",
        3 : "N"
    }



TILE_DIC = {i: f"{i+1}m"
            if i <= 8
            else f"{i-8}p"
            if i <= 17
            else f"{i-17}s"
            for i in range(27)}

honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd", -128:"None"}
TILE_DIC.update(honour_entries)



# converts hand from xml format
def formatHandFromXML(hand_string):
    if hand_string == '':
        return [0]*34

    hand_list = [0]*34
    string_list = hand_string.split(",")
    array = [int(ch) for ch in string_list]
    for i in array:
        hand_list[i // 4] +=1
    return hand_list




# formats hand into web format (can be plugged into: https://tenhou.net/2/?q=4566788m456p2246s)
def toWebFormat(handArray):
    dict = {0: 'm',
        1: 'p',
        2: 's',
        3: 'z'
    }
    split_indices=[9,18,27]
    handArray =  np.split(handArray, split_indices) 
    string = ''

    for k, suit in enumerate(handArray):
        if sum(suit) == 0:
            continue
        for num in range(len(suit)):
            if suit[num] == 0:  continue
            else:  string += str(num+1)*suit[num]
        
        string += dict[k]

    return string



#prints a matrix in readable format
def matprint(mat, fmt="g", file = None):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  " , file=file)
        print("" , file=file )



dbfile = 'es4p.db'
con = sqlite3.connect(dbfile)
cur = con.cursor()
res = cur.execute(f"SELECT log_id, log_content FROM logs")




game_logs = res.fetchmany(NUMGAMES)[START_IDX:]

con.close()

games_for_manual_testing = [convertLog(logs) for logs in game_logs]


def manualTest(gameNum):
    tupl = games_for_manual_testing[gameNum - START_IDX]
    game = tupl[1]

    game_riichi, game_chi, game_pon, game_kan = gamelogToStates(game)

    print("gameid: ", tupl[0])
    for i in game_kan:
        mat=i[0]
        printNice(mat)
        print("label: ", i[1])
        print("last discard:", mat[0][30])
        matprint(i[0])
        print("")



# prints gameState matrix into a readable format for debugging
def printNice(game, file = None):
    print("round wind: ", game[0], "| dealer: ", game[1], "| tilesInWall: ", game[5], "| doras: ", toWebFormat(game[34:68]), "| roundNum: ", game[33], "| honba sticks: ", game[3], "| riichi sticks: ", game[4],"| scores", game[6:10] , file=file )
    print("POV wind: "+ WIND_DIC[game[2]]+ " | POVHand: ", toWebFormat(game[68:102]) , file=file )  

    for i in range(4):
        print("P"+str(i)+ "| #chi=", game[14+i], "| #pon=", game[18+i], "| #kan=", game[22+i], "| #isOpen=", game[26+i],"| #isRiichi=", game[10+i],"| melds: "+toWebFormat(game[34*(i + 3): 34*(i + 4)]), file=file )
    for i in range(4):
        print("P"+str(i)+" pool: ", toWebFormat(game[34*(i + 7): 34*(i + 8)]) , file=file)




def printStates(states, file = None):
    for state in states:
        printNice(state, file=file)
        print("label: ", state[-1] , file=file )
        print("call tile:", TILE_DIC[int(state[30])] , file=file)
        #matprint(i[0], file=file)
        print("", file=file)


def printTestToFile(gameNum):
    with open("testing/NEW.txt" , "w+") as file:
        tupl = games_for_manual_testing[gameNum - START_IDX]
        game = tupl[1]

        game_riichi, game_chi, game_pon, game_kan = gamelogToStates(game)

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


