## Reducing the Latency of the UK Multimodal Public Transport System
This is the GitHub Repo for COMP5530M Group Project. 



## How to run the server
1. clone the repository
`git clone git@github.com:PatrykRosowski/COMP5530M-Group-Project.git`
2. setup virtual environment and install dependencies
- `cd COMP5530M-Group-Project`
- `python3 -m venv .venv`
- windows - `.venv\Scripts\activate`
- mac or linux - `source .venv/bin/activate`
- `pip install -r requirements.txt`
3. create .env file and populate secret key
4. set environment variable
- `export FLASK_APP=run.py`
- `export FLASK_DEBUG=1`
5. run server
- `flask run`
- if failed - `python3 run.py`
6. complete
- server url `127.0.0.1:5000`


## Routing engine setup
1. install docker desktop or docker on your cli
- make sure docker is installed properlly `docker --version`
2. setup the docker container
- `docker-compose up valhalla`
3. wait few minutes for map building
- server url `127.0.0.1:8002`
- to check server status `127.0.0.1:8000/status`
4. other commands
- to start server `docker start valhalla`
- to stop server `docker stop valhalla`
