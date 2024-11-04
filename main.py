import time
from process_replay import saveAll, printTestToFile



saveAll([2018])



printTestToFile(0)



# start_time = time.time()

# start_time = time.time()

# saveAll()

# end_time = time.time()

# duration = end_time - start_time

# print(f"saveAll() took {duration:.4f} seconds")





file1_path = 'out.txt'
file2_path = 'out2.txt'

try:
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        contents1 = f1.read()
        contents2 = f2.read()

    if contents1 == contents2:
        print("The files are the same.")
    else:
        print("The files are different.")
except FileNotFoundError as e:
    print(f"Error: {e}")
except IOError as e:
    print(f"Error reading file: {e}")