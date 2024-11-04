from .testing_functions import printTestToFile


printTestToFile(0)

file1_path = 'testing/out.txt'
file2_path = 'testing/out2.txt'

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