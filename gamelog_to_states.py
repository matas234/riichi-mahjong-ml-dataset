from game_state import GameState
import numpy as np
from helper_functions import decodeMeld


DRAW_DIC = {
    'T': 0,
    'U': 1,
    'V': 2,
    'W': 3
}

DISCARD_DIC = {
    'D': 0,
    'E': 1,
    'F': 2,
    'G': 3
}



def gamelogToStates(game_log):
    chi_states = np.empty((0, 374), dtype=int)
    chi_labels = np.empty((0, 2) , dtype=int)

    pon_states = np.empty((0, 374), dtype=int)
    pon_labels = np.empty((0, 2) , dtype=int)

    kan_states = np.empty((0, 374), dtype=int)
    kan_labels = np.empty((0, 2) , dtype=int)

    riichi_states = np.empty((0, 374), dtype=int)
    riichi_labels = np.empty((0, 2) , dtype=int)


    def handleMeldsOtherPlayers():
        nonlocal chi_states, chi_labels, pon_states, pon_labels, kan_states, kan_labels

        discard_player = game_state.getLastDiscardPlayer()
        tile = game_state.getLastDiscardTile()

        players = [0,1,2,3]
        players.remove(discard_player)  # discard player cant call the tile
        call_player = None
        # true if next call is Pon or Kan; they get priority over chi.
        is_pon_in_priority = lambda player: False

        next_move  = game_log[index+1]
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
            if game_state.canChi(player) and (not is_pon_in_priority(player)):
                game_state.buildMatrix(player=player, for_meld=True)

                if is_next_call_chi and cur_player_is_call_player:
                    chi_label = 1
                    game_state.decPlayerPool(discard_player, tile)

                chi_states = np.append(chi_states,
                                       [game_state.game_state],
                                       axis=0)

                chi_labels = np.append(chi_labels,
                                       [np.eye(2, dtype=int)[chi_label]],
                                       axis=0)

            ### PON ###
            if game_state.canPon(player):
                game_state.buildMatrix(player=player, for_meld=True)

                if is_next_call_pon and cur_player_is_call_player:
                    pon_label = 1
                    game_state.decPlayerPool(discard_player, tile)


                pon_states = np.append(pon_states,
                                       [game_state.game_state],
                                       axis=0)

                pon_labels = np.append(pon_labels,
                                       [np.eye(2, dtype=int)[pon_label]],
                                       axis=0)


            ### KAN ###
            if game_state.canKan(player):
                game_state.buildMatrix(player, for_meld=True)

                if is_next_call_kan and cur_player_is_call_player:
                    kan_label = 1
                    game_state.decPlayerPool(discard_player, tile)

                kan_states = np.append(kan_states,
                                       [game_state.game_state],
                                       axis=0)

                kan_labels = np.append(kan_labels,
                                       [np.eye(2, dtype=int)[kan_label]],
                                       axis=0)



    def handleMeldsSelf():
        nonlocal kan_states, kan_labels

        draw_player = game_state.last_draw_player

        is_next_move_call = (game_log[index+1][0] == "N")

        closed_kan_label, chankan_label = 0, 0

        ### CLOSED KAN ###
        # If the player has 4 of the same tile then builds the matrix and appends it with the label to kanArr
        can_closed_kan, call_tile = game_state.canClosedKan(draw_player)

        if can_closed_kan:
            game_state.buildMatrix(player=draw_player, for_meld=True, for_closed_meld=True, call_tile=call_tile)

            if is_next_move_call:
                closed_kan_label = 1

            kan_states = np.append(kan_states,
                                   [game_state.game_state],
                                   axis=0)

            kan_labels = np.append(kan_labels,
                                   [np.eye(2, dtype=int)[closed_kan_label]],
                                   axis=0)



        ### CHANKAN ###
        can_chakan, call_tile = game_state.canChakan(draw_player)

        if can_chakan:
            game_state.buildMatrix(player=draw_player, for_meld=True, for_closed_meld=True, call_tile=call_tile)

            if is_next_move_call:
                chankan_label = 1

            kan_states = np.append(kan_states,
                                   [game_state.game_state],
                                   axis=0)

            kan_labels = np.append(kan_labels,
                                   [np.eye(2, dtype=int)[chankan_label]],
                                   axis=0)



    def handleRiichi(player):
        nonlocal riichi_states, riichi_labels

        if game_state.canRiichi(player):
            riichiLabel = 0
            game_state.buildMatrix(player=player)

            if game_log[index+1][0] == "REACH":
                riichiLabel = 1

            riichi_states = np.append(riichi_states,
                                      [game_state.game_state],
                                      axis=0)

            riichi_labels = np.append(riichi_labels,
                                      [np.eye(2, dtype=int)[riichiLabel]],
                                      axis=0)



    prv_call_player = False
    for index,item in enumerate(game_log):
        if item[1]:
            attr = item[1]

            if item[0] == "INIT":
                game_state = GameState()
                game_state.initialiseGame(attr)

            elif item[0] == "N":
                meld_info = decodeMeld(attr["m"])
                player = int( attr["who"] )

                ### theres some very unique bugs if i dont have these specific conditions
                ### one is related to sequence of subsequent calls by 2 players (game_log[index-2][0] != "N" fixes that)
                ### the other is when a player kans twice in a row (prvCallPlayer == player) fixes that
                ### and obviously draw player and call player are always the same player in a kan'
                is_closed_call = (player == game_state.last_draw_player and
                                  (game_log[index-2][0] != "N" or prv_call_player == player))

                game_state.handleMeld(player, meld_info, is_closed_call)

                prv_call_player = player

            elif item[0] == "DORA":
                game_state.addDoraIndicator( int(attr["hai"]) // 4 )

            elif item[0] == "REACH":
                game_state.setRiichi(game_state.last_draw_player)
                if attr["step"] == "2":
                    points = [int(i) for i in attr["ten"].split(",")]
                    game_state.setPlayerScore(points)

        else:
            attr = item[0]             # attr in the form of, say, T46
            moveIndex = attr[0]        # T
            tile = int(attr[1:]) // 4  # 46 // 4

            #### DRAWS ####
            if moveIndex in DRAW_DIC:
                cur_player = DRAW_DIC[moveIndex]
                game_state.handleDraw(cur_player, tile)
                handleMeldsSelf()
                handleRiichi(cur_player)

            #### DISCARDS ####
            else:
                cur_player = DISCARD_DIC[moveIndex]
                game_state.handleDiscard(cur_player, tile)
                game_state.addPlayerPool(cur_player, tile)  # Always adds pool in this function and if the tile gets called then handleMeldsOtherPlayers() deletes it from pool
                handleMeldsOtherPlayers()


    return (riichi_states, riichi_labels,
            chi_states, chi_labels,
            pon_states, pon_labels,
            kan_states, kan_labels)
