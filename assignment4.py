import os
import builtins

def create_index(input_file, output_path, sorted):
    print('Creating index from: ' + input_file + '\nTo: ' + output_path + '\nSorted: ' + str(sorted) + '\n')

    index_dict = {  'cat':    '1000', # Key, value dictionary for bitmap index
                    'dog':    '0100',
                    'turtle': '0010',
                    'bird':   '0001',
                    0:  '1000000000',
                    1:  '0100000000',
                    2:  '0010000000',
                    3:  '0001000000',
                    4:  '0000100000',
                    5:  '0000010000',
                    6:  '0000001000',
                    7:  '0000000100',
                    8:  '0000000010',
                    9:  '0000000001',
                    'True\n':  '10\n',
                    'False\n': '01\n'   }

    file, _ = os.path.splitext(os.path.basename(input_file)) # Grab just filename and remove suffix
    output_path = os.path.join(output_path, file) # Combine output path and filename

    if sorted:
        output_path = output_path + '_sorted' # Add sorted to filename

    with open(input_file, 'r') as i, open(output_path, 'w') as o: # Open io files

        lines = i.readlines()
        if sorted:
            lines = builtins.sorted(lines) # Sort file if needed
            
        for line in lines:
            species, age, adopted = line.split(',') # Split lines

            o.write(index_dict[species]) # Species

            age = int(age) # Age
            if age % 10 == 0:
                o.write(index_dict[(age // 10) - 1])
            else:
                o.write(index_dict[age // 10])

            o.write(index_dict[adopted]) # Adopted

def compress_index(bitmap_index, output_path, compression_method, word_size):
    print('Compressing index from: ' + bitmap_index + '\nTo: ' + output_path + '\nCompression Method: ' + compression_method + '\nWord Size: ' + str(word_size) +'\n')

    file = os.path.basename(bitmap_index) # Grab just filename and remove suffix
    output_path = os.path.join(output_path, file) # Combine output path and filename
    output_path = output_path + '_' + str(compression_method) + '_' + str(word_size) # Append proper suffix to output file

    grab_size = word_size - 1
    runs_0 = 0
    runs_1 = 0

    with open(bitmap_index, 'r') as i, open(output_path, 'w') as o:

        block = i.read(grab_size)
        while len(block) == grab_size:

            if '\n' in block:
                block = block.replace('\n', '')
                block += i.read(1)

            if block.count('0') == len(block): # Run of 0's
                if runs_1 > 0:
                    runs_1 = write_runs(o, runs_1, word_size, 1)
                runs_0 += 1

            elif block.count('1') == len(block): # Runs of 1's
                if runs_0 > 0:
                    runs_0 = write_runs(o, runs_0, word_size, 0)
                runs_1 += 1

            else: # Literal
                if runs_0 > 0:
                    runs_0 = write_runs(o, runs_0, word_size, 0)
                elif runs_1 > 0:
                    runs_1 = write_runs(o, runs_1, word_size, 1)
                o.write('0' + block + '\n')

            block = i.read(grab_size)

        if runs_1 > 0: # Flush runs of 1's
            runs_1 = write_runs(o, runs_1, word_size, 1)

        if len(block) != 0: # Leftover bits
            if '\n' in block:
                block = block.replace('\n', '')

                if len(block) == 0:
                    if runs_0 > 0:
                        runs_0 = write_runs(o, runs_0, word_size, 0)
                    return

            while len(block) != grab_size: # Pad rightmost side with 0's
                block += '0'

            if block.count('0') == len(block): # Run of 0's
                runs_0 = write_runs(o, runs_0 + 1, word_size, 0)
            else: # Literal
                o.write('0' + block + '\n')
        
        elif runs_0 > 0: # Flush runs of 0's
            runs_0 = write_runs(o, runs_0, word_size, 0)

def write_runs(o, runs, word_size, type):
    binary = bin(runs)[2:].zfill(word_size - 2) # Convert # of runs to binary and truncate leading 0b, then pad leftmost side with 0's up to word_size - 2
    if type == 0:
        o.write('10' + binary + '\n')
    elif type == 1:
        o.write('11' + binary + '\n')

    return 0

def compare_files(file_1, file_2):
    with open(file_1, 'r') as f1, open(file_2, 'r') as f2:
        return f1.read() == f2.read()

if __name__ == '__main__': # Assumes running from a4
    create_index('data/animals.txt', 'myOutput/', False) # Tests if all my bitmap creation works
    print(compare_files('data/bitmaps/animals', 'myOutput/animals'))

    create_index('data/animals_small.txt', 'myOutput/', False)
    print(compare_files('data/bitmaps/animals_small', 'myOutput/animals_small'))

    create_index('data/animals.txt', 'myOutput/', True) # Test if I sort lexographically
    print(compare_files('data/bitmaps/animals_sorted', 'myOutput/animals_sorted'))

    compress_index('myOutput/animals_small', 'myOutput/', 'WAH', 8)
    print(compare_files('data/compressed/animals_small_WAH_8', 'myOutput/animals_small_WAH_8'))