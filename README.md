# pixeloza
&nbsp; (or pixelosis) is a series of programs to display images in a text terminal, using increasingly involved characters: from simple rectangular blocks, to triangles and polygons. The basic versions should work in any console/text file, the later ones require more unicode. 

## pixeloza1

This mode was added retrospectively, so that images can be displayed as true monochrome black/white, but with dithering, so they are actually recognizable. There are several classical dithering algorithms inside, and the code uses my own
[mix of Atkinson and Floyd-Steinberg](https://monodromy.group/blog/mini/froginson.php). It produces something like this:<br>
<img alt="a colourful frog" src="/images/froszka_ex1_1.jpeg" width=300> &emsp; from the original &emsp;
<img alt="a colourful frog" src="/images/froszka_ex1_0.jpeg">.

If run without arguments, it will give you frogs. But you can supply any number of keywords to be searched for on the internet.
The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--inv` - to invert black/white (for pasting into text files);<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all);<br>
`--show_full` - to display (as an image with the default viewer) the full resolution dithered picture.<br>

## pixeloza2

This is the actual basic version, which pixelates the image using ▀, as before, but manipulating the full RGB color.
The font should have 2:1 aspect ratio for best results, otherwise the image will be slightly distorted. But effects are already great,
with mere 98 rows and 188 columns we get:<br>
<img alt="a colourful frog" src="/images/froszka_ex2_1.jpeg" width=480><br>
from the original:<br>
<img alt="a colourful frog" src="/images/froszka_ex2_0.jpeg" width=480>.

(Yes, I am aware of the irony of inserting a high resolution image of a block text reduction of a high resolution image ;)

The available options are:<br>
`--file PATH` - to show a local file;<br>
`--web URL` - to show image at that url;<br>
`--wide` - to make the image use all available terminal columns (so you need ot scroll to see it all).<br>


## pixeloza3

There is no pixeloza3.

## pixeloza4

Coming soon.

## pixeloza3

Coming soon.

##

See also the [interactive frogs and toads](https://monodromy.group/frogs/).
