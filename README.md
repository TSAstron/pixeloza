# pixeloza
&nbsp; (or pixelosis) is a series of programs to display images in a text terminal, using increasingly involved characters: from simple rectangular blocks, to triangles and polygons. The basic versions should work in any console/text file, the later ones require more unicode. 

## pixeloza1.py

This mode was added retrospectively, so that images can be displayed as true monochrome black/white, but with dithering, so they are actually recognizable. There are several classical dithering algorithms inside, and the code uses my own
[mix of Atkinson and Floyd-Steinberg](https://monodromy.group/blog/mini/froginson.php). It produces something like this:<br>
<img alt="a pixelated frog" src="/images/froszka_ex1_1.jpeg" width=300> &emsp; from the original &emsp;
<img alt="a colourful frog" src="/images/froszka_ex1_0.jpeg">.

If run without arguments, it will give you frogs. But you can supply any number of keywords to be searched for on the internet.
The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--inv` - to invert black/white (for pasting into text files);<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--show_full` - to display (as an image with the default viewer) the full resolution dithered picture.<br>

With a tiny font size (like 6) the images are surprisingly good, but that is not working size terminal. The real improvements come with the next modes.

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
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all).<br>


## pixeloza3

There is no pixeloza3.

## pixeloza4.py

This version is black and white, as its primary goal was to get compound pixel shapes working. Before, the simple character ▀ effectively acted as two pixels, because both its foreground and background colours could be set independently (top and bottom squares, respectively). However, in the search for higher resolution, characters such as ▚ or 🬗 were included here. But this does not mean the whole block is now divided into 6 independent pixels. It is still only possible to set the fore- and background colours (or graylevels), meaning that multiple visible pixels/rectangles share their values. So the main task solved here, was to decide what sort of shape best fits a fragment of the original image, and with what level of gray. Assuming that each character has a 2:1 aspect ratio, this can be done by dividing the original image's pixelarray into rectangles 12 pixel high and 6 pixel wide (so each black part of 🬗 is 4 by 3), from which the values of the bak- and foreground can be computed for each shape. Then it's just  matter of choosing which shapes minimizes the error (e.g. mean square).

With this, what is achieved is almost 300 pixels of effective width (and in the wide mode even more of height). Here is the previous image again for comparison:<br>
<img alt="a pixelized frog" src="/images/froszka_ex4_1.jpeg" width=480>

Note, that there is no internal dithering or anti-aliasing applied, although that would further help. But it wasn't the goal really.

The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all).<br>

## pixeloza5.py

The final challenge is to add colour and extend to other (relatively simple) polygonal shapes, like triangles and lines. The former turned out not to be that difficult — there are just 3 channels instead of one value per pixel, so the red, green, and blue levels for each sub-shape can be determined independently, and it's just a matter of deciding on how to quantify (dis)agreement. I implemented a simple sum of errors. The latter is also almost solved in the previous version — given any character's shape, the question is how the image's pixel project onto it. We just have to count pixel values using the character sub-shapes as masks (hence the additional module masks.py). Once we have a general procedure, any mask can be implemented. Version 5 has many new characters like:  ▎, 🭀, 🭜 or 🮚. This allows for uncanny improvement, although sometimes the pointy angles are discernible.

Here's a crab for a change:<br>
<img alt="a pixelized colourful crab" src="/images/froszka_ex5_1.jpeg" width=480><br>
from the original:<br>
<img alt="a colourful crab" src="/images/froszka_ex5_0.jpeg" width=480>.

The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--rect` - to only use tha rectangular masks, i.e. the same characters as pixeloza4.py;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all).<br>

The first frog now looks like this:<br>
<img alt="a colourful frog" src="/images/froszka_ex5_2.jpeg" width=480>.

##

See also the [interactive frogs and toads](https://monodromy.group/frogs/).
