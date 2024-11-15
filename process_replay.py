import bz2
import sqlite3
from typing import List
import h5py
from lxml import etree
import xml.etree.ElementTree as ET
from tqdm import tqdm

from gamelog_to_states import gamelogToStates


#redefine numGames so don't cook my computer
NUMGAMES = 300


dbfile = 'es4p.db'
con = sqlite3.connect(dbfile)
cur = con.cursor()
res = cur.execute(f"SELECT log_id, log_content FROM logs")


game_logs = []
for i in range(NUMGAMES):
    game_logs.append(res.fetchone())

con.close()


### takes a game_log from the .db file, decrompresses it, formats the xml, returns (game_id, game_replay)
def convertLog(log):
    blob = log[0]

    XML = etree.XML

    decompress = bz2.decompress
    content = decompress(blob)

    xml = XML(content, etree.XMLParser(recover=True))

    rough_string = ET.tostring(xml, encoding='unicode')
    root = ET.fromstring(rough_string)

    game_replay = [(element.tag, element.attrib) for element in root]

    return game_replay




TOTAL_ROWS = 10_000#75_000_000
CHUNK_SIZE = 2048
COMPRESSION = "gzip"


def saveAll(years: List[int], path_to_save_in: str, path_to_db_file: str):
    with h5py.File(r"C:\Users\msaba\Documents\GitHub\actual-dataset\hanchan_hp5\file.h5", "w") as h5_file:
        DATASETS_NAMES_TPL = (
            'riichi_states',
            'riichi_labels',
            'chi_states',
            'chi_labels',
            'pon_states',
            'pon_labels',
            'kan_states',
            'kan_labels'
        )

        dataset_cur_idx_lst = [0] * 8


        for idx, name in enumerate(DATASETS_NAMES_TPL):
            size = 374 if idx%2 == 0 else 2

            h5_file.create_dataset(name,
                                   shape=(TOTAL_ROWS, size),
                                   maxshape=(None, size),
                                   compression=COMPRESSION,
                                   chunks=(CHUNK_SIZE, size))

        dbfile = path_to_db_file

        con = sqlite3.connect(dbfile)
        cur = con.cursor()
        res = cur.execute("SELECT COUNT(*) FROM logs")
        num_games = res.fetchone()[0]
        res = cur.execute("SELECT log_content FROM logs")

        for _ in tqdm(range(num_games), desc="Processing"):
            log = res.fetchone()

            # print(f"Processing {log[0]}")
            game = convertLog(log)

            game_tupl = gamelogToStates(game)

            for idx in range(8):
                dataset = h5_file[DATASETS_NAMES_TPL[idx]]
                dataset_idx = dataset_cur_idx_lst[idx]
                game = game_tupl[idx]

                dataset[dataset_idx : dataset_idx+game.shape[0], :] = game_tupl[idx]
                dataset_cur_idx_lst[idx] += game.shape[0]



            for name, dataset, cur_idx in zip(DATASETS_NAMES_TPL, [h5_file[name] for name in DATASETS_NAMES_TPL], dataset_cur_idx_lst):
                new_size = cur_idx
                dataset.resize((new_size, dataset.shape[1]))
