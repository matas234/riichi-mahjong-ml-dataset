from .testing_functions import printTestToFile


printTestToFile(0)





file1_path = 'testing/OLD.txt'
file2_path = 'testing/NEW.txt'


try:
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        contents1 = f1.readlines()
        contents2 = f2.readlines()

    # Compare the contents line by line
    max_lines = max(len(contents1), len(contents2))
    differences = []

    for i in range(max_lines):
        line1 = contents1[i] if i < len(contents1) else None
        line2 = contents2[i] if i < len(contents2) else None

        if line1 != line2:
            differences.append((i + 1, line1, line2))  # Store line number and differing lines

    if not differences:
        print("The files are the same.")
    else:
        print("The files are different.")
        for line_number, line1, line2 in differences:
            print(f"Line {line_number} differs:")
            if line1 is not None:
                print(f"  File 1: {line1.strip()}")
            else:
                print("  File 1: <No line>")
            if line2 is not None:
                print(f"  File 2: {line2.strip()}")
            else:
                print("  File 2: <No line>")

except FileNotFoundError as e:
    print(f"Error: {e}")
except IOError as e:
    print(f"Error reading file: {e}")