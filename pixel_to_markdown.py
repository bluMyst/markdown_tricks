# Pillow is supposed to be a good imaging library. It's a fork of PIL.
from __future__ import print_function, division
from PIL import Image
import math
import sys
import operator
import ahto_lib

# TODO: Command-line flags and options.

# image.getcolors image.getpixel
# getpixel returns (R, G, B)
# image.width image.height
# pixels start at the upper-right corner at 0,0

DEBUG = True

# All values are in pixels.
SPACE_CHAR_WIDTH = 5
MONOSPACE_CHAR_WIDTH = 8

# 7 at the beginning and 7 at the end.
MONOSPACE_CONTAINER_WIDTH = 7+7

NBSP = u'\u00A0'

# Character to use inside of the markdown 'pixels'. On reddit night mode, NBSP
# looks good because the monospace boxes themselves are a noticably different
# color from the background. For day mode, though, try '#' or '%'. Be careful
# with unicode characters because the spacing tends to be sliiiightly off, even
# in a monospace font.
PIXEL_CHAR = '#'

# Number of characters per pixel. On reddit, 2 looks 'streteched out', but the
# pixels are less offcenter.
PIXEL_NUM_CHARS = 2

pixel_width = MONOSPACE_CONTAINER_WIDTH + MONOSPACE_CHAR_WIDTH * PIXEL_NUM_CHARS

def debug(*args, **kwargs):
    if DEBUG:
        return print(*args, **kwargs)
    else:
        return None

def color_to_str(color):
    def to_hex_byte(n):
        return hex(n)[2:].zfill(2)

    return '#' + ''.join(map(to_hex_byte, color))

def image_to_markdown(image, filled_color, blank_color):
    # This is the exact pixel value we're at right now.
    markdown_x = 0

    markdown = ''

    def is_pixel_dark(color):
        if color == filled_color:
            return True
        elif color == blank_color:
            return False
        else:
            raise ValueError("Image has invalid color: {color}".format(
                color=color_to_str(color)))

    for y in xrange(image.height):
        for x in xrange(image.width):
            dark = is_pixel_dark( image.getpixel((x, y)) )

            if not debug: print(('##' if dark else '  '), end='')

            if dark:
                markdown   += '`' + PIXEL_CHAR * PIXEL_NUM_CHARS + '`'
                markdown_x += pixel_width
            else:
                goal_x = pixel_width * (x+1)

                spaces_to_add = int(round(
                    (goal_x - markdown_x) / SPACE_CHAR_WIDTH))

                if DEBUG:
                    debug("{markdown_x:>4}px ->"
                        " {new_x:>4}px / {goal_x:>4}px  ".format(
                        new_x = markdown_x + SPACE_CHAR_WIDTH * spaces_to_add,
                        **locals()), end='')

                    debug("{sa} {pa:>4}px, ({sb} {pb:>4}px), {sc} {pc:>4}px".format(
                        sa=spaces_to_add-1,
                        pa=(spaces_to_add-1) * SPACE_CHAR_WIDTH + markdown_x,
                        sb=spaces_to_add,
                        pb=(spaces_to_add)   * SPACE_CHAR_WIDTH + markdown_x,
                        sc=spaces_to_add+1,
                        pc=(spaces_to_add+1) * SPACE_CHAR_WIDTH + markdown_x))

                markdown   += NBSP * spaces_to_add
                markdown_x += SPACE_CHAR_WIDTH * spaces_to_add

        markdown  += '  \n'
        markdown_x = 0
        print()

    print()
    return markdown

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='turn simple black-and-white images'
                    ' into Markdown documents')

    parser.add_argument('-d', '--debug', action='store_true',
        help='print debug information')

    parser.add_argument('-i', '--invert', action='store_true',
        help='invert the image, so that the lighter pixels will be filled in'
             ' and the darker pixels will be left blank')

    parser.add_argument('-p', '--pixel-char', dest='pixel_char', default='#',
        help='the character used to fill in pixels')

    parser.add_argument('image', type=argparse.FileType('r'),
        help='the image file to use')

    parser.add_argument('outfile', nargs='?', default='image.md',
        type=argparse.FileType('w'), help='the file to output markdown to')

    args       = parser.parse_args()
    DEBUG      = args.debug
    PIXEL_CHAR = args.pixel_char

    if DEBUG:
        from pprint import pprint
        pprint(args)

    if len(args.pixel_char) != 1:
        print('Invalid pixel_char:', args.pixel_char)
        print('Can only be one character long.')
        exit(1)

    image = Image.open(sys.argv[1])
    print("Opened image file:", sys.argv[1], end=' ')
    print(image.format, image.mode, image.size)
    colors = image.getcolors()

    if len(colors) != 2:
        print("Image has too many different colors. 2 expected,"
            " {} found.".format(len(colors)))
        exit(1)

    colors = [color for occurances, color in colors]
    filled_color, blank_color = sorted(colors, key=sum, reverse=args.invert)

    print("Color for 'filled': {f}  Color for 'blank': {b}".format(
        f=color_to_str(filled_color),
        b=color_to_str(blank_color)))

    print('filled looks kinda like this: ['
        + str(PIXEL_CHAR * PIXEL_NUM_CHARS) + ']')
    print('blank is... blank')

    if not ahto_lib.yes_no(True, "Does that look correct?"):
        exit(1)

    print()

    if len(sys.argv) >= 3:
        markdown_filename = sys.argv[2]
    else:
        markdown_filename = 'image.md'

    print('Writing to:', markdown_filename)

    with open(markdown_filename, 'w') as mdfile:
        markdown = image_to_markdown(image, filled_color, blank_color)
        mdfile.write(markdown.encode('utf8'))
