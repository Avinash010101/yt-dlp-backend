from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests

app = FastAPI()

# Enable CORS for your frontend
origins = ["https://trimic.in"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch video info
@app.get("/info")
def get_info(url: str):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": [
                {
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "resolution": f.get("resolution") or f.get("height"),
                    "url": f["url"]
                }
                for f in info["formats"]
            ]
        }
    except Exception as e:
        return JSONResponse({"error": str(e)})

# Stream download
@app.get("/download")
def download(url: str, format_id: str):
    ydl_opts = {"quiet": True, "format": format_id}

    def generate():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=False)
            video_url = result["url"]
            with requests.get(video_url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        yield chunk

    return StreamingResponse(generate(), media_type="video/mp4")
