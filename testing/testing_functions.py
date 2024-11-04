import sqlite3
from global_helper_functions import toWebFormat
from matrifixy_replays import gameLogToMatrix
from process_replay import convertLog


windDict = {
        0 : "E",
        1 : "S",
        2: "W",
        3 : "N"
    }


tile_dic = {i: f"{i+1}m" if i <= 8 else f"{i-8}p" if i <= 17 else f"{i-17}s" for i in range(27)}
honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd", -128:"None"}
tile_dic.update(honour_entries)




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


NUMGAMES = 300

game_logs = []
for i in range(NUMGAMES):
    game_logs.append(res.fetchone())

con.close()

games_for_manual_testing = [convertLog(logs) for logs in game_logs]


def manualTest(gameNum):
    tupl = games_for_manual_testing[gameNum]
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



# prints gameState matrix into a readable format for debugging
def printNice(game, file = None):
    int_game = [[int(element) for element in row] for row in game]
    game=int_game
    print("round wind: ", game[0][0], "| dealer: ", game[0][1], "| tilesInWall: ", game[0][5], "| doras: ", toWebFormat(game[1]), "| roundNum: ", game[0][33], "| honba sticks: ", game[0][3], "| riichi sticks: ", game[0][4],"| scores", game[0][6:10] , file=file )
    print("POV wind: "+ windDict[ game[0][2] ]+ " | POVHand: ", toWebFormat(game[2]) , file=file )  

    for i in range(4):
        print("player"+str(i)+ "| #chi=", game[0][14+i], "| #pon=", game[0][18+i], "| #kan=", game[0][22+i], "| #isOpen=", game[0][26+i],"| #isRiichi=", game[0][10+i],"| melds: "+toWebFormat(game[3+i]) , file=file )
    for i in range(4):
        print("player"+str(i)+" pool: ", toWebFormat(game[7+i]) , file=file)




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
        tupl = games_for_manual_testing[gameNum]
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


