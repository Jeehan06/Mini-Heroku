# Mini-Heroku — Project Notes

> **Purpose:** A small, self-hosted PaaS prototype that automates the process of building and running containerized applications.
>
> **Project status:** Foundational Docker setup and automated image building are working. Container lifecycle automation, port allocation, and the deployment manager are still to be implemented.

---

## 1. Project goal

The long-term goal is to deploy a small application using one command, for example:

```bash
python3 deployment/manager.py ./hello
```

The manager should eventually:

1. Validate the application directory.
2. Build a Docker image for the application.
3. Create and start a container from that image.
4. Allocate an available host port.
5. Make the application reachable through a URL.
6. Report deployment status and useful errors.

This is a learning prototype, not a production replacement for Heroku.

## 2. Technology stack

| Technology | Purpose in this project |
|---|---|
| Python | Automation and orchestration logic |
| Docker | Builds images and runs isolated containers |
| Flask | Example web application |
| Linux | Development and host environment |
| `subprocess` | Lets Python execute Docker CLI commands |
| `pathlib` | Handles filesystem paths |

## 3. Current project structure

The known project files are:

```text
mini-heroku/
├── deployment/
│   └── builder.py
└── hello/
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```

The project folder on the development machine is:

```text
/home/jeeshan/Desktop/mini heroku learning guide
```

Planned files (not yet confirmed as implemented):

```text
deployment/
├── builder.py       # implemented: builds Docker images
├── container.py     # planned: container lifecycle operations
├── port_manager.py  # planned: host-port allocation
└── manager.py       # planned: coordinates a full deployment
```

## 4. Example application

The `hello/` directory contains a small Flask application.

The application listens on port `5000` and must bind to `0.0.0.0` inside the container so that Docker's port forwarding can reach it.

A simple example:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "hello from the container"

app.run(host="0.0.0.0", port=5000)
```

`requirements.txt`:

```text
flask
```

## 5. Dockerfile

The current Dockerfile:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```

What each instruction does:

| Instruction | Meaning |
|---|---|
| `FROM python:3.12-slim` | Starts from a small image that already has Python 3.12 |
| `WORKDIR /app` | Sets `/app` as the working directory inside the image |
| `COPY requirements.txt .` | Copies the dependency list into the image |
| `RUN pip install -r requirements.txt` | Installs Flask and other listed dependencies while building |
| `COPY app.py .` | Copies the application code into the image |
| `CMD ["python", "app.py"]` | Runs the Flask application when a container starts |

## 6. What we have implemented: `builder.py`

**Status: Implemented and successfully tested.**

The builder accepts an application directory and an image name. It checks that the directory and its Dockerfile exist, then asks Docker to build an image.

Current implementation:

```python
import subprocess
import sys
from pathlib import Path


def build_image(app_dir, image_name):
    app_path = Path(app_dir).resolve()

    if not app_path.is_dir():
        raise FileNotFoundError("Application directory does not exist.")

    dockerfile = app_path / "Dockerfile"

    if not dockerfile.is_file():
        raise FileNotFoundError("Dockerfile was not found in the application directory.")

    print(f"Building image: {image_name}")

    command = [
        "docker",
        "build",
        "-t",
        image_name,
        str(app_path)
    ]

    subprocess.run(command, check=True)
    print(f"Image '{image_name}' was built successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 builder.py <app_dir> <image_name>")
        sys.exit(1)

    app_dir = sys.argv[1]
    image_name = sys.argv[2]

    build_image(app_dir, image_name)
```

### How to run it

From the project root:

```bash
python3 deployment/builder.py ./hello miniheroku-hello
```

This command was successfully run. Docker reported that the image was built and tagged as `miniheroku-hello:latest`.

Docker also displayed a warning that the legacy image builder is deprecated and recommends BuildKit/buildx. The build itself succeeded; this warning did not stop the build.

### Important Python concepts used

