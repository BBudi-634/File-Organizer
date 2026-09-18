import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

path = r"C:/Users/Lolsiest/Downloads/" # hardcoded. DON'T FORGET TO CHANGE AND MAKE IT NOT HARDCODED!!!!!!!!!!!!!

CATEGORIES = {
    "Images": ('.jpg', '.jpeg', '.png', '.gif', 'webp'),
    "Documents": ('.pdf', '.docx', '.txt'),
    "Videos": ('.mp4', '.mov'),
    "Audio": ('.mp3', '.wav'),
    "Archives": ('.zip', '.tar.gz', '.tar.xz'),
    "Executables": ('.exe', '.bat')
}

for filename in os.listdir(path):
    for category, extensions in CATEGORIES.items():
        if filename.endswith(extensions):
            dest = os.path.join(path, category, filename)
            if not os.path.exists(dest):
                shutil.move(path + filename, dest)
            break


