
from typing import List, Tuple
import numpy as np
from helper_functions import formatHandFromXML
from shanten_calculator import calculateShanten

class GameState:
    game_state = np.zeros(375, dtype=int)
    private_hands = np.zeros((4, 34), dtype=int)
    player_melds = np.zeros((4, 34), dtype=int)
    player_pools = np.zeros((4, 34), dtype=int)

    is_closed = [True, True, True, True]
    player_pon_tiles = [[], [], [], []]
    closed_kans = [0, 0, 0, 0]
    chis_num = [0, 0, 0, 0]    #
    pons_num = [0, 0, 0, 0]    # num of melds for each player
    kans_num = [0, 0, 0, 0]    #
    player_scores = [0,  0,  0,  0]
    player_winds = [0, 0, 0, 0]
    is_in_riichi = [False, False, False, False]

    round_wind = 0
    honba_sticks = 0
    round_dealer = 0
    wall_tiles = 70

    last_draw_player = 0
    last_draw_tile = 0
    last_discard_player = 0
    last_discard_tile = 0

    def __init__(self):
        self.reset()

    @classmethod
    def reset(cls):
        cls.game_state.fill(0)
        cls.private_hands.fill(0)
        cls.player_melds.fill(0)
        cls.player_pools.fill(0)

        cls.round_wind = 0
        cls.honba_sticks = 0
        cls.round_dealer = 0
        cls.wall_tiles = 70

        cls.last_draw_player = 0
        cls.last_draw_tile = 0
        cls.last_discard_player = 0
        cls.last_discard_tile = 0

        for i in range(4):
            cls.is_closed[i] = True
            cls.is_in_riichi[i] = False
            cls.player_pon_tiles[i].clear()
            cls.closed_kans[i] = 0
            cls.chis_num[i] = 0
            cls.pons_num[i] = 0
            cls.kans_num[i] = 0
            cls.player_scores[i] = 0
            cls.player_winds[i] = 0


    def setLabel(self, label):
        self.game_state[-1] = label

    # builds matrix for POV player
    # forMeld   Riichi: False , Meld: true   (only difference is last discard)
    def buildMatrix(self,
                    player: int,
                    call_tile: int = None,
                    for_meld = False,
                    for_closed_meld = False,
        ):
        # player ordering relative to input player. e.g. player =2  => player_ordering = [2,3,0,1]   (counterclockwise on table)
        player_ordering = [i%4 for i in range(player, player + 4)]

        #round wind
        self.game_state[0] = self.round_wind
        #dealer
        self.game_state[1] = player_ordering.index(self.round_dealer)
        #pov wind
        self.game_state[2] = self.player_winds[player]
        #num of honba sticks
        self.game_state[3] = self.honba_sticks
        #num of riichi sticks
        self.game_state[4] = self.is_in_riichi.count(True)
        #num of tiles left in wall (kans might mess this up need to check)
        self.game_state[5] = self.wall_tiles
        #padding
        self.game_state[30:33] = -128
        #round number
        self.game_state[33] = self.round_dealer + 1

        #pov hand
        self.game_state[68:102] = self.private_hands[player]

        for idx, player in enumerate(player_ordering):
            #melds
            self.game_state[34*(idx + 3): 34*(idx + 4)] = self.player_melds[player]
            #pools
            self.game_state[34*(idx + 7): 34*(idx + 8)] = self.player_pools[player]

            #scores
            self.game_state[6+idx] = self.player_scores[player]
            #riichis
            self.game_state[10+idx] = 1 if self.is_in_riichi[player] else 0
            #number of chis
            self.game_state[14+idx] = self.chis_num[player]
            #number of pons
            self.game_state[18+idx] = self.pons_num[player]
            #number of kans
            self.game_state[22+idx] = self.kans_num[player]
            # 0: closed, 1: open
            self.game_state[26+idx] = 0 if self.is_closed[player] else 1


        # sets call tile for the meld matrices
        if for_meld:
            if for_closed_meld:
                self.game_state[30] = call_tile
            else:
                self.game_state[30] = self.last_discard_tile


    def setRiichi(self, player):
        self.is_in_riichi[player] = True


    def addPlayerPool(self, player, tile):
        self.player_pools[player][tile] += 1


    def decPlayerPool(self, player, tile):
        self.player_pools[player][tile] -= 1


    def addMeldNum(self, player, meldType):
        if meldType == 0:
            self.chis_num[player] += 1

        elif meldType == 1:
            self.pons_num[player] += 1

        elif meldType == 2:
            self.kans_num[player] += 1


    # this is dependant on roundDealer so should only be called once the dealer is set
    def setPlayerWinds(self):
        dealer = self.round_dealer
        self.player_winds = [(i-dealer)%4 for i in range(4)]


    def setPlayerScore(self, scores):
        self.player_scores = scores


    def getLastDiscardPlayer(self):
        return self.last_discard_player


    def getLastDiscardTile(self):
        return self.last_discard_tile


    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.game_state[34 + doraIndicator] += 1


    def canPon(self, player):
        tile = self.last_discard_tile
        return (self.private_hands[player][tile] >= 2 and
                not self.is_in_riichi[player])


    def canKan(self, player):
        tile = self.last_discard_tile
        return (self.private_hands[player][tile] == 3 and
                not self.is_in_riichi[player])


    def canChi(self, player):

        tile = self.last_discard_tile
        fromPlayer = self.last_discard_player

        #checks whether it's a honour tile, that the call is from the player before in ordering, and that Riichi has not been called
        if (tile//9 == 3 or
            not ((fromPlayer + 1) % 4 == player) or
            self.is_in_riichi[player]
        ):
            return False

        #number of the tile
        tile_num = tile % 9

        #hand of player
        hand = self.private_hands[player]

        #if tileNum is 1
        if tile_num == 0:
            return (hand[tile+1]>0 and
                    hand[tile+2]>0)

        #if tileNum is 9
        elif tile_num == 8:
            return (hand[tile-1]>0 and
                    hand[tile-2]>0)

        #if tileNum is 2
        elif tile_num == 1:
            return ((hand[tile+1]>0 and hand[tile+2]>0) or
                     hand[tile-1]>0 and hand[tile+1]>0)

        #if tileNum is 8
        elif tile_num == 7:
            return ((hand[tile-1]>0 and hand[tile-2]>0) or
                     hand[tile-1]>0 and hand[tile+1]>0)

        # else:  3 <= tileNum <= 7 so can make any chi with it
        else:
            return ((hand[tile-1]>0 and hand[tile-2]>0) or
                    (hand[tile-1]>0 and hand[tile+1]>0) or
                    (hand[tile+1]>0 and hand[tile+2]>0))


    def canClosedKan(self, player) -> Tuple[bool, int]:
        for tile in range(34):
            if self.private_hands[player][tile] == 4:
                return True, tile

        return False, None


    def canChakan(self, player):
        for tile in range(34):
            if (self.private_hands[player][tile] > 0 and
                tile in self.player_pon_tiles[player]
            ):
                return True, tile

        return False , None


    def canRiichi(self, player):
        return (not self.is_in_riichi[player] and
                self.is_closed[player] and
                calculateShanten(called_melds_num = self.closed_kans[player],
                                 hand = self.private_hands[player]
                                 ) <= 0 and
                self.wall_tiles >= 4)


    def handleDraw(self, player, tile):
        self.last_draw_player = player
        self.last_draw_tile = tile
        self.wall_tiles -=1                     # remove a wall tile after drawing
        self.private_hands[player][tile] += 1    # add the drawn tile to hand


    def handleDiscard(self, player, tile):
        self.last_discard_player = player
        self.private_hands[player][tile] -= 1  # remove discarded tile from hand
        self.last_discard_tile = tile


    def initialiseGame(self, data):
        #sets points
        points = [int(i) for i in data["ten"].split(",")]
        self.setPlayerScore(points)

        #sets player winds
        self.round_dealer = int(data["oya"])
        self.setPlayerWinds()

        #sets starting hands
        self.private_hands = [formatHandFromXML(data["hai"+str(i)]) for i in range(4)]

        #sets more metadata form seed
        seed = [int(i) for i in data["seed"].split(',')]
        self.addDoraIndicator(seed[5] // 4)
        self.honba_sticks = seed[1]
        self.round_wind = seed[0] // 4


    #meldInfo = [1,2,3]
    #meldType (0-3) 0 chi, 1 pon, 2 Kan, 3 Chakan
    def handleMeld(self,
                   player: int,
                   meld_info: List[int],
                   is_closed_call: bool
        ):
        meld_tiles = meld_info[0]
        meld_type = meld_info[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meld_type == 3:
            # removes the pon from player
            self.player_pon_tiles[player].remove(meld_tiles[0])

            # decrements pon count
            self.pons_num[player] -= 1
            # adds the chakan to player calls
            self.player_melds[player][meld_tiles[0]] = 4
            # increments kan count
            self.kans_num[player] += 1
            # removes the tile from player private hand
            self.private_hands[player][meld_tiles[0]] = 0

        # handles closed kan
        elif is_closed_call:
            self.private_hands[player][ meld_tiles[0] ] = 0
            self.kans_num[player] += 1
            self.player_melds[player][ meld_tiles[0] ] = 4

        # handles regular call
        else:
            # sets player to open since he called a regular meld
            self.is_closed[player] = False
            # adds meld tiles to meld attribute
            for tile in meld_tiles:
                self.player_melds[player][tile] += 1

            called = self.last_discard_tile
            meld_tiles.remove(called)

            #removes tiles from player hand
            for tile in meld_tiles:
                self.private_hands[player][tile] -= 1
            # adds pon if pon
            if meld_type == 1:
                self.player_pon_tiles[player].append(meld_tiles[0])
            # adds meld number
            self.addMeldNum(player, meld_type)
