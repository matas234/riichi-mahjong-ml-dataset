from matrix import Matrix
import numpy as np
from global_helper_functions import decodeMeld



drawDic = {
    'T': 0,
    'U': 1,
    'V': 2,
    'W': 3
}

discardDic = {
    'D': 0,
    'E': 1,
    'F': 2,
    'G': 3
}




def matrixifymelds(arr):

    chiArr = []
    ponArr = []
    kanArr = []
    def handleMeldsOtherPlayers():
        discardPlayer = matrix.getLastDiscardPlayer()
        tile = matrix.getLastDiscardTile()
        
        players = [0,1,2,3]
        players.remove(discardPlayer)  # discard player cant call the tile
        callPlayer = None
        # true if next call is Pon or Kan; they get priority over chi.
        isPonInPriotity = lambda player: False
       
        nextMove  = arr[index+1]
        isNextMoveCall = (nextMove[0] == "N")

        isNextCallChi, isNextCallPon, isNextCallKan = False, False, False

        if isNextMoveCall:
            meldType = decodeMeld( int(nextMove[1]["m"]) )[1]
            callPlayer = int(nextMove[1]["who"])

            isNextCallChi = (meldType==0)
            isNextCallPon = (meldType==1)
            isNextCallKan = (meldType==2)

            isPonInPriotity = lambda player:  (isNextCallPon or isNextCallKan) and (player != callPlayer)
       
        for player in players:
            chiLabel, ponLabel, kanLabel = 0, 0, 0

            isCurrentPlayerCallPlayer = (callPlayer == player)

            ### CHI ###
            if matrix.canChi(player) and (not isPonInPriotity(player)):
                matrix.buildMatrix(player=player, forMeld=True)
                if isNextCallChi and isCurrentPlayerCallPlayer: 
                    chiLabel = 1
                    # removes the tile from the wall since it got called
                    matrix.decPlayerPool(discardPlayer, tile)

                chiArr.append([np.copy(matrix.getMatrix()), chiLabel])

            ### PON ### 
            if matrix.canPon(player):
                matrix.buildMatrix(player=player, forMeld=True)
                if isNextCallPon and isCurrentPlayerCallPlayer: 
                    ponLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                # ponArr.append([copy.deepcopy(matrix.getMatrix()), ponLabel])
                ponArr.append([np.copy(matrix.getMatrix()), ponLabel])

            ### KAN ###
            if matrix.canKan(player):
                matrix.buildMatrix(player, forMeld=True)
                if isNextCallKan and isCurrentPlayerCallPlayer: 
                    kanLabel = 1
                    matrix.decPlayerPool(discardPlayer, tile)
                kanArr.append([np.copy(matrix.getMatrix()), kanLabel])


    def handleMeldsSelf():
        drawPlayer = matrix.getLastDrawPlayer()

        isNextMoveCall = (arr[index+1][0] == "N")

        closedKanLabel, chankanLabel = 0, 0

        ### CLOSED KAN ###
        # If the player has 4 of the same tile then builds the matrix and appends it with the label to kanArr
        canClosedKan, callTile = matrix.canClosedKan(drawPlayer)
        
        if canClosedKan:
            matrix.buildMatrix(player=drawPlayer, forMeld=True, forClosedMeld=True, callTile=callTile)
            if isNextMoveCall:
                closedKanLabel = 1
            kanArr.append([np.copy(matrix.getMatrix()), closedKanLabel])


        ### CHANKAN ###
        canChakan, callTile = matrix.canChakan(drawPlayer)

        if canChakan:
            matrix.buildMatrix(player=drawPlayer, forMeld=True, forClosedMeld=True, callTile=callTile)
            if isNextMoveCall:
                chankanLabel = 1
            kanArr.append([np.copy(matrix.getMatrix()), chankanLabel])


    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]

            if item[0] == "INIT":
                #clears matrix attributes
                matrix = Matrix() 
                #initializes start of game
                matrix.initialiseGame(attr)

            elif item[0] == "N":
                meldInfo = decodeMeld(attr["m"])
                player = int( attr["who"] )
                isClosedCall = (player == matrix.getLastDrawPlayer()) and arr[index-2][0] != "N"

                matrix.handleMeld(player, meldInfo, isClosedCall)
          
            elif item[0] == "DORA":
                matrix.addDoraIndicator( int(attr["hai"]) // 4 )
            
            elif item[0] == "REACH":
                matrix.setRiichi( matrix.getLastDrawPlayer() )
                if attr["step"] == "2":
                    points = [int(i) for i in attr["ten"].split(",")]
                    matrix.setPlayerScore(points) 

        else:
            attr = item[0]        # attr in the form of, say, T46
            moveIndex = attr[0]   # T
            tile = int(attr[1:]) // 4  # 46 // 4

            #### DRAWS ####
            if moveIndex in drawDic:
                curPlayer = drawDic[moveIndex]
                matrix.handleDraw(curPlayer, tile)
                handleMeldsSelf()    

            #### DISCARDS ####  
            else:
                curPlayer = discardDic[moveIndex]
                matrix.handleDiscard(curPlayer, tile)
                matrix.addPlayerPool(curPlayer, tile)  # Always adds pool in this function and if the tile gets called then handleMeldsOtherPlayers() deletes it from pool
                handleMeldsOtherPlayers()
                
    return chiArr, ponArr, kanArr




def matrixify(arr):
    reachArr = []

    #riichi conditions are: the player is not already in riichi, hand is closed, is in tenpai, and >=4 tiles in live wall (rule)
    #checks for riichi conditions, and then appends to reachArr if passes necessary conditions
    def handleRiichi(player):
        if matrix.canRiichi(player):
            riichiLabel = 0
            matrix.buildMatrix(player=player)

            # if riichis then sets to riichi
            if arr[index+1][0] == "REACH": 
                riichiLabel = 1
                matrix.setRiichi(player)

            reachArr.append([np.copy(matrix.getMatrix()), riichiLabel]) 


    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]

            if item[0] == "INIT":
                #clears matrix attributes
                matrix = Matrix() 
                #initializes start of game 
                matrix.initialiseGame(attr)

            elif item[0] == "N":
                meldInfo = decodeMeld(attr["m"])
                player = int( attr["who"] )
                isClosedKan = (player == matrix.getLastDrawPlayer()) and arr[index-2][0] != "N"
                
                matrix.handleMeld(player, meldInfo, isClosedKan)
 
            # if new dora then adds it
            elif item[0] == "DORA":
                matrix.addDoraIndicator( int(attr["hai"]) // 4 )

            elif (item[0] == "REACH") and attr["step"] == "2":
                points = [int(i) for i in attr["ten"].split(",")]
                matrix.setPlayerScore(points) 


        else:
            attr = item[0]             # attr in the form of, say, T46
            moveIndex = attr[0]        # T
            tile = int(attr[1:]) // 4  # 46 // 4
            
            #### DRAWS ####
            if moveIndex in drawDic:
                curPlayer = drawDic[moveIndex]
                matrix.handleDraw(curPlayer, tile)
                handleRiichi(curPlayer)

            #### DISCARDS ####  
            else:
                curPlayer = discardDic[moveIndex]
                matrix.handleDiscard(curPlayer, tile)
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(curPlayer, tile)

    return reachArr