import os, shutil # shell utilities = allows us to perform various file-related tasks (copying, moving, ect)

path = os.path.join(os.path.expanduser("~"), "Downloads")

CATEGORIES = {
    "Images": ('.jpg', '.jpeg', '.png', '.gif', '.webp'),
    "Documents": ('.pdf', '.docx', '.txt'),
    "Videos": ('.mp4', '.mov'),
    "Audio": ('.mp3', '.wav'),
    "Archives": ('.zip', '.tar.gz', '.tar.xz', '.rar', '.7z'),
    "Executables": ('.exe', '.bat'),
    "Others": ('.psd', '.iso', '.msix')
}

for filename in os.listdir(path):
    for category, extensions in CATEGORIES.items():
        if filename.endswith(extensions):
            dest = os.path.join(path, category, filename)
            os.makedirs(os.path.join(path, category), exist_ok=True)
            if not os.path.exists(dest):
                shutil.move(os.path.join(path, filename), dest)
            break


