import subprocess
import sys
from pathlib import Path

def build_image(app_dir,image_name):
    
    app_path = Path(app_dir).resolve() #convert apppath to an absolute path 

    if not app_path.is_dir():
        raise FileNotFoundError("directory napalu bhai !! ") ##checks if its a dir

    dockerfile = app_path/"Dockerfile"
    
    if not dockerfile.is_file():
        raise FileNotFoundError("Dockerfile tu nai nohoi ...") #checks if its a file

    print(f"Building image ::{image_name}")
    
    
    #now we make the Docker build command ...................................................

    command=[
             "docker",
             "build",
             "-t",
             image_name,
             str(app_path)
    ] 

    ##executing the build command 
    subprocess.run(command,check=True)
    print(f"image '{image_name}' WAS BUILT SUCCESSFULLY !!!!")


if __name__ == "__main__": #sys.args stores info we type after python in terminal

    if len(sys.argv) != 3:
        print("usage: python builder.py <app_dir> <image_name>")
        sys.exit(1)

    app_dir = sys.argv[1]
    image_name = sys.argv[2]

    build_image(app_dir, image_name)
