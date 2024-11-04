import numpy as np




# converts hand from xml format
def formatHandFromXML(hand_string):
    if hand_string == '':
        return [0]*34

    out=np.zeros(34, dtype=int)
    string_list = hand_string.split(",")
    array = np.array([int(ch) for ch in string_list])
    for i in array:
        out[i // 4] +=1
    return out



#prints a matrix in readable format
def matprint(mat, fmt="g", file = None):
    col_maxes = [max([len(("{:"+fmt+"}").format(x)) for x in col]) for col in mat.T]
    for x in mat:
        for i, y in enumerate(x):
            print(("{:"+str(col_maxes[i])+fmt+"}").format(y), end="  " , file=file)
        print("" , file=file )


windDict = {
        0 : "E",
        1 : "S",
        2: "W",
        3 : "N"
    }


tile_dic = {i: f"{i+1}m" if i <= 8 else f"{i-8}p" if i <= 17 else f"{i-17}s" for i in range(27)}
honour_entries = {27 : "e", 28 : "s", 29 : "w", 30 : "n", 31 : "wd", 32 : "gd", 33 : "rd", -128:"None"}
tile_dic.update(honour_entries)



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


# prints gameState matrix into a readable format for debugging
def printNice(game, file = None):
    int_game = [[int(element) for element in row] for row in game]
    game=int_game
    print("round wind: ", game[0][0], "| dealer: ", game[0][1], "| tilesInWall: ", game[0][5], "| doras: ", toWebFormat(game[1]), "| roundNum: ", game[0][33], "| honba sticks: ", game[0][3], "| riichi sticks: ", game[0][4],"| scores", game[0][6:10] , file=file )
    print("POV wind: "+ windDict[ game[0][2] ]+ " | POVHand: ", toWebFormat(game[2]) , file=file )  

    for i in range(4):
        print("player"+str(i)+ "| #chi=", game[0][14+i], "| #pon=", game[0][18+i], "| #kan=", game[0][22+i], "| #isOpen=", game[0][26+i],"| #isRiichi=", game[0][10+i],"| melds: "+toWebFormat(game[3+i]) , file=file )
    for i in range(4):
        print("player"+str(i)+" pool: ",toWebFormat(game[7+i]) , file=file)


# decodes meld (from integer)
def decodeMeld(data): #chi:0, pon:1, kan: 2, chakan:3
    def decodeChi(data):
        meldType = 0
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        baseAndCalled = data >> 10
        called = baseAndCalled % 3
        base = baseAndCalled // 3
        base = (base // 7) * 9 + base % 7
        tiles = [(t0 + 4 * (base + 0))//4, (t1 + 4 * (base + 1))//4, (t2 + 4 * (base + 2))//4]
        return tiles, meldType

    def decodePon(data):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1,2,3),(0,2,3),(0,1,3),(0,1,2))[t4]
        baseAndCalled = data >> 9
        called = baseAndCalled % 3
        base = baseAndCalled // 3
        if data & 0x8:
            meldType = 1
            tiles = [(t0 + 4 * base)//4, (t1 + 4 * base)//4, (t2 + 4 * base)//4]
        else:
            meldType = 3
            tiles = [(t0 + 4 * base)//4, (t1 + 4 * base)//4, (t2 + 4 * base)//4]
        return tiles, meldType

    def decodeKan(data, fromPlayer):
        baseAndCalled = data >> 8
        if fromPlayer:
            called = baseAndCalled % 4
        base = baseAndCalled // 4
        meldType = 2
        tiles = [base, base, base, base]
        return tiles, meldType

    data = int(data)
    meld = data & 0x3
    if data & 0x4:
        meld = decodeChi(data)
    elif data & 0x18:
        meld = decodePon(data)
    else:
        meld = decodeKan(data, False)
    return meld
