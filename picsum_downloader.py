from PIL import Image
import urllib.request
import numpy as np

number_of_images = 10
photo_resolution = 50


avgRgbValsOfAllImages = []


url = f"https://picsum.photos/{photo_resolution}"

for i in range(0,number_of_images):

    urllib.request.urlretrieve(url, f"images/picsumImg{i}.png")

    img = Image.open(f"images/picsumImg{i}.png")
    #img.show()

    with Image.open(f"images/picsumImg{i}.png") as img:
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

with open("images/avg_rgb_values.txt", "w") as file:
    file.write(f"{avgRgbValsOfAllImages}")
