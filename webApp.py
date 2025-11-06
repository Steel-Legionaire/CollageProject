from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
from fastapi.concurrency import run_in_threadpool

import io
import os
import uuid

import collageGenerator

# Create FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Point FastAPI to your templates directory
templates = Jinja2Templates(directory="templates")

# Define a simple route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello, World!"})

@app.post("/", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...), resolution: int = Form(...)):

    contents = await file.read()

    image = Image.open(io.BytesIO(contents)).convert("RGB")

    filename = f"{uuid.uuid4().hex}.png"
    save_path = os.path.join("static", "processed", filename)
    image.save(save_path)

    # Send to backend to create collage
    collageGenerator.inputImg = image
    result_path = await run_in_threadpool(collageGenerator.createAndSaveCollage, image, resolution)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "uploaded_image": f"{save_path}",
            "processed_image": result_path,
        },
    )