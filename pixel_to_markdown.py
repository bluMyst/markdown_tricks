# Pillow is supposed to be a good imaging library. It's a fork of PIL.
from PIL import Image
from __future__ import print_function
import sys
import operator

class Color(object):
    def __init__(self, red, green, blue):
        self.red   = red
        self.green = green
        self.blue  = blue
        self.value = sum([red, green, blue])

    def __repr__(self):
        return "Color({self.red}, {self.green}, {self.blue}".format(**locals())

    def __str__(self):
        s = '#'
        s += hex(self.red)[:2]
        s += hex(self.green)[:2]
        s += hex(self.blue)[:2]
        return s

if __name__ == '__main__':
    image = Image.open(sys.argv[1])
    print("Opened image file: " + sys.argv[1])
    print(image.format, image.mode, image.size)
    # image.getdata image.getcolors image.getpalette image.getpixel
    # getpixel returns (R, G, B)
    colors = image.getcolors()

    if len(colors) != 2:
        print("Image has too many different colors. 2 expected, {} found.".format(
            len(colors)))
        exit(1)
    else:
        colors = [Color(*color) for _, color in colors]

        lightest_color, darkest_color = colors.sort(
            key=operator.attrgetter('value'))

    print()
