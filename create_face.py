from concurrent.futures import process
from ctypes import resize
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

    url = "https://www.google.com.au/search?q=nicholas+cage&hl=en&authuser=0&tbm=isch&sxsrf=ALiCzsabPB2SqxnuojRckEReLevgFJSEvQ%3A1664624939763&source=hp&biw=2176&bih=1100&ei=Kyk4Y9DuK7zF4-EPrMGo4Ak&iflsig=AJiK0e8AAAAAYzg3O2parGsNUGtq6K3DxEc-lNQxEo1-&ved=0ahUKEwiQsN2R-776AhW84jgGHawgCpwQ4dUDCAY&uact=5&oq=nicholas+cage&gs_lcp=CgNpbWcQAzIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQ6CAgAEIAEELEDOgsIABCABBCxAxCDAToICAAQsQMQgwE6BAgAEANQ5gRYyRVgtxZoAnAAeACAAcsBiAH6EJIBBjAuMTEuMpgBAKABAaoBC2d3cy13aXotaW1nsAEA&sclient=img"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')

    image_tags = soup.find_all('img')
    links = []
    for image_tag in image_tags:
        links.append(image_tag['src'])

    print([link for link in links])

    for i, link in enumerate(links):
        # exclude any src that starts with images/branding to avoid google branded content
        if not link.startswith("/images/branding"):
            urllib.request.urlretrieve(link, f"{image_path}/{i}.png")

            # open image in pillow and then append to a list
            img = Image.open(f"{image_path}/{i}.png")
            images.append(img)

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

# just do one nicholas cage picture for now
source = sample_nicholas_frames[0]
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

        dominant_colour = find_common_colour(sample_image=source, bbox=bbox)

        # find most closest matching image to colour described:
        close_color = closest_color(dominant_colour, processed_images)
        for image, color in processed_images:
            if close_color == color:
                print("color found")

                image.thumbnail((pixel_size_x, pixel_size_y))
                image = image.convert("RGB")
                canvas.paste(image, (prev_x, prev_y))

                break

        prev_x = x

    prev_x = 0
    prev_y = y

sample_image.show()
canvas.show()