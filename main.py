from process_replay import saveAll


if __name__ == "__main__":
    saveAll(years = [2016, 2017, 2018, 2019, 2020],   #available years: 2016, 2017, 2018, 2019, 2020
            path_to_save_in = "C:\\Users\\msaba\\Documents\\GitHub\\actual-dataset",
            path_to_db_file = "C:\\Users\\msaba\\Documents\\GitHub\\riichi-dataset\\es4p.db")

