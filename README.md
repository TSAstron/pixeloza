# pixeloza
&nbsp; (or pixelosis) is a series of programs to display images in a text terminal, using increasingly involved characters: from simple rectangular blocks, to triangles and polygons. The basic versions should work in any console/text file, the later ones require more unicode (fonts).
In any case, **pure text** is used, there is no pixel-level display involved. Check the [Appendix](#appendix) for the necessary python packages.

## pixeloza1.py

This mode was added retrospectively, so that images can be displayed as true monochrome black/white, but with dithering, so they are actually recognizable. There are several classical dithering algorithms inside, and the code uses my own
[mix of Atkinson and Floyd-Steinberg](https://monodromy.group/blog/mini/froginson.php). It produces something like this:<br>
<img alt="a pixelated frog" src="/images/froszka_ex1_1.jpeg" width=300> &emsp; from the original &emsp;
<img alt="a colourful frog" src="/images/froszka_ex1_0.jpeg">.

If run without arguments, it will give you frogs. But you can supply any number of keywords to be searched for on the internet, e.g. `python3 pixeloza1.py space elves`. The output can additionally be manipulated with the available options:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--inv` - to invert black/white (for pasting into text files);<br>
`--show_full` - to display (as an image with the default viewer) the full resolution dithered picture;<br>
`--help` - to show the options and usage.<br>

With a tiny font size (like 6) the images are surprisingly good, but that is not working size terminal. The real improvements come with the next modes.<br>
For an image-to-image dithering, with various algorithms, check out the [JavaScript implementation on my homepage](https://monodromy.group/dither/).

## pixeloza2.py

This is the actual basic version, which pixelates the image using ▀, as before, but manipulating the full RGB color.
The font should have 2:1 aspect ratio for best results, otherwise the image will be slightly distorted. But effects are already great,
with mere 98 rows and 188 columns we get:<br>
<img alt="a pixelized frog" src="/images/froszka_ex2_1.jpeg" width=480><br>
from the original:<br>
<img alt="a smiling, colourful frog" src="/images/froszka_ex2_0.jpeg" width=480>.

(Yes, I am aware of the irony of inserting a high resolution image of a block text reduction of a high resolution image ;)

The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--inv` - to invert colours;<br>
`--help` - to show the options and usage.<br>

## pixeloza3.py

An improvement on pixeloza1, utilizing 1/6 blocks (like 🬗). This will require a font that covers the unicode range of U+1FB00 -- U+1FB3B, but standard fonts like Ubuntu Mono, DejaVu Sans Mono, Cascadia Mono or Noto Mono work. The displayed blocks are no longer squares, but the algorithm takes that into account, achieving a somewhat better resolution. However, this is where the OS and the specific terminal you use will start interfering visibly: various hinting and aliasing rules might lead to the blocks being separate by empty lines (for some font sizes), leading to a sliced image. Not much can be done about it, other than creating custom fonts for specific terminals - like in [pixeloza8](#pixeloza8py).<br>
Here's our frog model again, looking even better:<br>
<img alt="a pixelized frog" src="/images/froszka_ex1_3.jpeg" width=360>

The available options are the same as for pixeloza1:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--inv` - to invert black/white (for pasting into text files);<br>
`--show_full` - to display (as an image with the default viewer) the full resolution dithered picture;<br>
`--help` - to show the options and usage.<br>

## pixeloza4.py

This version is black and white, as its primary goal was to get compound pixel shapes working. Before, the simple character ▀ effectively acted as two pixels, because both its foreground and background colours could be set independently (top and bottom squares, respectively). However, in the search for higher resolution, characters such as ▚ or 🬗 were included here. But this does not mean the whole block is now divided into 6 independent pixels. It is still only possible to set the fore- and background colours (or graylevels), meaning that multiple visible pixels/rectangles share their values. So the main task solved here, was to decide what sort of shape best fits a fragment of the original image, and with what level of gray. Assuming that each character has a 2:1 aspect ratio, this can be done by dividing the original image's pixelarray into rectangles 12 pixel high and 6 pixel wide (so each black part of 🬗 is 4 by 3), from which the values of the bak- and foreground can be computed for each shape. Then it's just  matter of choosing which shapes minimizes the error (e.g. mean square).

With this, what is achieved is almost 300 pixels of effective width (and in the wide mode even more of height). Here is the previous image again for comparison:<br>
<img alt="a pixelized frog" src="/images/froszka_ex4_1.jpeg" width=480>

Note, that there is no internal dithering or anti-aliasing applied, although that would further help. But it wasn't the goal really.

The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--inv` - to invert colours;<br>
`--help` - to show the options and usage.<br>

## pixeloza5.py

The final challenge is to add colour and extend to other (relatively simple) polygonal shapes, like triangles and lines. The former turned out not to be that difficult — there are just 3 channels instead of one value per pixel, so the red, green, and blue levels for each sub-shape can be determined independently, and it's just a matter of deciding on how to quantify (dis)agreement. I implemented a simple sum of errors. The latter is also almost solved in the previous version — given any character's shape, the question is how the image's pixel project onto it. We just have to count pixel values using the character sub-shapes as masks (hence the additional module masks.py). Once we have a general procedure, any mask can be implemented. Version 5 has many new characters like:  ▎, 🭀, 🭜 or 🮚. This allows for uncanny improvement, although sometimes the pointy angles are discernible.

Here's a crab for a change:<br>
<img alt="a pixelized colourful crab" src="/images/froszka_ex5_1.jpeg" width=480><br>
from the original:<br>
<img alt="a colourful crab" src="/images/froszka_ex5_0.jpeg" width=480>.

The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--inv` - to invert colours;<br>
`--rect` - to only use tha rectangular masks, i.e. the same characters as [pixeloza4.py](#pixeloza4py);<br>
`--help` - to show the options and usage.<br>

The first frog now looks like this:<br>
<img alt="a colourful frog" src="/images/froszka_ex5_2.jpeg" width=480>.

## pixeloza8.py

The "version" number really signifies the 8-bit of blocks like 𜵘 - all possible 2x4 square configurations available at our disposal.
Although these can be found in the Symbols for Legacy Computing Supplement Unicode block,
and various fonts (like Cascadia) have them, they display inconsistently across systems and terminals.
Plus, inconveniently, the characters are not ordered properly: lacking those blocks that can be found elsewhere.

There are 256 characters required, and it would be nice if they were accessible with Python's simple `chr`.
So, I made my own pixel fonts, included here, that occupy the Private Usa Are starting at U+EE00.
BinaryDejaVu4x2.ttf has the required blocks inserted into the DejaVu Sans Mono font,
while RandomYxZ.bdf are linux bitmap fonts of various sizes.
The former works everywhere, but might display with the artifacts mentioned in [pixeloza3](#pixeloza3py),
the latter works ideally under linux, specifically in the good old xterm via<br>
`xterm -fn "-*-Random8x16*"`

With a 16-pixel font on a 4K screen, the effect is like a normal dithered image,
although such a terminal is probably not very readable for actual text.<br>
<img alt="a dithered frog" src="/images/froszka_ex1_8.jpeg" width=480>
<img alt="a dithered crab" src="/images/froszka_ex5_8.jpeg" width=480>

The available options are the same as for pixeloza3:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--inv` - to invert black/white (for pasting into text files);<br>
`--show_full` - to display (as an image with the default viewer) the full resolution dithered picture;<br>
`--help` - to show the options and usage.<br>

##

See also the [interactive frogs and toads](https://monodromy.group/frogs/) and [the image ditherer](https://monodromy.group/dither/).
<br><br>

## Appendix

Though widely used, some python packages might not be included with your python distribution. Most likely these are:<br>
`requests`, `numpy`, `bs4` (BeautifulSoup), `Pillow` (PIL). The `numba` package is not necessary, but speeds up the computation considerably.<br>
Installation depends on the system, but for python3 it is usually some version of:<br>
`python3 -m pip install package_name` or `pip3 install package_name` (user/environment specific)<br>
`conda install conda-forge::package_name` (miniconda etc.)<br> 
`sudo apt install python3-package_name` (system-wide for Ubuntu).
