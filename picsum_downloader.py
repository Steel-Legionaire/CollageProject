from PIL import Image
import urllib.request


number_of_images = 5

photo_resolution = 50

url = f"https://picsum.photos/{50}"

for i in range(0,number_of_images):

    urllib.request.urlretrieve(url, f"picsumImg{i}.png")

    img = Image.open(f"picsumImg{i}.png")
    #img.show()