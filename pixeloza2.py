#!/bin/python3

""" This is the main version, which gets a random image (based on keywords
supplied as commandline arguments) and pixelizes it using simple half-blocks ▀.

--web, --file, --wide options as in pixeloza1.py
"""

import os, sys, random, requests
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError

def display(image_stream, eff_width, eff_height, wideQ):
    image = Image.open(image_stream)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    width, height = image.size

    # Calculate scaling factors to fit the image within the terminal
    x_scale = width / eff_width
    y_scale = height / eff_height
    scale = x_scale if wideQ else max(x_scale,y_scale)
    width, height = round(width/scale), round(height/scale)
    image = image.resize((width,height))

    # Process each block of pixels and display color in terminal
    for y in range(0, height, 2):
        odd = True if (y1:=y+1) == height else False
        for x in range(0, width, 1):
            r1, g1, b1 = image.getpixel((x, y))
            r2, g2, b2 = (0,0,0) if odd else image.getpixel((x, y1 ))
            # Convert RGB values to ANSI color codes
            ansi_color = f"\033[38;2;{r1};{g1};{b1}m" + f"\033[48;2;{r2};{g2};{b2}m"
            print(f"{ansi_color}\u2580", end='') # ▀
        print("\033[0m")  # Reset colors and Move to the next row

def obtain(quer):
    url = "https://www.google.com/search"
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    params = {
        "q": quer,
        "udm": 2,
        "safe": "off",
        "sclient": "img",
        "start": random.choice([1,10,20,30,40,50]) }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        img_elements = soup.find_all("img")
        img_urls = [img["src"] for img in img_elements if "src" in img.attrs and not img["src"].startswith('/images/branding')]
        if len(img_urls) > 0:
            return random.choice( img_urls )
    print("Failed to fetch search results - please try again!")
    exit(1)

def main(opt=[]):
    # Terminal dimensions
    terminal_size = os.get_terminal_size()
    eff_width = terminal_size.columns-1
    eff_height = 2*(terminal_size.lines-1)
    
    wideQ = True if '--wide' in opt else False
    opt = [o for o in opt if o != '--wide' ]

    if len(opt) == 2 and opt[0] == '--file':
        display( opt[1], eff_width, eff_height, wideQ )
        return

    try:
        if len(opt)==2 and opt[0] == "--web":
            image_url = opt[1]
        else:
            image_url = obtain( ' '.join(opt) ) if opt else obtain("frog")
        response = requests.get(image_url)
        if response.status_code!=200:
            print(image_url)
            print("Couldn't fetch image - please try again!")
            exit(1)
        display( BytesIO(response.content), eff_width, eff_height, wideQ )
    except Exception as e:
        print(type(e).__name__, '\n', e)
        print(image_url)
        print("Unacceptable image or url - please try again!")

if __name__ == "__main__":
    main( sys.argv[1:] )
