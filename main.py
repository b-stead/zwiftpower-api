import keyring
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from zpdatafetch import ZPCyclistFetch, ZPTeamFetch

KEYRING_SERVICE = "zpdatafetch"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    username = keyring.get_password(KEYRING_SERVICE, "username")
    password = keyring.get_password(KEYRING_SERVICE, "password")
    if not username or not password:
        raise RuntimeError(
            "ZwiftPower credentials not found in system keyring.\n"
            "Run: zpdata config\n"
            "or set manually:\n"
            "  keyring set zpdatafetch username\n"
            "  keyring set zpdatafetch password"
        )
    yield


app = FastAPI(title="Zwift Racing API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/rider/{zwift_id}")
async def get_rider(zwift_id: int):
    """Fetch full profile data for a single rider by Zwift ID."""
    try:
        fetcher = ZPCyclistFetch()
        cyclists = await fetcher.afetch(zwift_id)
        cyclist = cyclists.get(zwift_id)
        if not cyclist:
            raise HTTPException(status_code=404, detail=f"Rider {zwift_id} not found")
        return cyclist.asdict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/team/{team_id}")
async def get_team(team_id: int):
    """Fetch full team roster including power data for all members."""
    try:
        fetcher = ZPTeamFetch()
        teams = await fetcher.afetch(team_id)
        team = teams.get(team_id)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        return team.asdict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/team/{team_id}/riders")
async def get_team_riders(team_id: int):
    """Fetch the riders list for a team including power profiles."""
    try:
        fetcher = ZPTeamFetch()
        teams = await fetcher.afetch(team_id)
        team = teams.get(team_id)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
        return team.aslist()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
