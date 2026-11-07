import subprocess

def create_container(image_name, container_name, host_port, container_port):
    command =[
        "docker",
        "create",
        "--name",
        container_name,                ##Docker create --name <container_name> -p host_p:cont_p <img_name>
        "-p",
        f"{host_port}:{container_port}",
        image_name
    ]
    result = subprocess.run(command,check=True,capture_output=True,text=True)
     ##check=True: Raise an error if Docker fails.
     ##capture_output=True: Capture Docker's output instead of immediately printing it.
     ##text=True: Return output as readable strings instead of bytes.
    
    container_id=result.stdout.strip()

    print(f"CONTAINER CREATED SUCCESSFULLY !!!!")
    print(f"Container ID ::{container_id}")

    return container_id
#..........................................................................................
def start_container(container_id):
    command=[
        "docker",
        "start",
        container_id
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )
    print("CONTAINER STARTED SUCCESS")
    print(f"container::{result.stdout.strip()}")
    return result.stdout.strip()
    #..............................................................................................
def stop_container(container_id):
    command=[
        "docker",
        "stop",
        container_id
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )
    print("CONTAINER STOPPED")
    print(f"container::{result.stdout.strip()}")
    return result.stdout.strip()
#.........................................................................................................
def remove_container(container_id):
    command=[
        "docker",
        "rm",
        container_id
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )
    print("CONTAINER REMOVEEEED")
    print(f"container::{result.stdout.strip()}")
    return result.stdout.strip()
##///////////////////////////////////////////////
def get_container_status(container_id):
    command=[
        "docker",
        "inspect",
        "--format",
        "{{.State.Status}}",
        container_id
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )
    status = result.stdout.strip()
    print(f"container status::{status}")
    return status
