import uuid
from PIL import Image, ImageTk
import ast
import numpy as np
from datetime import datetime
import cv2
import os
import tkinter as tk


totalElapsedTime = datetime.now()

# ====================== CONFIG ======================
INPUT_IMAGE = "helldiver.png"
INPUT_IMAGES_PATH = "images"
SCALE = 250 # Size of the collection images
RESOLUTION = 3  # Size of each tile
useWebcam = False
openWindowWhenDone = False
# ====================================================

def spliceInputImage(img, res, scale):

    splicedImage = []
    splicedCoords = []

    for y in range(int(img.height/res)):
        for x in range(int(img.width/res)):

            # Crop image and convert and append
            crop_dimensions = (x*res, y*res, x*res+res, y*res+res)
            splicedImage.append(img.crop(crop_dimensions).convert('RGB'))
            splicedCoords.append((x*scale, y*scale))
            
    return splicedImage, splicedCoords

def getNextFrame(cap):
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Warning: Failed to grab frame.")
        return None
    return frame

def videoLoop(frame, root, cap):
    frame = getNextFrame(cap)
    if frame is None:
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    bgImg = Image.fromarray(rgb_frame)

    bgImgCollage = createCollage(bgImg)

    collageBgTk = ImageTk.PhotoImage(image=bgImgCollage)  # Convert to PhotoImage
    

    # If the label already exists, just update the image
    if hasattr(videoLoop, "label"):
        videoLoop.label.configure(image=collageBgTk)
        videoLoop.label.image = collageBgTk  # keep a reference
    else:
        videoLoop.label = tk.Label(root, image=collageBgTk)
        videoLoop.label.pack()
        videoLoop.label.image = collageBgTk  # keep a reference

    root.after(30, videoLoop, frame, root, cap)  # smaller delay for smoother video

def videoFeed(width, height):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    frame = cap.read()

    root = tk.Tk()

    root.title("Collage Video Feed")

    root.geometry(f"{width}x{height}")

    root.resizable(False, False)

    root.after(30, videoLoop, frame, root, cap)

    root.mainloop()

