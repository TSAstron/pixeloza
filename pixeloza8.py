#!/bin/python3

""" This is the improved dithring version, which gets a random image (based on
keywords supplied as commandline arguments) and pixelizes it using the custom
bitmap font (currently: Random...bdf) that contains 2x4 square blocks."""

help_text = """
usage:
[python] pixeloza8.py keyword1 keyword2 ...

    displays a random image from the net, found by keywords
    (including unrecognized options)

options:
--file PATH     to use local file
--web URL       to use an image from the web

--wide          to use all console/terminal colums
--inv           to invert black/white (console/txt file visibility)
--show_full     to also show the image (in default image viewer) dithered in full resolution
"""

import os, sys, requests
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
            C[y,x+1] += err
            C[y,x+2] += err
            C[y+1,x-1] += err # works because x=0 goes to C[:,-1], which is never used
            C[y+1,x] += err
            C[y+1,x+1] += err
            C[y+2,x] += err

@njit
def AtkinsonRand(B):
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    #print( (C[0:8,:] - 255*(C[0:8,:]/255).round()).mean(axis=1) )
    #mu = C[0,:].mean()
    #print('munu', mu, si)
    eta = 1 # scaling for random dir switching ∈ [0,1]
    # random setup for Linear Congruential Generator
    Xn = 2718
    m = 1 << 32 # 1 << 64
    a = 1664525 # (6364136223846793005)
    c = 1013904223 # 1
    for y in range(B.shape[0]):
        if y < 8:
            """
            print( 'mean err:', (C[y,:] - 255*(C[y,:]>=128).astype(C.dtype)).mean(),
                  'mean+2:', C[y+2,:].mean() )
                  """
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = (C[y,x]-255)/8, 255
            else:
                err, B[y,x] = C[y,x]/8, 0
            # slight random weight change (keeping the sum) at the furthest points
            # changes direction -> gets rid of artifact streaks (line/diag)
            # R is in [-1,0,1], take 1/2 for ordinary Atkinson
            Xn = (a*Xn + 1) % m
            q = eta*((Xn%3)-1)
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
    # FS + AtkinsonRand using LCG for reproducible random
    C = numpy.zeros((B.shape[0]+2,B.shape[1]+2), dtype=float)
    C[:-2,:-2] = B
    #random setup
    Xn = (2718)
    m = 1 << 32 # 1 << 64 # if only we had long long...
    a = 1664525 # 6364136223846793005
    c = 1013904223 # 1?
    for y in range(B.shape[0]):
        for x in range(B.shape[1]):
            if C[y,x] >= 128:
                err, B[y,x] = C[y,x]-255, 255
            else:
                err, B[y,x] = C[y,x], 0
            Xn = (a*Xn + c) % m
            q = (Xn%3)-1 # [-1,0,1]
            #q = R[y,x]
            C[y,x+1] += 0.28125*err # 7/16 + 1/8 -> 9/32
            C[y,x+2] += 0.0625*(1+q)*err # 0 + (1+q)/8 -> (1+q)/16
            C[y+1,x-1] += 0.15625*err # 3/16 + 1/8 -> 5/32
            C[y+1,x] += 0.21875*err #  5/16 + 1/8 -> 7/32
            C[y+1,x+1] += 0.09375*err #  1/16 + 1/8 -> 3/32
            C[y+2,x] += 0.0625*(1-q)*err #  0 + (1-q)/8 -> (1-q)/16
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
    if invQ:
        image = ImageOps.invert(image)
    #algo = Atkinson
    #algo = FloydSteinberg
    #algo = JarvisJudisNinke
    algo = FSAtkinson # seems FSA is better than Hybrid...
    #algo = FSAtkinsonRand
    #algo = AtkinsonRand
    if fullQ: # full res dither
        Bx = numpy.array(image.convert('L'))
        algo(Bx)
        Image.fromarray(Bx).show()

    # Calculate scaling factors to fit the image within the terminal grid
    x_scale = width / eff_width
    y_scale = height / eff_height
    scale = x_scale if scale_mode=='x' else max(x_scale, y_scale)
    width, height = round(width/scale), round(height/scale)
    print("rescaled size", width, height, ", overhangs", over_w := width%2, over_h := height%4)
    # the first padding reflects placing the image inside the terminal dictated
    # grid, while keeping the aspect ratio
    height_p = height + (4 - over_h) if over_h else height # padded array
    width_p = width + (2 - over_w) if over_w else width # padded array
    # the second padding duplicates first rows/columns so that the diffused noise
    # reaches "stable" values on the actual first row
    B = numpy.zeros( (height_p + 2, width_p + 2), dtype='uint8')

    image = image.resize((width,height)) # here is where PIL adds artifacts at the borders!
    image = image.convert('L')
    # copy into bottom left corner: top row scrolls up, right col might have scrollbar
    B[-height:,2:2+width] = image
    B[-height-2:-height,2:] = B[-height:-height+1,2:]
    B[:,0:2] = B[:,2:2+1]
    algo(B[-height-2:,:]) #[-height:,:width]) # full B doesn't loose all diff err at right border
    # noise used, but the (1st) padding pixels are fake, so blacken
    B[:,2+width:] = 0 
    # second padding copied the 1st line, so blacken
    B[-height-2:-height] = 0

    height_b, width_b = B[2:,2:].shape
    D = B[2:,2:].reshape((height_b//4,4,width_b)).reshape((height_b//4,4,width_b//2,2))
    D = D.transpose((0,2,1,3)).reshape((height_b//4, (width_b//2)*8)) # packbits can deal with all blocks unfolded into the last axis
    DD = numpy.packbits(D, axis=1, bitorder='big') # big-endian Because that's the font!

    # Process each 8x2 pixel matrx packed as uint16, and display in terminal
    line = ""
    for y in DD:
        for x in y:
            line += chr(0xEE00+x) # astype necessary???
        line += '\n'
    print(line[:-1])

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
        elif opts[i] == '--rect':
            print('--rect does nothing in dithering and will be ignored')
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
    terminal_size = os.get_terminal_size(sys.__stdin__.fileno())
    eff_width = 2*terminal_size.columns
    eff_height = 4*(terminal_size.lines-1) # save 1 for sys prompt
    
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
        print(image_url)
        print("Unacceptable image or url - please try again!")
        raise e

if __name__ == "__main__":
    main( sys.argv[1:] )
