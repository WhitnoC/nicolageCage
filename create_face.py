
import os
from random import sample
import sys
import requests
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from PIL import GifImagePlugin
import urllib
from colorthief import ColorThief
from math import sqrt


def closest_color(rgb, sample_images):
    r, g, b = rgb
    color_diffs = []
    for image, color in sample_images:
        cr, cg, cb = color
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))

    return min(color_diffs)[1]


def find_common_colour(sample_image, bbox, palette_size=16):
    """
    from a given bounding box of space sampled from target image, 
    find the most common colour present in that particular portion of the image
    """

    #print(bbox)
    img = sample_image.crop((bbox))
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    print(dominant_color)

    return dominant_color


def scrape_images():

    images = []

    #TODO: This is gross, fix lol

    urls = ["https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:red&client=firefox-b-d&sa=X&ved=0CAQQ2J8EahcKEwjA0Myw9cD6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:orange&client=firefox-b-d&sa=X&ved=0CAUQ2J8EahcKEwjgtIqS9sD6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:yellow&client=firefox-b-d&sa=X&ved=0CAYQ2J8EahcKEwig7f2W9sD6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:green&client=firefox-b-d&sa=X&ved=0CAcQ2J8EahcKEwjYpaOE98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:teal&client=firefox-b-d&sa=X&ved=0CAgQ2J8EahcKEwiQw4mM98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:purple&client=firefox-b-d&sa=X&ved=0CAoQ2J8EahcKEwjwifaw98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:pink&client=firefox-b-d&sa=X&ved=0CAsQ2J8EahcKEwjojYjC98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:white&client=firefox-b-d&sa=X&ved=0CAwQ2J8EahcKEwjgp5DG98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:black&client=firefox-b-d&sa=X&ved=0CA4Q2J8EahcKEwiYjI_M98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083",
    "https://www.google.com/search?q=nicolas%20cage&tbm=isch&hl=en&tbs=ic:specific%2Cisc:brown&client=firefox-b-d&sa=X&ved=0CA8Q2J8EahcKEwiY4OfP98D6AhUAAAAAHQAAAAAQAg&biw=2159&bih=1083"]


    #url = "https://www.google.com.au/search"
    i = 0
    for url in urls:
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')

        image_tags = soup.find_all('img')
        links = []
        for image_tag in image_tags:
            links.append(image_tag['src'])

        print([link for link in links])

        for link in links:
            # exclude any src that starts with images/branding to avoid google branded content
            if not link.startswith("/images/branding"):
                urllib.request.urlretrieve(link, f"{image_path}/{i}.png")

                # open image in pillow and then append to a list
                img = Image.open(f"{image_path}/{i}.png")
                images.append(img)

                i+= 1

    return images
 
def find_colours(images):

    """
    for the scraped images, find the most dominant colour and then append to a tuple list
    """

    processed_images = []
    for image in images:
        colour = find_common_colour(image, (0,0, image.width, image.height))
        processed_images.append((image, colour))

    return processed_images


# variables to tweak before running script
sample_image = Image.open(os.path.join(os.getcwd(), "sample.gif"))
# path of images that will be used in collage
image_path = os.path.join(os.getcwd(), "nicholas_cage_pictures") 
scrape = False # choose whether or not to scrape images from google

# size of bounding box to sample for given images
pixel_size_x, pixel_size_y = (10,10) 

if not os.path.exists(image_path):
    os.makedirs(image_path)

# Retrieve frames from sample image and append them to a gif
sample_nicholas_frames = []
for frame in range(0, sample_image.n_frames):
    sample_image.seek(frame)
    sample_nicholas_frames.append(sample_image)


# scrape images from google
if scrape is True:
    images = scrape_images()

images = []
# find all images from target directory and open them in pillow
for file in os.listdir(image_path):
    opened_img = Image.open(os.path.join(image_path, file))
    images.append(opened_img)

#find all dominant colours for images and then append to tupled list:
processed_images = find_colours(images)

new_frames = []
for img in sample_nicholas_frames:

    source = img
    width, height = source.size
    squares = (width // pixel_size_x, height // pixel_size_y)
    rows, collumns = squares[0], squares[1]

    prev_x, prev_y = 0, 0
    # create a blank canvas to use, that is the same resolution as the image used
    canvas = Image.new("RGB", (width, height), (0,0,0))

    for collumn in range(collumns):
        for row in range(rows):
            
            x, y = (pixel_size_x * (row+1)), (pixel_size_y * (collumn+1))
            bbox = (prev_x, prev_y, x, y)

            dominant_colour = find_common_colour(sample_image=img, bbox=bbox)

            # find most closest matching image to colour described:
            close_color = closest_color(dominant_colour, processed_images)
            for image, color in processed_images:
                if close_color == color:

                    image.thumbnail((pixel_size_x, pixel_size_y))
                    image = image.convert("RGB")
                    canvas.paste(image, (prev_x, prev_y))

                    break

            prev_x = x

        prev_x = 0 
        prev_y = y

    new_frames.append(canvas)


new_frames[0].save(f"result.gif", format="gif", save_all=True, append_images=new_frames[1:], duration=1, loop=0)