- `Path(app_dir).resolve()` converts the supplied path into an absolute path.
- `app_path.is_dir()` checks whether the path is an existing directory.
- `app_path / "Dockerfile"` joins the directory path with the filename.
- `dockerfile.is_file()` checks whether the Dockerfile exists as a file.
- `sys.argv` contains command-line arguments. `sys.argv[0]` is the script name; the next two entries are the app directory and image name.
- `len(sys.argv) != 3` checks that the user supplied exactly two arguments after the script name.
- `if __name__ == "__main__":` makes the command-line section run only when this file is executed directly. It will not run when another Python file imports `build_image()`.
- `subprocess.run(command, check=True)` runs Docker from Python. If Docker exits with an error, Python raises an exception instead of pretending the build succeeded.
- Passing a list to `subprocess.run()` keeps arguments separate and safely handles paths containing spaces.

### A bug we fixed

Initially, the `if __name__ == "__main__":` section was indented inside `build_image()`. That meant the command-line section was in the wrong place and could cause the function to call itself again.

We moved that section back to the top level (no indentation under the function). This is important because `build_image()` should do one job: build an image. The command-line block should handle input arguments and call the function.

## 7. Docker concepts covered so far

### Image vs container

| Docker image | Docker container |
|---|---|
| A packaged template of an application and its environment | A running or stopped instance created from an image |
| Similar to a recipe or application template | Similar to a prepared meal made from that recipe |
| Built using a Dockerfile | Created from an image |

One image can be used to create multiple containers.

### Host port and container port

A mapping such as:

```bash
-p 8001:5000
```

means:

- `8001` is the port on the host machine.
- `5000` is the port inside the container where Flask listens.

A later deployment could use a different host port for each application while the apps all listen on port `5000` internally.

### `0.0.0.0` vs `127.0.0.1`

- `127.0.0.1` means “only accept connections through this machine's own loopback interface.”
- `0.0.0.0` means “listen on all available network interfaces.”

Inside a container, binding Flask to `0.0.0.0` allows Docker's port forwarding to reach the application.

### Image tags

An image can have multiple tags. We observed that `hello:latest` and `miniheroku-hello:latest` referred to the same image ID at that point. Different tags do not necessarily mean different image contents.

`latest` is just a tag name; it is not a guarantee that Docker always selects the newest build.

## 8. Useful Docker commands learned

These are manual inspection/testing commands. The eventual Mini-Heroku workflow should execute the required Docker operations automatically through Python.

| Command | Purpose |
|---|---|
| `docker images` | List locally available images |
| `docker ps` | List running containers |
| `docker ps -a` | List running and stopped containers |
| `docker logs <container>` | View a container's output |
| `docker image rm <image>` | Remove an image tag/image, if it is not in use |
| `docker build -t <name> <directory>` | Build an image manually |

Do not remove unrelated containers or images as part of routine project testing.

## 9. Implementation status

| Component | Status | Responsibility |
|---|---|---|
| Flask sample app | Exists | Example app to deploy |
| Dockerfile | Exists | Describes how to package the app |
| `builder.py` | **Implemented and tested** | Builds an image through Python |
| `container.py` | Not implemented yet | Creates, starts, stops, lists, and removes containers |
| `port_manager.py` | Not implemented yet | Finds and tracks available host ports |
| `manager.py` | Not implemented yet | Coordinates the complete deployment process |
| Tests and documentation | In progress | Verify behavior and explain the system |

## 10. Next steps

We will implement the project one component at a time:

1. **`container.py`** — automate container creation and lifecycle operations using Python's `subprocess` module.
2. **`port_manager.py`** — allocate an available host port for each deployed app.
3. **`manager.py`** — connect the builder, container manager, and port manager into one deployment command.
4. **Testing** — deploy more than one app, check URLs, and test common failure cases.
5. **Documentation/demo** — document architecture, commands, limitations, and a repeatable demonstration.

### Important design principle

The user should not have to manually type `docker build` or `docker run` every time they deploy an application. Those Docker commands will be invoked internally by the Python modules. The final user-facing workflow should be a single Mini-Heroku command.

---

## 11. Change log

- **2026-10-28 to 2026-10-29:** Set up and tested a basic Flask application in Docker; learned the image/container distinction and basic port mapping.
- **2026-10-31 to 2026-11-03:** Created the `deployment` directory and implemented `builder.py` to validate an app directory and automate Docker image building.
- **Next update:** Add the `container.py` implementation and its tests here.
