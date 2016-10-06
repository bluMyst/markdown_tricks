# Pillow is supposed to be a good imaging library. It's a fork of PIL.

from PIL import Image
import math
import sys
import operator
import ahto_lib
import itertools

# Some terminology:
# The following is called a monospace block:
# `##`
# This particular monospace block has a width of 2. Note that this isn't the same thing as its
# width in actual pixels.
# A monospace pixel can be either filled (monospace block) or unfilled (NBSP's).
# A monospace pixel is different from a normal pixel. A monospace pixel is an imaginary grid of pixels
# that are each one monospace block long.

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

NBSP = '\u00A0'

def debug(*args, **kwargs):
    if DEBUG:
        return print(*args, **kwargs)
    else:
        return None

def color_to_str(color):
    ''' takes an (r, g, b) tuple '''
    return '#{:0>2X}{:0>2X}{:0>2X}'.format(*color)

class ImageMarkdownConverter(object):
    def __init__(self, image, invert=False, block_char='#', block_width=2):
        'If invert is True, the filled-in pixels will be the lighter ones.'
        self.image       = image
        self.block_char  = block_char
        self.block_width = block_width

        colors = [color for occurances, color in image.getcolors()]

        if len(colors) != 2:
            raise ValueError("ImageMarkdownConverter called on image with "
                + str(len(colors)) + " colors.")

        self.filled_color, self.blank_color = sorted(
            colors, key=sum, reverse=invert)

        if DEBUG:
            print("Checking image for colors we don't expect...", end='')

            for pixel in self.image.getdata():
                assert pixel in [self.filled_color, self.blank_color]

            print(" done.")

    def get_monospace_block_width(self):
        return MONOSPACE_CONTAINER_WIDTH + MONOSPACE_CHAR_WIDTH * self.block_width

    def _map_over_image(self, f):
        ''' function f should take args in the form of f(x, y, pixel_color) '''

        for y in range(self.iamge.width):
            for x in range(self.image.height):
                f(x, y, self.image.getpixel((x, y)))

    def ascii_art(self, block_width=2, filled_char='#', blank_char=' '):
        ''' Converts the image to ASCII art and returns it as a string. '''
        s = ''

        for y in range(self.image.height):
            for x in range(self.image.width):
                filled = self.image.getpixel((x, y)) == self.filled_color
                pixel = filled_char if filled else blank_char
                s += pixel * block_width

            s += '\n'

        return s

    def image_to_markdown(self):
        # This is the exact pixel value we're at right now.
        markdown_x = 0

        markdown = ''

        for y in range(image.height):
            for x in range(image.width):
                dark = self.image.getpixel((x, y)) == self.filled_color

                if dark:
                    markdown   += '`' + self.block_char * self.block_width + '`'
                    markdown_x += self.get_monospace_block_width()
                else:
                    goal_x = self.get_monospace_block_width() * (x+1)

                    spaces_to_add = int(round(
                        (goal_x - markdown_x) / SPACE_CHAR_WIDTH))

                    if DEBUG:
                        # TODO: Very ugly code below.
                        debug("{markdown_x:>4}px ->"
                            " {new_x:>4}px / {goal_x:>4}px  ".format(
                            new_x = markdown_x + SPACE_CHAR_WIDTH * spaces_to_add,
                            **locals()), end='')

                        debug("{a:>4}px, ({b:>4}px), {c:>4}px".format(
                            a=(spaces_to_add-1) * SPACE_CHAR_WIDTH + markdown_x,
                            b=(spaces_to_add)   * SPACE_CHAR_WIDTH + markdown_x,
                            c=(spaces_to_add+1) * SPACE_CHAR_WIDTH + markdown_x))

                    markdown   += NBSP * spaces_to_add
                    markdown_x += SPACE_CHAR_WIDTH * spaces_to_add

            markdown  += '  \n'
            markdown_x = 0
            debug()

        return markdown

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Turn simple black-and-white images'
                    ' into Markdown documents. Default output file is image.md,'
                    " so if you can't find your file, it's probably there.")

    parser.add_argument('-d', '--debug', action='store_true',
        help='print debug information and do extra data-checking')

    parser.add_argument('-i', '--invert', action='store_true',
        help='Invert the image, so that the lighter pixels will be filled in'
             ' and the darker pixels will be left blank.')

    # The percent sign is treated as a special character in the help, so we escape it with a second
    # percent sign.
    parser.add_argument('-b', '--block-char', metavar='CHR', dest='block_char', default='#',
        #help='the character used to fill in pixels')
        help='''
            Character to use inside of the markdown 'pixels'. On reddit night mode, NBSP
            looks good because the monospace boxes themselves are a noticably different
            color from the background. For day mode, though, try '#' or '%%'. Be careful
            with unicode characters because the spacing tends to be sliiiightly off, even
            in a monospace font.
        ''')

    # Number of characters per pixel. On reddit, 2 looks 'streteched out', but the
    # pixels are in a perfect grid.
    parser.add_argument('-w', '--block-width', metavar='INT', dest='block_width', default=2, type=int,
        #help='the number of characters per pixel (be careful with this one)')
        help='''
            Number of characters per 'pixel'. On reddit, 2 looks streteched out, but the
            pixels are in a perfect grid. 1 has more square-looking pixels, but they're slightly wonky.
            3 and above are a horrible idea.
        ''')

    #parser.add_argument('image', type=argparse.FileType('r'),
    #parser.add_argument('image', type=(lambda filename: open(filename, 'r')),
    parser.add_argument('image', help='the image file to use')

    parser.add_argument('outfile', nargs='?', default='image.md',
        type=argparse.FileType('w'), help='The file to output markdown to.'
                                          ' (default = image.md)')

    args  = parser.parse_args()
    DEBUG = args.debug

    if DEBUG:
        from pprint import pprint
        pprint(args)

    if len(args.block_char) != 1:
        print('Invalid pixel_char:', args.pixel_char)
        print('Can only be one character long.')
        exit(1)

    image = Image.open(args.image)
    print(image.format, image.mode, image.size)
    converter = ImageMarkdownConverter(image, args.invert, args.block_char, args.block_width)

    filled, blank = converter.filled_color, converter.blank_color
    print("Color for 'filled': {f}  Color for 'blank': {b}".format(
        f=color_to_str(filled),
        b=color_to_str(blank)))

    print(converter.ascii_art(filled_char=args.block_char))

    if not ahto_lib.yes_no(True, "Does that look correct?"):
        exit(1)

    print()

    markdown = converter.image_to_markdown()
    #args.outfile.write(markdown.encode('utf8'))
    args.outfile.write(markdown)
