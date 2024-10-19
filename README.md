# Locust Coding Challenge

This is my entry for the the coding challenge 🚀 
To start there of course improvements that could be made but time is limited. Some obvious ones:
- Unit tests. Had I more time I would have written unit tests using Pytest.
- Typing. Adding Mypy as a tool and typing as much as possible of the code.
- Add doc strings and more comments.
- Working docker compose spec

## Prerequisites
- This repo makes use of `uv` package/project manager,  see installation notes - https://docs.astral.sh/uv/getting-started/installation/
- After cloning the repo, run `uv sync` to create a virtual environment and install the dependencies
- The app requires a connection to a postgres db instance. Connection variables can be set in the `.env` file.
- Fire up our web app using `fastapi dev .\app\main.py`

## Usage
The FastApi app can be started in development mode using the command `fastapi dev .\app\main.py`. This triggers a lifespan event in `main.py` that in turn run `init_db()`. This function creates three tables based on the models in `app.models` as well as creating a initial user that can be used for authenticating towards the routes.

Once the Fastapi is up and running we can in another bash terminal run the script that measures cpu usage: 
```bash
cpu_monitor  --john@test.com  --password secret
```
cpu_monitor is a separate installable python package, and an dependency of our Fastapi app. See `pyproject.toml` where we point to its wheel -> `cpu-monitor = { path = "cpu_monitor/dist/cpu_monitor-0.1-py3-none-any.whl" }`.
The cpu_monitor package pyproject file includes: 
```toml
[project.scripts]
cpu_monitor = "cpu_monitor:main"
```
This makes `cpu_monitor` an available command that will run `cpu_monitor.main` with the provided args. Note that the provided credentials needs to match a user in the db. The script can be stopped by pressing Ctrl-C, which will trigger a method that displays the final cpu usage report.
Available arguments:
- username
- password
- measure_interval (defaults to 5 seconds)
- display_interval (defaults to 10 seconds)
- threshold (defaults to 5)
Example run of script:

![bild](https://github.com/user-attachments/assets/03bf083d-0c73-4e4f-a317-f7bb8a5f68fc)


