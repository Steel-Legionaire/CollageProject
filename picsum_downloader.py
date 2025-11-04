from PIL import Image
import urllib.request
import numpy as np

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
    print ("\033[A \033[A")
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end="")



number_of_images = 1000
photo_resolution = 50

startingIndex = 0

avgRgbValsOfAllImages = []

outputPath = "testImages"

url = f"https://picsum.photos/{photo_resolution}"

for startingIndex in range(0,number_of_images):

    urllib.request.urlretrieve(url, f"{outputPath}/picsumImg{startingIndex}.png")

    img = Image.open(f"{outputPath}/picsumImg{startingIndex}.png")
    progress_bar(startingIndex+1, number_of_images, prefix='Downloading:',suffix='Complete',length=40)
    #print(f"{startingIndex+1}/{number_of_images}")

    #img.show()

    with Image.open(f"{outputPath}/picsumImg{startingIndex}.png") as img:
        img = img.convert('RGB')

        # Retrieve the width and height of the image.
        width, height = img.size

        # Initialize a list to store RGB values.
        rgb_values = []

        # Use a list comprehension to populate the list with RGB values of each pixel.
        rgb_values = [img.getpixel((x, y)) for y in range(height) for x in range(width)]

    averageRgbValues = (0, 0, 0)
    totalRgbValues = (0, 0, 0)

    counter = 0

    for val in rgb_values:
        totalRgbValues = (totalRgbValues[0] + val[0], totalRgbValues[1] + val[1], totalRgbValues[2] + val[2])

        counter+=1

    averageRgbValues = (int(totalRgbValues[0] / counter), int(totalRgbValues[1] / counter), int(totalRgbValues[2] / counter))

    avgRgbValsOfAllImages.append(averageRgbValues)

    #print(avgRgbValsOfAllImages)

with open(f"{outputPath}/avg_rgb_values.txt", "w") as file:
    file.write(f"{avgRgbValsOfAllImages}")

print("\n")