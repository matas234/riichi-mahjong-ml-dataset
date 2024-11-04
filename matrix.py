
import numpy as np
from global_helper_functions import formatHandFromXML
from shanten_calculator import calculateShanten

class Matrix:     
    def __init__(self):
        self.gameState = np.zeros((11, 34), dtype=np.int16)
        self.privateHands = [[0]*34 for _ in range(4)]
        self.playerMelds = [[0]*34 for _ in range(4)]
        self.playerPool = [[0]*34 for _ in range(4)]
        self.doras = [0]*34
        self.Riichi = [False, False, False, False]

        # metadata
        self.roundWind = 0   #0:E, 1:S, ...
        self.playerScores = [0, 0, 0, 0]
        self.playerWinds = [0,1,2,3]
        self.honbaSticks = 0
        self.roundWind = 0
        self.roundDealer = 0
        self.wallTiles = 70      # technically 69 but the dataset considers dealer 14th tile as a draw
        self.chisNum = [0,0,0,0]    #
        self.ponsNum = [0,0,0,0]    # num of melds for each player
        self.kansNum = [0,0,0,0]    #

        #used to keep track of things
        self.lastDrawPlayer = 0
        self.lastDrawTile = 0       
        self.lastDiscardPlayer = 0
        self.lastDiscardTile = 0
        self.closedKans = [0,0,0,0]       
        self.Closed = [True, True, True, True]  
        self.playerPons = [[], [], [], []]        #pons for each player, need for closed kan/chankan 

    def getRiichi(self, player):   #needed
        return self.Riichi[player]
    
    def setRiichi(self, player):
        self.Riichi[player] = True

    # builds matrix for POV player
    # forMeld   Riichi: False , Meld: true   (only difference is last discard)   
    def buildMatrix(self, player, forMeld=False, forClosedMeld=False, callTile=None):
        # player ordering relative to input player. e.g. player =2  => player_ordering = [2,3,0,1]   (counterclockwise on table)
        player_ordering = [i%4 for i in range(player,player+4)]

        #round wind
        self.gameState[0][0] = self.roundWind
        #dealer
        self.gameState[0][1] = player_ordering.index(self.roundDealer)
        #pov wind
        self.gameState[0][2] = self.playerWinds[player]        
        #num of honba sticks
        self.gameState[0][3] = self.honbaSticks
        #num of riichi sticks
        self.gameState[0][4] = self.Riichi.count(True)  
        #num of tiles left in wall (kans might mess this up need to check)
        self.gameState[0][5] = self.wallTiles
        #padding
        self.gameState[0][30:33] = -128
        #round number
        self.gameState[0][33] = self.roundDealer + 1    
        
        #pov hand
        self.gameState[2] = self.privateHands[player]

        for index,player in enumerate(player_ordering):
            #melds
            self.gameState[3+index] = self.playerMelds[player]
            #pools
            self.gameState[7+index] = self.playerPool[player]

            #scores
            self.gameState[0][6+index] = self.playerScores[player]
            #riichis
            self.gameState[0][10+index] = 1 if self.Riichi[player] else 0
            #number of chis
            self.gameState[0][14+index] = self.chisNum[player]
            #number of pons
            self.gameState[0][18+index] = self.ponsNum[player]
            #number of kans
            self.gameState[0][22+index] = self.kansNum[player]
            # 0: closed, 1: open
            self.gameState[0][26+index] = 0 if self.Closed[player] else 1


        # sets call tile for the meld matrices
        if forMeld:
            if forClosedMeld:
                self.gameState[0][30] = callTile
            else:
                self.gameState[0][30] = self.lastDiscardTile
            

    def getMatrix(self):  
        return self.gameState
    
    def addPlayerPonTiles(self, player, tiles):
        self.playerPons[player].append(tiles[0])

    def decPlayerPonTiles(self, player, tiles):
        self.playerPons[player].remove(tiles[0])

    def getPlayerPonTiles(self, player):
        return self.playerPons[player]

    def addClosedKan(self, player):
        self.closedKans[player] += 1           

    def getClosedKan(self, player):  #needed
        return self.closedKans[player]

    def addPlayerPool(self, player, tile):
        self.playerPool[player][tile] += 1

    def decPlayerPool(self, player, tile):
        self.playerPool[player][tile] -= 1
    
    def addChi(self, player):
        self.chisNum[player] += 1

    def addPon(self, player):
        self.ponsNum[player] += 1

    def decPon(self, player):
        self.ponsNum[player] -= 1

    def addKan(self, player):
        self.kansNum[player] += 1

    def addMeldNum(self, player, meldType):
        if meldType == 0:
            self.addChi(player)
        elif meldType == 1:
            self.addPon(player)
        elif meldType == 2:
            self.addKan(player)    

    def getMeldNum(self, player):
        return self.chisNum[player] + self.ponsNum[player] + self.kansNum[player]

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
        dealer = self.roundDealer
        self.playerWinds = [(i-dealer)%4 for i in range(4)]

    def setRoundWind(self, wind):
        self.roundWind = wind
    
    def setDealer(self, dealer):
        self.roundDealer = dealer

    #input amount 
    def setHonbaSticks(self, amount):
        self.honbaSticks = amount
    
    #decrement wall tiles by one
    def decWallTiles(self):
        self.wallTiles -=1
    
    def getWallTiles(self):
        return self.wallTiles
    
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
        self.lastDiscardPlayer = player

    def getLastDiscardPlayer(self):
        return self.lastDiscardPlayer

    def setLastDiscardTile(self, tile):
        self.lastDiscardTile = tile

    def getLastDiscardTile(self):
        return self.lastDiscardTile
    
    def setLastDrawPlayer(self, player):
        self.lastDrawPlayer = player

    def getLastDrawPlayer(self):
        return self.lastDrawPlayer
    
    def setLastDrawTile(self, tile):
        self.lastDrawTile = tile

    def getLastDrawTile(self):
        return self.lastDrawTile

    #input tile (0-34)
    def addDoraIndicator(self, doraIndicator):
        self.gameState[1][doraIndicator] += 1
            
    def canPon(self, player):
        tile = self.lastDiscardTile
        return (self.privateHands[player][tile] >= 2) and not self.getRiichi(player)

    def canKan(self, player):
        tile = self.lastDiscardTile
        return (self.privateHands[player][tile] == 3) and not self.getRiichi(player)

    def canChi(self, player): 
        
        tile = self.lastDiscardTile
        fromPlayer = self.lastDiscardPlayer

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
            playerHasTile_inPon = (tile in self.playerPons[player])

            if playerHasTile_inHand and playerHasTile_inPon:
                canChackan = True
                callTile = tile
                break
        
        return canChackan , callTile

    def canRiichi(self, player):
        return (not self.Riichi[player] and
                self.Closed[player] and
                calculateShanten(hand=self.privateHands[player], numCalledMelds=self.closedKans[player]) <= 0 and
                self.wallTiles >= 4)


    def setOpen(self, player):
        self.Closed[player] = False
    
    def getClosed(self, player):
        return self.Closed[player]

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
            self.playerMelds[player][ meldTiles[0] ] = 4
            self.addKan(player)
            self.privateHands[player][ meldTiles[0] ] = 0
       
        # handles closed kan       
        elif isClosedCall:
            self.privateHands[player][ meldTiles[0] ] = 0
            self.addKan(player)
            self.playerMelds[player][ meldTiles[0] ] = 4

        # handles regular call
        else:
            self.setOpen(player)
            # adds meld tiles to meld attribute
            for tile in meldTiles:
                self.playerMelds[player][tile] += 1 

            called = self.lastDiscardTile
            meldTiles.remove(called)  
            #removes tiles from player hand
            for tile in meldTiles:
                self.privateHands[player][tile] -= 1
            # adds pon if pon
            if meldType == 1:
                self.addPlayerPonTiles(player, meldTiles)
            # adds meld number
            self.addMeldNum(player, meldType)