def openWindow(width, height, img):
    # Create the main window (root window)
    root = tk.Tk()

    # Set the window title
    root.title("My Python Window")
    # Set the window dimensions (width x height)
    image = Image.open(savePath)

    root.geometry(f"{image.width}x{image.height}")
    root.resizable(False, False)
    
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(root, image=photo)
    label.pack()

    # Start the Tkinter event loop, which displays the window and handles interactions
    root.mainloop()

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """
    Displays a progress bar in the terminal.
    iteration: current iteration
    total: total iterations
    prefix: prefix string
    suffix: suffix string
    length: character length of the bar
    fill: character used to fill the progress bar
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)

def cacheInputImages():
    cache = []
    counter=0
    for filename in os.listdir(INPUT_IMAGES_PATH):
        if filename.lower().endswith(".png"):
            imgPath = os.path.join(INPUT_IMAGES_PATH, f"picsumImg{counter}.png")
            cache.append(Image.open(imgPath))
            counter+=1
    
    return cache

def computeAvgRGB(img):

    # Convert img to a numpy array
    img_arr = np.array(img)

    # Get average across both axises and all three channels
    average_color = np.mean(img_arr, axis=(0, 1))

    # Assign each channel to the color 
    r, g, b = int(average_color[0]), int(average_color[1]), int(average_color[2])

    return(r, g, b)

def findBestMatch(avg_rgb, all_rgb_vals, tolerance):

    # Convert target RGB tuple to NumPy array
    avg_rgb = np.array(avg_rgb)
    
    # Convert list of RGB tuples to a 2D NumPy array
    all_rgb_vals = np.array(all_rgb_vals)
    
    while True:
        # Compute absolute differences between target and all RGB values
        diff = np.abs(all_rgb_vals - avg_rgb)  # Shape: (num_colors, 3)
        
        # Check if all channels are within the tolerance
        mask = np.all(diff <= tolerance, axis=1)

        if np.any(mask):
            return np.argmax(mask)  # Return the index of the first match
        
        # If no match is found, increase tolerance
        tolerance += 5

def createCollage(img, res = RESOLUTION, scale=SCALE):
    completedNum = 0
    tolerance = 10

    res = abs(res)

    print(f"Res: {res}, Scale: {scale}")

    if(res == 0):
        return "static/images/error.png"

    total = (int(img.height/res) * int(img.width/res))

    multiplyer = scale // res # How much bigger the output image will be compared to original

    print(multiplyer)

    outputWidth = (int(img.width / res) * res) * multiplyer
    outputHeight = (int(img.height / res) * res) * multiplyer

    output_img = Image.new('RGB', (outputWidth, outputHeight))


    splicedImageArr, splicedImageCoordsArr = spliceInputImage(img, res, scale)

    cahcedImages = cacheInputImages()
    

    collageStart = datetime.now()

    for i in range(len(splicedImageArr)):

        # Get its avg rgb
        croppedImageAverageRgbValues = computeAvgRGB(splicedImageArr[i])

        # Search for a best match
        bestMatchIndex = findBestMatch(croppedImageAverageRgbValues, allRgbVals, tolerance)
            
        # Open and resize selected image

        selectedImg = cahcedImages[bestMatchIndex]

        selectedImg = selectedImg.resize( (scale, scale ) )

        # Paste it to the output

        output_img.paste(selectedImg, splicedImageCoordsArr[i])
        
        # Increment how many sections completed
        completedNum+=1

        # Update the progress bar
        progress_bar(completedNum, total, 'Generating:', 'Complete')     

    elapsedSeconds = (datetime.now() - collageStart).total_seconds()

    print(f"\n✅ Time To Generate: {elapsedSeconds:.2f} seconds") 

    return output_img  

def createAndSaveCollage(img, res, scale):
    """ Intended for use with the web app """
    completedNum = 0
    tolerance = 10

    res = abs(res)

    print(f"Res: {res}, Scale: {scale}")

    if(res == 0):
        return "static/images/error.png"

    total = (int(img.height/res) * int(img.width/res))

    multiplyer = scale // res # How much bigger the output image will be compared to original

    print(multiplyer)

    outputWidth = (int(img.width / res) * res) * multiplyer
    outputHeight = (int(img.height / res) * res) * multiplyer

    output_img = Image.new('RGB', (outputWidth, outputHeight))


    splicedImageArr, splicedImageCoordsArr = spliceInputImage(img, res, scale)

    cahcedImages = cacheInputImages()
    

    collageStart = datetime.now()

    for i in range(len(splicedImageArr)):

        # Get its avg rgb
        croppedImageAverageRgbValues = computeAvgRGB(splicedImageArr[i])

        # Search for a best match
        bestMatchIndex = findBestMatch(croppedImageAverageRgbValues, allRgbVals, tolerance)
            
        # Open and resize selected image

        selectedImg = cahcedImages[bestMatchIndex]

        selectedImg = selectedImg.resize( (scale, scale ) )

        # Paste it to the output

        output_img.paste(selectedImg, splicedImageCoordsArr[i])
        
        # Increment how many sections completed
        completedNum+=1

        # Update the progress bar
        progress_bar(completedNum, total, 'Generating:', 'Complete')     

    elapsedSeconds = (datetime.now() - collageStart).total_seconds()

    print(f"\n✅ Time To Generate: {elapsedSeconds:.2f} seconds") 

    try:
        savePath = f"static/processed/{uuid.uuid4().hex}.png"
        output_img.save(savePath)
    except:
        return "static/images/error.png"

    return savePath

# Reading in the txt file generated by the picsum_downloader.py
# Since it is a string we are using a literal evalutaion to get an array of tuples

# The index of a tupel corrisponds to the image with the same number at the end of its file name

with open(f"{INPUT_IMAGES_PATH}/avg_rgb_values.txt", "r") as file:
    allRgbVals = ast.literal_eval(file.readline())

cahcedImages = cacheInputImages()

if __name__ == "__main__":
    inputImg = Image.open(INPUT_IMAGE)

    if useWebcam:
        total = (int(inputImg.height/RESOLUTION) * int(inputImg.width/RESOLUTION)) // 3
    else:
        total = (int(inputImg.height/RESOLUTION) * int(inputImg.width/RESOLUTION))

    if(useWebcam):
        videoFeed(640, 480)
    else:

        npImage = np.array(createCollage(inputImg))

        finalImg = cv2.cvtColor(npImage, cv2.COLOR_RGB2BGR)

        savePath = f"{INPUT_IMAGE.strip('.png')}-collage.png"

        cv2.imwrite(savePath, finalImg)

        #if openWindowWhenDone:
        #    openWindow(finalImg.width, finalImg.height, finalImg)

        elapsedSeconds = (datetime.now() - totalElapsedTime).total_seconds()
        print(f"\n✅ Total Elapsed Time: {elapsedSeconds:.2f} seconds") 

