#!/usr/bin/python3

""" This is the retro version, which gets a random image (based on keywords
supplied as commandline arguments) and pixelizes it using simple half-blocks ▀,
as 1/0 monochrome pixels."""

help_text = """
basic usage:
[python] pixeloza1.py keyword1 keyword2 ...

    displays a random image from the net, found by keywords
    (including unrecognized options)

options:
--file PATH     to use a local file (overrides --web)
--web URL       to use an image from the web

--wide          to use all console/terminal colums
--inv           to invert black/white (console/txt file visibility)
--show_full     to also show the image (in default image viewer) dithered in full resolution
"""

import os, sys 
import requests
import numpy
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from numba import njit
except ImportError:
    print("Couldn't import numba, proceeding without JIT")
    def njit(*args, **kwargs):
        if type(args[0]).__name__ == 'function':
            return args[0]
        else:
            return lambda q: q
@njit
def Atkinson(B):
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = (C[y,x]-255)/8, 255
            else:
                err, B[y,x] = C[y,x]/8, 0
            q = 0
            C[y,x+1] += err
            C[y,x+2] += (1+q)*err
            C[y+1,x-1] += err # works because x=0 goes to C[:,-1], which is never used
            C[y+1,x] += err
            C[y+1,x+1] += err
            C[y+2,x] += (1-q)*err
@njit
def AtkinsonRand(B):
    # randomly nudge the weights of the furthest pixels - helps prevent
    # artifact lines
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = (C[y,x]-255)/8, 255
                #ER[y,x,0] = (C[y,x] - ER[y,x,1])
            else:
                err, B[y,x] = C[y,x]/8, 0
            q = (numpy.random.randint(3)-1)/2 
            C[y,x+1] += err
            C[y,x+2] += (1+q)*err
            C[y+1,x-1] += err # works because x=0 goes to C[:,-1], which is never used
            C[y+1,x] += err
            C[y+1,x+1] += err
            C[y+2,x] += (1-q)*err
@njit
def FloydSteinberg(B):
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = (C[y,x]-255)/16, 255
            else:
                err, B[y,x] = C[y,x]/16, 0
            C[y,x+1] += err*7
            C[y+1,x-1] += err*3
            C[y+1,x] += err*5
            C[y+1,x+1] += err*1
@njit
def JarvisJudisNinke(B):
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = (C[y,x]-255)/48, 255
            else:
                err, B[y,x] = C[y,x]/48, 0
            C[y,x+1] += err*7
            C[y,x+2] += err*5
            C[y+1,x-2] += err*3
            C[y+1,x-1] += err*5
            C[y+1,x] += err*7
            C[y+1,x+1] += err*5
            C[y+1,x+2] += err*3
            C[y+2,x-2] += err
            C[y+2,x-1] += err*3
            C[y+2,x] += err*5
            C[y+2,x+1] += err*3
            C[y+2,x+2] += err
@njit
def FSAtkinson(B):
    # Mixed Atkinson + Floyd-Steinberg
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = C[y,x]-255, 255
            else:
                err, B[y,x] = C[y,x], 0
            C[y,x+1] += 0.28125*err # 7/16 + 1/8 -> 9/32
            C[y,x+2] += 0.0625*err # 0 + 1/8 -> 1/16
            C[y+1,x-1] += 0.15625*err # 3/16 + 1/8 -> 5/32
            C[y+1,x] += 0.21875*err #  5/16 + 1/8 -> 7/32
            C[y+1,x+1] += 0.09375*err #  1/16 + 1/8 -> 3/32
            C[y+2,x] += 0.0625*err #  0 + 1/8 -> 1/16
@njit
def FSAtkinsonRand(B):
    # FS + AtkinsonRand
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = C[y,x]-255, 255
            else:
                err, B[y,x] = C[y,x], 0
            q = (numpy.random.randint(3)-1)
            C[y,x+1] += 0.28125*err        # 7/16 + 1/8 -> 9/32
            C[y,x+2] += 0.0625*(1+q)*err   # 0 + (1+q)/8 -> (1+q)/16
            C[y+1,x-1] += 0.15625*err      # 3/16 + 1/8 -> 5/32
            C[y+1,x] += 0.21875*err        #  5/16 + 1/8 -> 7/32
            C[y+1,x+1] += 0.09375*err      #  1/16 + 1/8 -> 3/32
            C[y+2,x] += 0.0625*(1-q)*err   #  0 + (1-q)/8 -> (1-q)/16
