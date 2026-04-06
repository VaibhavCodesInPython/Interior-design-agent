import base64
import os
import subprocess
import sys
def open_file(path:str)-> None:
    if sys.platform.startswith("darwin"): # for macos
        subprocess.run(["open",path],check=False)
    elif os.name == "nt": #for windos
        os.startfile(path)
    elif os.name == "posix": #for linux
        subprocess.run(["xdg-open",path],check=False)
    else:
        print(f"Unregistered platform encountered. Platform type: {sys.platform}")

def retrieve_image_from_resources(path: str):
    if not os.path.isabs(path):
        path= os.path.join("resources",path)
    with open(path,'rb') as f:
        base64_image = base64.b64encode(f.read().decode("utf-8"))
    return base64_image