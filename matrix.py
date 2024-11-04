
import numpy as np
from global_helper_functions import formatHandFromXML
from shanten_calculator import calculateShanten

class Matrix:     
    def __init__(self):
        self.game_state = np.zeros((11, 34), dtype=int)
        self.privateHands = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.player_melds = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.player_pools = [[0]*34 , [0]*34 , [0]*34 , [0]*34]
        self.doras = [0]*34
        self.is_in_riichi = [False, False, False, False]

        # metadata
        self.round_wind = 0   #0:E, 1:S, ...
        self.playerScores = [0, 0, 0, 0]
        self.player_winds = [0,1,2,3]
        self.honba_sticks = 0
        self.round_wind = 0
        self.round_dealer = 0
        self.wall_tiles = 70      # technically 69 but the dataset considers dealer 14th tile as a draw
        self.chis_num = [0,0,0,0]    #
        self.pons_num = [0,0,0,0]    # num of melds for each player
        self.kans_num = [0,0,0,0]    #

        #used to keep track of things
        self.last_draw_player = 0
        self.last_draw_tile = 0       
        self.last_discard_player = 0
        self.last_discard_tile = 0
        self.closed_kans = [0,0,0,0]       
        self.is_closed = [True, True, True, True]  
        self.player_pon_tiles = [[], [], [], []]   



    def getRiichi(self, player):   #needed
        return self.is_in_riichi[player]
    
    def setRiichi(self, player):
        self.is_in_riichi[player] = True

    # builds matrix for POV player
    # forMeld   Riichi: False , Meld: true   (only difference is last discard)   
    def buildMatrix(self, player, forMeld=False, forClosedMeld=False, callTile=None):
        # player ordering relative to input player. e.g. player =2  => player_ordering = [2,3,0,1]   (counterclockwise on table)
        player_ordering = [i%4 for i in range(player,player+4)]

        #round wind
        self.game_state[0][0] = self.round_wind
        #dealer
        self.game_state[0][1] = player_ordering.index(self.round_dealer)
        #pov wind
        self.game_state[0][2] = self.player_winds[player]        
        #num of honba sticks
        self.game_state[0][3] = self.honba_sticks
        #num of riichi sticks
        self.game_state[0][4] = self.is_in_riichi.count(True)  
        #num of tiles left in wall (kans might mess this up need to check)
        self.game_state[0][5] = self.wall_tiles
        #padding
        self.game_state[0][30:33] = -128
        #round number
        self.game_state[0][33] = self.round_dealer + 1    
        
        #pov hand
        self.game_state[2] = self.privateHands[player]

        for index,player in enumerate(player_ordering):
            #melds
            self.game_state[3+index] = self.player_melds[player]
            #pools
            self.game_state[7+index] = self.player_pools[player]

            #scores
            self.game_state[0][6+index] = self.playerScores[player]
            #riichis
            self.game_state[0][10+index] = 1 if self.is_in_riichi[player] else 0
            #number of chis
            self.game_state[0][14+index] = self.chis_num[player]
            #number of pons
            self.game_state[0][18+index] = self.pons_num[player]
            #number of kans
            self.game_state[0][22+index] = self.kans_num[player]
            # 0: closed, 1: open
            self.game_state[0][26+index] = 0 if self.is_closed[player] else 1


        # sets call tile for the meld matrices
        if forMeld:
            if forClosedMeld:
                self.game_state[0][30] = callTile
            else:
                self.game_state[0][30] = self.last_discard_tile
            

    def getMatrix(self):  
        return self.game_state
    
    def addPlayerPonTiles(self, player, tiles):
        self.player_pon_tiles[player].append(tiles[0])

    def decPlayerPonTiles(self, player, tiles):
        self.player_pon_tiles[player].remove(tiles[0])

    def getPlayerPonTiles(self, player):
        return self.player_pon_tiles[player]

    def addClosedKan(self, player):
        self.closed_kans[player] += 1           

    def getClosedKan(self, player):  #needed
        return self.closed_kans[player]

    def addPlayerPool(self, player, tile):
        self.player_pools[player][tile] += 1

    def decPlayerPool(self, player, tile):
        self.player_pools[player][tile] -= 1
    
    def addChi(self, player):
        self.chis_num[player] += 1

    def addPon(self, player):
        self.pons_num[player] += 1

    def decPon(self, player):
        self.pons_num[player] -= 1

    def addKan(self, player):
        self.kans_num[player] += 1

    def addMeldNum(self, player, meldType):
        if meldType == 0:
            self.addChi(player)
        elif meldType == 1:
            self.addPon(player)
        elif meldType == 2:
            self.addKan(player)    

    def getMeldNum(self, player):
        return self.chis_num[player] + self.pons_num[player] + self.kans_num[player]

    # initialises starting hands for each player
    def initialisePrivateHands(self, hands):
        for i in range(4):
            self.privateHands[i] = hands[i]

    #input player (0-3) tile (0-34)
    def addTilePrivateHand(self, player, tile):
        self.privateHands[player][tile] += 1

    #input player (0-3) tile (0-34)
    def removeTilePrivateHand(self, player, tile):
        self.privateHands[player][tile] -= 1

    def getPrivateHand(self, player):
        return self.privateHands[player]
    
    # this is dependant on roundDealer so should only be called once the dealer is set
    def setPlayerWinds(self):
        dealer = self.round_dealer
        self.player_winds = [(i-dealer)%4 for i in range(4)]

    def setRoundWind(self, wind):
        self.round_wind = wind
    
    def setDealer(self, dealer):
        self.round_dealer = dealer

    #input amount 
    def setHonbaSticks(self, amount):
        self.honba_sticks = amount
    
    #decrement wall tiles by one
    def decWallTiles(self):
        self.wall_tiles -=1
    
    def getWallTiles(self):
        return self.wall_tiles
    
    def getPlayerScores(self):
        return self.playerScores
    
    def setPlayerScore(self, scores):
        self.playerScores = scores
    
    def getPlayerScore(self, player):
        if player in [0,1,2,3]:
            return self.playerScores[player]
        else:
            print("Invalid Player")
    
    def setLastDiscardPlayer(self, player):
        self.last_discard_player = player

    def getLastDiscardPlayer(self):
        return self.last_discard_player

    def setLastDiscardTile(self, tile):
        self.last_discard_tile = tile

    def getLastDiscardTile(self):
        return self.last_discard_tile
    
    def setLastDrawPlayer(self, player):
        self.last_draw_player = player

    def getLastDrawPlayer(self):
        return self.last_draw_player
    
    def setLastDrawTile(self, tile):
        self.last_draw_tile = tile

    def getLastDrawTile(self):
        return self.last_draw_tile

    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.game_state[1][doraIndicator] += 1
            
    def canPon(self, player):
        tile = self.last_discard_tile
        return (self.privateHands[player][tile] >= 2) and not self.getRiichi(player)

    def canKan(self, player):
        tile = self.last_discard_tile
        return (self.privateHands[player][tile] == 3) and not self.getRiichi(player)

    def canChi(self, player): 
        
        tile = self.last_discard_tile
        fromPlayer = self.last_discard_player

        #checks whether it's a honour tile, that the call is from the player before in ordering, and that Riichi has not been called
        if (tile//9 == 3 or 
            not((fromPlayer + 1) % 4 == player) 
            or self.getRiichi(player)
        ):
            return False
        
        else:
            #number of the tile
            t = tile % 9
            #hand of player
            h = self.privateHands[player]
            
            #if tileNum is 1
            if t == 0: 
                return (h[tile+1]>0 and h[tile+2]>0)
            #if tileNum is 9
            elif t == 8: 
                return (h[tile-1]>0 and h[tile-2]>0)
            #if tileNum is 2
            elif t == 1: 
                return (h[tile+1]>0 and h[tile+2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            #if tileNum is 8
            elif t == 7: 
                return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0)
            # else:  3 <= tileNum <= 7 so can make any chi with it
            else: 
                return (h[tile-1]>0 and h[tile-2]>0) or (h[tile-1]>0 and h[tile+1]>0) or (h[tile+1]>0 and h[tile+2]>0)


    def canClosedKan(self, player):
        hand = self.privateHands[player]
        canClosedKan = False
        callTile = None

        for tile in range(34):
            if hand[tile] == 4:
                canClosedKan = True
                callTile = tile
                break

        return canClosedKan, callTile


    def canChakan(self, player):
        hand = self.privateHands[player]
        canChackan = False
        callTile = None

        for tile in range(34):
            playerHasTile_inHand = (hand[tile]>0)
            playerHasTile_inPon = (tile in self.player_pon_tiles[player])

            if playerHasTile_inHand and playerHasTile_inPon:
                canChackan = True
                callTile = tile
                break
        
        return canChackan , callTile

    def canRiichi(self, player):
        return (not self.is_in_riichi[player] and
                self.is_closed[player] and
                calculateShanten(hand=self.privateHands[player], numCalledMelds=self.closed_kans[player]) <= 0 and
                self.wall_tiles >= 4)


    def setOpen(self, player):
        self.is_closed[player] = False
    
    def getClosed(self, player):
        return self.is_closed[player]

    def handleDraw(self, player, tile):
        self.setLastDrawPlayer(player)   
        self.setLastDrawTile(tile)
        self.decWallTiles()                 # remove a wall tile after drawing
        self.addTilePrivateHand(player, tile)      # add the drawn tile to hand

    def handleDiscard(self, player, tile):
        self.setLastDiscardPlayer(player)
        self.removeTilePrivateHand(player, tile)   # remove discarded tile from hand
        self.setLastDiscardTile(tile)

    def initialiseGame(self, data):
        #sets points
        points = [int(i) for i in data["ten"].split(",")]
        self.setPlayerScore(points)
        
        #sets player winds
        self.setDealer(int(data["oya"]))
        self.setPlayerWinds()

        #sets starting hands
        initialHands = [formatHandFromXML(data["hai"+str(i)]) for i in range(4)]
        self.initialisePrivateHands(initialHands)

        #sets more metadata form seed
        seed = [int(i) for i in data["seed"].split(',')]
        self.addDoraIndicator(seed[5] // 4)
        self.setHonbaSticks(seed[1])
        self.setRoundWind(seed[0] //4)
        self.setDealer(seed[0] % 4)


    #meldInfo = [1,2,3]
    #meldType (0-3) 0 chi, 1 pon, 2 Kan, 3 Chakan
    def handleMeld(self, player, meldInfo, isClosedCall):
        meldTiles = meldInfo[0]
        meldType = meldInfo[1]

        # (ordering of if and elif is important here)
        # handles chakan
        if meldType == 3: 
            self.decPlayerPonTiles(player, meldTiles)
            self.decPon(player)
            self.player_melds[player][ meldTiles[0] ] = 4
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0
       
        # handles closed kan       
        elif isClosedCall:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.player_melds[player][ meldTiles[0] ] = 4

        # handles regular call
        else:
            self.setOpen(player)
            # adds meld tiles to meld attribute
            for tile in meldTiles:
                self.player_melds[player][tile] += 1 

            called = self.last_discard_tile
            meldTiles.remove(called)  
            #removes tiles from player hand
            for tile in meldTiles:
                self.privateHands[player][tile] -= 1
            # adds pon if pon
            if meldType == 1:
                self.addPlayerPonTiles(player, meldTiles)
            # adds meld number
            self.addMeldNum(player, meldType)