@njit
def Hybrid(B):
    # Atkinson mixed with JJN
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = (C[y,x]-255)/48, 255
            else:
                err, B[y,x] = C[y,x]/48, 0
            C[y,x+1] += err*6.5
            C[y,x+2] += err*5.5
            C[y+1,x-2] += err*1.5
            C[y+1,x-1] += err*5.5
            C[y+1,x] += err*6.5
            C[y+1,x+1] += err*5.5
            C[y+1,x+2] += err*1.5
            C[y+2,x-2] += err*0.5
            C[y+2,x-1] += err*1.5
            C[y+2,x] += err*5.5
            C[y+2,x+1] += err*1.5
            C[y+2,x+2] += err*0.5

def display(image_stream, eff_width, eff_height, scale_mode, invQ, fullQ):
    image = Image.open(image_stream)
    width, height = image.size
    # full res dither
    if fullQ:
        Bx = numpy.array(image.convert('L'))
        FSAtkinson(Bx)
        #AtkinsonRand(Bx)
        Image.fromarray(Bx).show()
    # Calculate scaling factors to fit the image within the terminal
    x_scale = width / eff_width
    y_scale = height / eff_height
    scale = x_scale if scale_mode=='x' else max(x_scale,y_scale)
    width, height = round(width/scale), round(height/scale)
    print(width,height)
    if invQ:
        image = ImageOps.invert(image)
    image = image.resize((width,height))
    #image = image.convert('1') # this would be PIL's built-in dither
    image = image.convert('L')
    B = numpy.array(image) # this is Boolean for 1, but 8-bit for L
    FSAtkinson(B)

    # Process each block of pixels and display in terminal
    for y in range(0, height, 2):
        line = ""
        odd = True if (y1:=y+1) == height else False
        for x in range(0, width, 1):
            v1 = B[y,x]
            v2 = 0 if odd else B[y1,x]
            if v1: #==255:
                if v2: #==255:
                    line += "\u2588" # print("\u2588", end='') # █
                else:
                    line += "\u2580" # print("\u2580", end='') # ▀
            elif v2: #==255:
                line += "\u2584" # print("\u2584", end='') # ▄
            else:
                line += " " # print(" ", end='') # 
        print(line) #print("\033[0m")  # Reset colors and Move to the next row

def obtain(quer):
    url = "https://www.google.com/search"
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    params = {
        "q": quer,
        "udm": 2,
        "safe": "off",
        "sclient": "img",
        "start": numpy.random.choice([1,10,20,30,40,50]) }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        img_elements = soup.find_all("img")
        img_urls = [img["src"] for img in img_elements if "src" in img.attrs and not img["src"].startswith('/images/branding')]
        if len(img_urls) > 0:
            return numpy.random.choice( img_urls )
    print("Failed to fetch search results - please try again!")
    exit(1)

def parse_opts(opts):
    o = {'scale': None, 'query': 'frog', 'inv': False, 'full': False}
    keywords = []
    i = 0
    while i < len(opts):
        if opts[i] == '--wide':
            o['scale'] = 'x'
            i += 1
        elif opts[i] == '--inv':
            o['inv'] = True
            i += 1
        elif opts[i] == '--web':
            o['web'] = opts[i+1]
            i += 2
        elif opts[i] == '--file':
            o['file'] = opts[i+1]
            i += 2
        elif opts[i] == '--show_full':
            o['full'] = True
            i += 1
        else:
            keywords.append( opts[i] )
            i += 1
    if len(keywords) > 0:
        if any( q.startswith('--') for q in keywords ):
            print('Suspicious keywords found:', *[repr(k) for k in keywords if k.startswith('--')])
            print('Were those meant as options? Use --help to list them.')
        o['query'] = ' '.join(keywords)
    return o
def main(opts=[]):
    if '--help' in opts:
        print(help_text)
        return

    # Terminal dimensions
    terminal_size = os.get_terminal_size()
    eff_width = terminal_size.columns-1
    eff_height = 2*(terminal_size.lines-1)
    
    opt = parse_opts(opts)

    if 'file' in opt:
        display( opt['file'], eff_width, eff_height, opt['scale'], opt['inv'], opt['full'] )
        return

    try:
        if 'web' in opt:
            image_url = opt['web']
        else:
            image_url = obtain( opt['query'] )
        response = requests.get(image_url)
        if response.status_code!=200:
            print(image_url, "\nCouldn't fetch image - please try again!")
            sys.exit(1)
        display( BytesIO(response.content), eff_width, eff_height, opt['scale'], opt['inv'], opt['full'])
    except Exception as e:
        print(type(e).__name__, '\n', e)
        print(image_url, "\nUnacceptable image or url - please try again!")
        sys.exit(1)

if __name__ == "__main__":
    main( sys.argv[1:] )
    sys.exit(0)
