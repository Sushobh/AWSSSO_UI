from typing import Any
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ConfigFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
app = FastAPI()
config = ConfigFile()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.mount("/browser", StaticFiles(directory="browser"), name="")

@app.get('/')
def get_app_angular():
    with open('browser/index.html', 'r') as file_index:
        html_content = file_index.read()
    return HTMLResponse(html_content, status_code=200)


@app.get("/getProfiles")
async def getprofiles():
    return Response(status = 'PROFILES_FETCHED',data = config.getProfiles())

@app.get("/shutDown")
async def shutDown():

    return Response(status = 'SHUTDOWN',data="")

@app.get("/openLogin/{profile_name}")
async def openlogin(profile_name : str):
    config.spawn_cli_for_auth2(config.get_profile_by_name(profile_name).name)
    return Response(status = 'LOGIN_OPENED',data = '')

@app.get("/refreshCreds/{profile_name}")
async def refreshCreds(profile_name : str):
    profile = config.get_profile_by_name(profile_name)
    creds = profile.get_new_credentials()
    if creds == None:
        return Response(status='CREDS_EXPIRED_SPAWN_LOGIN',failed = True,data = ' ')
    config.store_aws_credentials(profile,creds)
    return Response(status = 'CREDS_RENEWED',data = config.getProfiles())

@app.get("/moveToDefault/{profile_name}")
async def moveToDefault(profile_name : str):
    config.move_profile_to_default(config.get_profile_by_name(profile_name))
    return Response(status='MOVED_PROFILE_TO_DEFAULT', data=config.getProfiles())



class Response:
    failed : bool = False
    status : str = 'SUCCESS'
    data : Any

    def __init__(self,status : str,data : Any,failed : bool = False,):
        self.failed = failed
        self.status = status
        self.data = data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
