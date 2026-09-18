import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

path = r"C:/Users/Lolsiest/Downloads/" # hardcoded. DON'T FORGET TO CHANGE AND MAKE IT NOT HARDCODED!!!!!!!!!!!!!

file_name = os.listdir(path) # shows all files in the path

folder_names = ['Images', 'Documents', 'Videos', 'Audio', 'Archives', 'Executables']

for loop in range(0,6):
    if not os.path.exists(path + folder_names[loop]):
        print(path + folder_names[loop])
        os.makedirs(path + folder_names[loop])

for file in file_name:
    if '.pdf' in file and not os.path.exists(path + "Documents/" + file):
        shutil.move(path + file, path + "Documents/" + file)
    if '.png' in file and not os.path.exists(path + "Images/" + file):
        shutil.move(path + file, path + "Images/" + file)
    if '.jpg' in file and not os.path.exists(path + "Images/" + file):
        shutil.move(path + file, path + "Images/" + file)
    if '.jpeg' in file and not os.path.exists(path + "Images/" + file):
        shutil.move(path + file, path + "Images/" + file)

    if '.docx' in file and not os.path.exists(path + "Documents/" + file):
        shutil.move(path + file, path + "Documents/" + file)
    if '.xlsx' in file and not os.path.exists(path + "Documents/" + file):
        shutil.move(path + file, path + "Documents/" + file)

    if '.zip' in file and not os.path.exists(path + "Archives/" + file):
        shutil.move(path + file, path + "Archives/" + file)

    if '.exe' in file and not os.path.exists(path + "Executables/" + file):
        shutil.move(path + file, path + "Executables/" + file)


