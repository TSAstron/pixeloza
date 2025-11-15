#!/bin/python3

""" This is the improved dithring version, which gets a random image (based on
keywords supplied as commandline arguments) and ixelizes it using extended
hextet blocks 🬀, as 1/0 monochrome pixels."""

help_text = """
basic usage:
[python] pixeloza3.py keyword1 keyword2 ...

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
import time, numpy
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

C_TREE = { # binary rep of characters (row-order)
        (0,0,0,0,0,0): ' ',
        (1,0,0,0,0,0): '\U0001FB00', # 🬀
        (0,1,0,0,0,0): '\U0001FB01', # 🬁
        (1,1,0,0,0,0): '\U0001FB02', # 🬂
        (0,0,1,0,0,0): '\U0001FB03', # 🬃
        (1,0,1,0,0,0): '\U0001FB04', # 🬄
        (0,1,1,0,0,0): '\U0001FB05', # 🬅
        (1,1,1,0,0,0): '\U0001FB06', # 🬆
        (0,0,0,1,0,0): '\U0001FB07', # 🬇
        (1,0,0,1,0,0): '\U0001FB08', # 🬈
        (0,1,0,1,0,0): '\U0001FB09', # 🬉
        (1,1,0,1,0,0): '\U0001FB0A', # 🬊
        (0,0,1,1,0,0): '\U0001FB0B', # 🬋
        (1,0,1,1,0,0): '\U0001FB0C', # 🬌
        (0,1,1,1,0,0): '\U0001FB0D', # 🬍
        (1,1,1,1,0,0): '\U0001FB0E', # 🬎

        (0,0,0,0,1,0): '\U0001FB0F', # 🬏
        (1,0,0,0,1,0): '\U0001FB10', # 🬐
        (0,1,0,0,1,0): '\U0001FB11', # 🬑
        (1,1,0,0,1,0): '\U0001FB12', # 🬒
        (0,0,1,0,1,0): '\U0001FB13', # 🬓
        (1,0,1,0,1,0): '\U0000258C', # ▌
        (0,1,1,0,1,0): '\U0001FB14', # 🬔
        (1,1,1,0,1,0): '\U0001FB15', # 🬕
        (0,0,0,1,1,0): '\U0001FB16', # 🬖
        (1,0,0,1,1,0): '\U0001FB17', # 🬗
        (0,1,0,1,1,0): '\U0001FB18', # 🬘
        (1,1,0,1,1,0): '\U0001FB19', # 🬙
        (0,0,1,1,1,0): '\U0001FB1A', # 🬚
        (1,0,1,1,1,0): '\U0001FB1B', # 🬛
        (0,1,1,1,1,0): '\U0001FB1C', # 🬜
        (1,1,1,1,1,0): '\U0001FB1D', #  '🬝'

        (0,0,0,0,0,1): '\U0001FB1E', # '🬞'
        (1,0,0,0,0,1): '\U0001FB1F', #  '🬟'
        (0,1,0,0,0,1): '\U0001FB20', # '🬠'
        (1,1,0,0,0,1): '\U0001FB21', #  '🬡'
        (0,0,1,0,0,1): '\U0001FB22', # '🬢'
        (1,0,1,0,0,1): '\U0001FB23', #  '🬣'
        (0,1,1,0,0,1): '\U0001FB24', # '🬤'
        (1,1,1,0,0,1): '\U0001FB25', #  '🬥'
        (0,0,0,1,0,1): '\U0001FB26', # '🬦'
        (1,0,0,1,0,1): '\U0001FB27', #  '🬧'
        (0,1,0,1,0,1): '\U00002590', # '▐'
        (1,1,0,1,0,1): '\U0001FB28', #  '🬨'
        (0,0,1,1,0,1): '\U0001FB29', # '🬩'
        (1,0,1,1,0,1): '\U0001FB2A', #  '🬪'
        (0,1,1,1,0,1): '\U0001FB2B', # '🬫'
        (1,1,1,1,0,1): '\U0001FB2C', #  '🬬'

        (0,0,0,0,1,1): '\U0001FB2D', # '🬭'
        (1,0,0,0,1,1): '\U0001FB2E', #  '🬮'
        (0,1,0,0,1,1): '\U0001FB2F', # '🬯'
        (1,1,0,0,1,1): '\U0001FB30', #  '🬰'
        (0,0,1,0,1,1): '\U0001FB31', # '🬱'
        (1,0,1,0,1,1): '\U0001FB32', #  '🬲'
        (0,1,1,0,1,1): '\U0001FB33', # '🬳'
        (1,1,1,0,1,1): '\U0001FB34', #  '🬴'
        (0,0,0,1,1,1): '\U0001FB35', # '🬵'
        (1,0,0,1,1,1): '\U0001FB36', #  '🬶'
        (0,1,0,1,1,1): '\U0001FB37', # '🬷'
        (1,1,0,1,1,1): '\U0001FB38', #  '🬸'
        (0,0,1,1,1,1): '\U0001FB39', # '🬹'
        (1,0,1,1,1,1): '\U0001FB3A', #  '🬺'
        (0,1,1,1,1,1): '\U0001FB3B', # '🬻'
        (1,1,1,1,1,1): '\U00002588'} #  '█'

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
    eta = 1
    #random setup for Linear Congruential Generator
    Xn = 2718
    m = 1 << 32 # 1 << 64
    a = 1664525 # (6364136223846793005)
    c = 1013904223 # 1
    for y in range(B.shape[0]):
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
    #algo = Atkinson
    #FloydSteinberg
    #JarvisJudisNinke
    algo = FSAtkinson # seems FSA is better than Hybrid...
    # algo = AtkinsonRand
    # algo = FSAtkinsonRand
    # full res dither
    if fullQ:
        Bx = numpy.array(image.convert('L'))
        algo(Bx)
        Image.fromarray(Bx).show()

    if invQ:
        image = ImageOps.invert(image)

    # Calculate scaling factors to fit the image within the terminal grid
    x_scale = width / eff_width
    y_scale = height / eff_height
    scale = x_scale if scale_mode=='x' else max(x_scale, y_scale)
    width, height = round(width/scale), round(height/scale)
    print("rescaled size", width, height, ", overhangs", over_w := width%6, over_h := height%12)
    height_p = height + (12 - over_h) if over_h else height # padded array
    width_p = width + (6 - over_w) if over_w else width # padded array
    B = numpy.zeros( (height_p, width_p), dtype='uint8')
    # top padding
    if over_h == 1 or over_h == 2 or over_h == 3: # padding: 2 black blocks
        B[8:12-over_h,:] = B[12-over_h:12-over_h+2,:].mean(axis=0,keepdims=True)
    elif over_h == 5 or over_h == 6 or over_h == 7: # padding: 1 black block
        B[4:12-over_h,:] = B[12-over_h:12-over_h+2,:].mean(axis=0,keepdims=True)
    elif over_h == 9 or over_h == 10 or over_h == 11: # padding: 0 black block
        B[0:12-over_h,:] = B[12-over_h:12-over_h+2,:].mean(axis=0,keepdims=True)
    # right padding
    if over_w == 1 or over_w == 2: # padding: 1 black blocks
        B[:,width_p+1:-3] = B[:,width_p-1:width_p+1].mean(axis=1,keepdims=True)
    elif over_h == 4 or over_h == 5: # padding: 0 black block
        B[:,width_p+1:] = B[:,width_p-1:width_p+1].mean(axis=1,keepdims=True)
    image = image.resize((width,height))
    image = image.convert('L')
    B[-height:,:width] = image
    #block into (4,3) yay
    B43 = B.reshape( (height_p, width_p//3, 3) ).reshape( (height_p//4, 4, width_p//3, 3) )
    B43 = B43.mean( axis=(1,3) )
    algo(B43)
    height_b, width_b = B43.shape
    D = B43.astype('bool').reshape((height_b//3,3,width_b)).reshape((height_b//3,3,width_b//2,2))
    D = D.transpose((0,2,1,3)).reshape((height_b//3,width_b//2,6))

    # Process each block of pixels and display in terminal
    line = ""
    for y in D:
        #line = ""
        for x in y:
            v = tuple(x)
            line += C_TREE[v]
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
    terminal_size = os.get_terminal_size()
    eff_width = 6*terminal_size.columns
    eff_height = 12*(terminal_size.lines-1) # save 1 for sys prompt

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

if __name__ == "__main__":
    main( sys.argv[1:] )
