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
    kan_arr = []
    def handleMeldsOtherPlayers():
        discard_player = matrix.getLastDiscardPlayer()
        tile = matrix.getLastDiscardTile()
        
        players = [0,1,2,3]
        players.remove(discard_player)  # discard player cant call the tile
        call_player = None
        # true if next call is Pon or Kan; they get priority over chi.
        is_pon_in_priority = lambda player: False
       
        next_move  = arr[index+1]
        is_next_move_call = (next_move[0] == "N")

        is_next_call_chi, is_next_call_pon, is_next_call_kan = False, False, False


        if is_next_move_call:
            meldType = decodeMeld( int(next_move[1]["m"]) )[1]
            call_player = int(next_move[1]["who"])

            is_next_call_chi = (meldType==0)
            is_next_call_pon = (meldType==1)
            is_next_call_kan = (meldType==2)

            is_pon_in_priority = lambda player:  (is_next_call_pon or is_next_call_kan) and (player != call_player)
       
       
        for player in players:
            chi_label, pon_label, kan_label = 0, 0, 0

            cur_player_is_call_player = (call_player == player)

            ### CHI ###
            if matrix.canChi(player) and (not is_pon_in_priority(player)):
                matrix.buildMatrix(player=player, forMeld=True)
                
                if is_next_call_chi and cur_player_is_call_player: 
                    chi_label = 1
                    # removes the tile from the wall since it got called
                    matrix.decPlayerPool(discard_player, tile)

                chiArr.append([np.copy(matrix.getMatrix()), chi_label])

            ### PON ### 
            if matrix.canPon(player):
                matrix.buildMatrix(player=player, forMeld=True)
                
                if is_next_call_pon and cur_player_is_call_player: 
                    pon_label = 1
                    matrix.decPlayerPool(discard_player, tile)

                # ponArr.append([copy.deepcopy(matrix.getMatrix()), ponLabel])
                ponArr.append([np.copy(matrix.getMatrix()), pon_label])

            ### KAN ###
            if matrix.canKan(player):
                matrix.buildMatrix(player, forMeld=True)
                
                if is_next_call_kan and cur_player_is_call_player: 
                    kan_label = 1
                    matrix.decPlayerPool(discard_player, tile)

                kan_arr.append([np.copy(matrix.getMatrix()), kan_label])


    def handleMeldsSelf():
        draw_player = matrix.getLastDrawPlayer()

        is_next_move_call = (arr[index+1][0] == "N")

        closed_kan_label, chankan_label = 0, 0

        ### CLOSED KAN ###
        # If the player has 4 of the same tile then builds the matrix and appends it with the label to kanArr
        can_closed_kan, call_tile = matrix.canClosedKan(draw_player)
        
        if can_closed_kan:
            matrix.buildMatrix(player=draw_player, forMeld=True, forClosedMeld=True, callTile=call_tile)

            if is_next_move_call:
                closed_kan_label = 1

            kan_arr.append([np.copy(matrix.getMatrix()), closed_kan_label])


        ### CHANKAN ###
        can_chakan, call_tile = matrix.canChakan(draw_player)

        if can_chakan:
            matrix.buildMatrix(player=draw_player, forMeld=True, forClosedMeld=True, callTile=call_tile)

            if is_next_move_call:
                chankan_label = 1

            kan_arr.append([np.copy(matrix.getMatrix()), chankan_label])


    for index,item in enumerate(arr): 
        if item[1]:
            attr = item[1]

            if item[0] == "INIT":
                matrix = Matrix() 
                #initializes start of game
                matrix.initialiseGame(attr)

            elif item[0] == "N":
                meld_info = decodeMeld(attr["m"])
                player = int( attr["who"] )
                is_closed_call = (player == matrix.getLastDrawPlayer()) and arr[index-2][0] != "N"

                matrix.handleMeld(player, meld_info, is_closed_call)
          
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
                cur_player = drawDic[moveIndex]
                matrix.handleDraw(cur_player, tile)
                handleMeldsSelf()    

            #### DISCARDS ####  
            else:
                cur_player = discardDic[moveIndex]
                matrix.handleDiscard(cur_player, tile)
                matrix.addPlayerPool(cur_player, tile)  # Always adds pool in this function and if the tile gets called then handleMeldsOtherPlayers() deletes it from pool
                handleMeldsOtherPlayers()
                
    return chiArr, ponArr, kan_arr




def matrixify(arr):
    riichi_arr = []

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

            riichi_arr.append([np.copy(matrix.getMatrix()), riichiLabel]) 


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
            move_idx = attr[0]        # T
            tile = int(attr[1:]) // 4  # 46 // 4
            
            #### DRAWS ####
            if move_idx in drawDic:
                curPlayer = drawDic[move_idx]
                matrix.handleDraw(curPlayer, tile)
                handleRiichi(curPlayer)

            #### DISCARDS ####  
            else:
                curPlayer = discardDic[move_idx]
                matrix.handleDiscard(curPlayer, tile)
                if arr[index+1][0] != "N":
                    matrix.addPlayerPool(curPlayer, tile)

    return riichi_arr