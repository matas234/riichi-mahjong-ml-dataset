from typing import List, Tuple

import numpy as np


splits_groups_cache: dict[Tuple[int], Tuple[int, int, bool]] = {}
splits_nogroups_cache: dict[Tuple[int], Tuple[int, bool]] = {}



def getPairs(suit_arr: List[int]):
    possible_pairs=[]
    for i in range(9):
        if suit_arr[i]>1:
            out = [0]*9
            out[i] = 2
            possible_pairs.append(out)
    return possible_pairs


def getTriplets(suit_arr: List[int]):
    possible_triplets=[]
    for i in range(9):
        if suit_arr[i]>2:
            triplet = [0]*9
            triplet[i] = 3
            possible_triplets.append(triplet)
    return possible_triplets


def completeSequences(suit_arr: List[int]):
    possible_sequences=[]
    for i in range(2,9):
        if all(suit_arr[i-j]>0 for j in range(3)):
            out = [0]*9
            out[i]=1
            out[i-1]=1
            out[i-2]=1
            possible_sequences.append(out)
    return possible_sequences


def incompleteSequences(suit_arr: List[int]):
    possible_insequences=[]
    if suit_arr[0]>0 and suit_arr[1]>0:
        out = [0]*9
        out[0]=1
        out[1]=1
        possible_insequences.append(out)
    for i in range(2,9):
        if suit_arr[i]>0 and suit_arr[i-1]>0:
            out = [0]*9
            out[i]=1
            out[i-1]=1
            possible_insequences.append(out)
        if suit_arr[i]>0 and suit_arr[i-2]>0:
            out = [0]*9
            out[i]=1
            out[i-2]=1
            possible_insequences.append(out)
    return possible_insequences



def hashSuitArr(suit_arr: List[int]):
    return sum(1 << (2 * tile)
               for tile in suit_arr)


def splitsNoGroups(suit_arr: List[int]):
    suit_tuple = tuple(suit_arr)
    if suit_tuple in splits_nogroups_cache:
        return splits_nogroups_cache[suit_tuple]

    max_taatsu_num = 0
    max_pair_presence = False

    inseqs_list = incompleteSequences(suit_arr)
    pairs_list = getPairs(suit_arr)

    for pair in pairs_list:
        cur_taatsu_num = splitsNoGroups([h - p for h, p in zip(suit_arr, pair)])[0] + 1
        if cur_taatsu_num > max_taatsu_num:
            max_taatsu_num = cur_taatsu_num
            max_pair_presence = True

    for inseq in inseqs_list:
        cur_taatsu_num, cur_pair_presence = splitsNoGroups([h - i for h, i in zip(suit_arr, inseq)])
        cur_taatsu_num += 1
        if cur_taatsu_num > max_taatsu_num:
            max_taatsu_num = cur_taatsu_num
            max_pair_presence = cur_pair_presence

    splits_nogroups_cache[suit_tuple] = (max_taatsu_num, max_pair_presence)

    return max_taatsu_num, max_pair_presence


def splits(suit_arr: List[int], groupNum: int = 0, pair_presence: bool = False):
    ## checks if suit_arr is cached
    suit_tuple = tuple(suit_arr)

    if suit_tuple in splits_groups_cache:
        (cached_group_num, cached_tatsu_num, cached_pair_presence) = splits_groups_cache[suit_tuple]

        return (cached_group_num + groupNum,
                cached_tatsu_num,
                cached_pair_presence or pair_presence)

    max_grp_num = groupNum
    max_tatsu_num = 0
    max_pair_presence = pair_presence

    seqs = completeSequences(suit_arr)
    triplets = getTriplets(suit_arr)

    for meld in seqs + triplets:
        cur_grp_num, cur_taatsu_num, cur_pair_presence = splits([h - m for h, m in zip(suit_arr, meld)], groupNum+1, pair_presence)

        if cur_grp_num > max_grp_num:
            max_grp_num = cur_grp_num
            max_tatsu_num = cur_taatsu_num
            max_pair_presence = cur_pair_presence

        elif cur_grp_num == max_grp_num:
            if cur_taatsu_num > max_tatsu_num or (cur_taatsu_num == max_tatsu_num and cur_pair_presence):
                max_tatsu_num = cur_taatsu_num
                max_pair_presence = cur_pair_presence

    if (not seqs) and (not triplets):     #if no more groups then counts maximum of taatsu
        max_tatsu_num, max_pair_presence = splitsNoGroups(suit_arr)


    splits_groups_cache[suit_tuple] = (max_grp_num - groupNum, max_tatsu_num, max_pair_presence)

    return max_grp_num, max_tatsu_num, max_pair_presence


def splitsTotal(hand: List[List[int]]):
    ## num of groups, num of taatsu, has pair
    total_split = [0,0,False]

    for suit_tiles in hand[:3]:
        suit_split = splits(suit_arr = suit_tiles)
        total_split[0] += suit_split[0]
        total_split[1] += suit_split[1]
        total_split[2] |= suit_split[2]

    for honour_tile in hand[3]:
        if honour_tile >= 3:
            total_split[0] += 1
        elif honour_tile == 2:
            total_split[1] +=1
            total_split[2] = True

    return total_split


def generalShanten(hand_array: List[List[int]], numCalledMelds: int = 0):
    total_split = splitsTotal(hand_array)
    taatsu_num = total_split[1]
    group_num = total_split[0] + numCalledMelds
    pair_presence = total_split[2]
    p=0

    #checking for the edge cases:
    if (taatsu_num >= 5-group_num) and (not pair_presence):
        p=1

    # using formula
    return 8 - 2*group_num - min(taatsu_num, 4 - group_num) - min(1, max(0, taatsu_num + group_num - 4) ) + p


def chiitoitsuShanten(hand_array: List[List[int]]):
    num_pairs = 0
    for suit in hand_array:
        for tile in suit:
            num_pairs += tile//2      #counts number of pairs, 4 of the same tile are treated as 2 pairs

    return 6 - num_pairs


def orphanSourceShanten(hand_array: List[List[int]]):
    diff_terminals = 0
    pairs_terminals = 0
    pair_const = 0

    for i in [0,8]:                  #iterates over numbered suits
        for suit in hand_array[:3]:
            pairs_terminals += min(1, suit[i]//2)
            diff_terminals += min(1, suit[i])

    for num in hand_array[3]:        #iterates over honours
        pairs_terminals += min(1, num//2)
        diff_terminals += min(1, num//1)

    if pairs_terminals > 0:
        pair_const=1

    return 13 - diff_terminals - pair_const


SPLIT_INDICES = [9,18,27,34]

def calculateShanten(hand: List[int], called_melds_num: int = 0):
    hand_array = [hand[i:j] for i, j in zip([0] + SPLIT_INDICES[:-1], SPLIT_INDICES)]

    return min(generalShanten(hand_array, called_melds_num),
               chiitoitsuShanten(hand_array),
               orphanSourceShanten(hand_array))
