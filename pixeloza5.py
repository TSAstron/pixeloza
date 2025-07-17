#!/usr/bin/python3

""" This has 3*2 sub-blocks. It gets a random image (based on keywords
supplied as commandline arguments), or reads a file with --file option,
or gets it from the internet with --web option,
then pixelizes it using the whole pandemonium of characters from masks.py
(unless --rect is used, which has pure 1/4 and 1/6 rectangles)
use --wide for the image to use all columns (preserving aspect), other
"options" are treated as search keywords.
"""

import os, sys
import numpy
from PIL import Image, UnidentifiedImageError
from masks import *

# FULL char/mask set
MASKS, CHARS, SHAPES = compose((SET1, SET2, SET3, SET4, SET5))
SHAPE_LENS = [ MASKS[q].sum() for q in SHAPES ]

# pixels in the full block: 4*3 per sub-block 3*2 sub-blocks per block (display character)
L0 = 12*6

def choose_shape( block ):
    A = numpy.array(block, dtype=float)
    #S_f = (A*A).sum() # needed if actual error is required
    I, TE = 0, 0 # 255*255*L0, without the common term err < 0
    M1, M2 = numpy.zeros(3,dtype='float64'), numpy.zeros(3,dtype='float64')
    block_sums = numpy.einsum('ijk,jkl->il', MASKS, A)
    sum0 = A.sum(axis=(0,1))
    for i, shape in enumerate(SHAPES):
        sum_f = numpy.zeros(3,dtype='float64')
        for m in shape:
            sum_f += block_sums[m]
        sum_b = sum0 - sum_f
        L_f = SHAPE_LENS[i] # "volume" of shape, L0-L-f for the complement
        mean_f, mean_b = sum_f/L_f, sum_b/(L0-L_f)
        tot_err = -sum_f@mean_f -sum_b@mean_b
        if tot_err < TE:
            I, M1, M2, TE = i, numpy.round(mean_f), numpy.round(mean_b), tot_err
    r1, g1, b1 = M1.astype('int')
    r2, g2, b2 = M2.astype('int')
    ansi_color = f"\033[38;2;{r1};{g1};{b1}m" + f"\033[48;2;{r2};{g2};{b2}m"
    return f"{ansi_color}{CHARS[I]}"

def display(image_stream, term_width, term_height, scale_mode=None):
    image = Image.open(image_stream)
    if image.mode != 'RGB': # '1' for 0/1, 'L' for greyscale
        image = image.convert('RGB')
    width, height = image.size
    print("original size", width, height)

    # Calculate scaling factors to fit the image within the terminal grid
    # which is 6 times as wide, and 12 times as high as the number of full blocks
    # assuming 2:1 character ratio. The block then has 6 sub-blocks,
    # which are 4x3 pixels
    grid_width, grid_height = 6*term_width, 12*term_height
    x_scale = width / grid_width
    y_scale = height / grid_height
    scale = x_scale if scale_mode=='x' else max(x_scale,y_scale)
    width, height = round(width/scale), round(height/scale)
    print("rescaled size", width, height )
    # overhangs are cut/copied to avoid averaging with the black padding
    # this the basic 6x12 grid has 2 sub-columns and 3 sub-rows,
    # so 6/2 -> mod 3, 12/3 -> mod 4 (see also pixeloza4)
    width = width if width%3==0 else width+3-(width%3)
    height = height if height%4==0 else height+4-(height%4)
    image = image.resize( (width,height) )

    width = width if width%6==0 else width+6-(width%6)
    height = height if height%12==0 else height+12-(height%12)
    new_image = Image.new("RGB", (width, height), 0)
    new_image.paste(image, (0,0))
    image = new_image

    # Process each block of pixels and display color in terminal
    for y in range(0, height, 12):
        msg = "" # f"{y//12:3d}"
        for x in range(0, width, 6):
            msg += choose_shape( image.crop((x,y,x+6,y+12)) )
        print(msg+"\033[0m")  # Reset colors and Move to the next row

def obtain(quer):
    import random
    eng = random.choice(["goo","bin"])
    if eng == 'bin':
        url = "https://bing.com/images/search"
        params = { "q": quer, "safesearch": "off", "first": random.choice([1,10,20,30,40,50]) }
    else:
        url = "https://www.google.com/search"
        params = { "q": quer, "udm": 2, "safe": "off", "start": random.choice([1,10,20,30,40,50]) }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        img_elements = soup.find_all("img")
        if eng=='bin':
            img_urls = [img["data-src"] for img in img_elements if "data-src" in img.attrs]
        else:
            img_urls = [img["src"] for img in img_elements if "src" in img.attrs and not img['src'].startswith('/images/branding')]
        if len(img_urls) > 0:
            return random.choice( img_urls )
    print("Failed to fetch search results - please try again!")
    exit(1)

def parse_opts(opts):
    o = {'scale': None, 'query': 'frog'}
    keywords = []
    i = 0
    while i < len(opts):
        if opts[i] == '--wide':
            o['scale'] = 'x'
            i += 1
        elif opts[i] == '--web':
            o['web'] = opts[i+1]
            i += 2
        elif opts[i] == '--file':
            o['file'] = opts[i+1]
            i += 2
        elif opts[i] == '--rect': # recalculating, a bit unoptimized
            global MASKS, CHARS, SHAPES, SHAPE_LENS
            MASKS, CHARS, SHAPES = compose((SET3, SET4))
            SHAPE_LENS = [ MASKS[q].sum() for q in SHAPES ]
            i += 1
        else:
            keywords.append( opts[i] )
            i += 1
    if len(keywords) > 0:
        o['query'] = ' '.join(keywords)
    return o

def main(opts=[]):
    opt = parse_opts(opts)

    # Terminal dimensions
    terminal_size = os.get_terminal_size()
    eff_width = terminal_size.columns-1
    eff_height = terminal_size.lines-1
    print("Terminal size", eff_width, eff_height)

    if 'file' in opt:
        display( opt['file'], eff_width, eff_height, opt['scale'] )
        exit(0)
    
    try:
        global requests
        import requests
        from io import BytesIO
        if 'web' in opt:
            image_url = opt['web']
        else:
            image_url = obtain(opt['query'])
        response = requests.get(image_url)
        if response.status_code!=200:
            print(image_url,"Couldn't fetch image - please try again!", sep='\n')
            exit(1)
        display( BytesIO(response.content), eff_width, eff_height, opt['scale'] )
    except Exception as e:
        print(type(e).__name__, '\n', e)
        print(image_url)
        print("Unacceptable image or url - please try again!")
        raise e

if __name__ == "__main__":
    main( sys.argv[1:] )
