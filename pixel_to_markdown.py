# Pillow is supposed to be a good imaging library. It's a fork of PIL.
from PIL import Image
from __future__ import print_function, division
import math
import sys
import operator
import ahto_lib

# image.getcolors image.getpixel
# getpixel returns (R, G, B)
# image.width image.height
# pixels start at the upper-right corner at 0,0



# All values are in pixels.
SPACE_CHAR_WIDTH = 5
MONOSPACE_CHAR_WIDTH = 8

# 7 at the beginning and 7 at the end.
MONOSPACE_CONTAINER_WIDTH = 7+7

NBSP = u'\xa0'

# Character to use inside of the markdown 'pixels'.
PIXEL_CHAR = NBSP

pixel_width = MONOSPACE_CONTAINER_WIDTH + MONOSPACE_CHAR_WIDTH

def color_to_str(color):
    return ('#' + hex(color[0])[2:]
                + hex(color[1])[2:]
                + hex(color[2])[2:])

def image_to_markdown(image, dark_color, light_color):
    # This is the exact pixel value we're at right now.
    markdown_x = 0

    markdown = ''

    def is_pixel_dark(color):
        if pixel == dark_color:
            return True
        elif pixel == light-color:
            return False
        else:
            raise ValueError("Image has invalid color: {color}".format(
                color=color_to_str(color)))

    for y in xrange(image.height):
        for x in xrange(image.width):
            dark = is_pixel_dark( image.getpixel((x, y)) )

            if dark:
                markdown += '`' + NBSP + '`'
                markdown_x += pixel_width
            else:
                goal_x = float(pixel_width*x)
                spaces_to_add = (goal_x - markdown_x) / SPACE_CHAR_WIDTH
                markdown   += NBSP * spaces_to_add
                markdown_x += SPACE_CHAR_WIDTH * spaces_to_add

        markdown  += '  \n'
        markdown_x = 0

    return markdown

if __name__ == '__main__':
    image = Image.open(sys.argv[1])
    print("Opened image file: " + sys.argv[1])
    print(image.format, image.mode, image.size)
    colors = image.getcolors()

    if len(colors) != 2:
        print("Image has too many different colors. 2 expected,"
            " {} found.".format(len(colors)))
        exit(1)

    lightest_color, darkest_color = sorted(colors, key=sum)

    print("Colors automatically detected.")
    print("Color for 'black': {b}  Color for 'white': {w}".format(
        b=color_to_str(darkest_color),
        w=color_to_str(lightest_color))

    if not ahto_lib.yes_no(True, "Does that look correct?"):
        exit(1)

    print()

    if len(sys.argv) >= 3:
        markdown_filename = sys.argv[2]
    else:
        markdown_filename = 'image.md'

    print('Writing to:', markdown_filename)

    with open(markdown_filename, 'w') as mdfile:
        mdfile.write( image_to_markdown(image) )
