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




dbfile = 'es4p.db'
con = sqlite3.connect(dbfile)
cur = con.cursor()
res = cur.execute(f"SELECT log_id, log_content FROM logs")

game_logs = res.fetchmany(NUMGAMES)[START_IDX:]

con.close()


games_for_manual_testing = [(game_id, convertLog([log])) for game_id, log in game_logs]




# prints gameState matrix into a readable format for debugging
def printNice(game, file = None):
    print("round wind: ", game[0], "| dealer: ", game[1], "| tilesInWall: ", game[5], "| doras: ", toWebFormat(game[34:68]), "| roundNum: ", game[33], "| honba sticks: ", game[3], "| riichi sticks: ", game[4],"| scores", game[6:10] , file=file )
    print("POV wind: "+ WIND_DIC[game[2]]+ " | POVHand: ", toWebFormat(game[68:102]) , file=file )

    for i in range(4):
        print("P"+str(i)+ "| #chi=", game[14+i], "| #pon=", game[18+i], "| #kan=", game[22+i], "| #isOpen=", game[26+i],"| #isRiichi=", game[10+i],"| melds: "+toWebFormat(game[34*(i + 3): 34*(i + 4)]), file=file )
    for i in range(4):
        print("P"+str(i)+" pool: ", toWebFormat(game[34*(i + 7): 34*(i + 8)]) , file=file)




def printStates(states, labels, file = None):
    for state, label in zip(states, labels): #states:
        printNice(state, file=file)
        print("label: ", 0 if label[0] else 1 , file=file )
        print("call tile:", TILE_DIC[int(state[30])] , file=file)
        #matprint(i[0], file=file)
        print("", file=file)


def printTestToFile(gameNum):
    with open("testing/NEW.txt" , "w+") as file:
        game_id, game = games_for_manual_testing[gameNum - START_IDX]

        game_riichi, riichi_labels, game_chi, chi_labels, game_pon, pon_labels, game_kan, kan_labels = gamelogToStates(game)

        print(f"gameid:  {game_id}", file=file,)

        print("" , file=file )
        print("" , file=file)
        print("Riichi States" , file=file )
        printStates(game_riichi, riichi_labels, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Chi States" , file=file)
        printStates(game_chi, chi_labels, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Pon States" , file=file )
        printStates(game_pon, pon_labels, file=file)

        print("" , file=file)
        print("" , file=file)
        print("Kan States" , file=file)
        printStates(game_kan, kan_labels, file=file)
