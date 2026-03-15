import os

def create_folder(name="NewFolder"):
    if not os.path.exists(name):
        os.mkdir(name)