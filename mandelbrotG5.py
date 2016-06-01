#!/usr/bin/env python
from mandelproc import MandelProc
from multiprocessing import cpu_count
import colors
import png
import argparse
import math
import os
import sys


def floatlist(s):
    try:
        result = map(float, s.split(','))
    except Exception as exc:
        msg = "Couldn't convert {!r} to floatlist: {}"
        raise argparse.ArgumentTypeError(msg.format(s, exc))

    if any(math.isnan(f) or math.isinf(f) for f in result):
        msg = "Invalid float types: {}"
        raise argparse.ArgumentTypeError(msg.format(s))

    return result


def bounds(s):
    s = floatlist(s)
    if len(s) != 2:
        raise argparse.ArgumentTypeError("Bounds only have two coordinates!")
    if s[0] >= s[1]:
        raise argparse.ArgumentTypeError("Left coordinate in bounds must be less than right coordinate!")
    return s


def colorlist(s):
    colors = s.split(',')
    result = []
    err_msg = "Invalid color format {!r}. Colors must be of the form RRGGBB."
    for c in colors:
        if len(c) != 6:
            raise argparse.ArgumentTypeError(err_msg.format(c))
        c_rgb = []
        for i in range(3):
            e_x = c[2*i:2*i+1]
            try:
                e_i = int(e_x, 16)
            except:
                raise argparse.ArgumentTypeError(err_msg.format(c))
            c_rgb.append(e_i/255.0)
        result.append(c_rgb)
    if len(result) == 1:
        result.append(result[0])
    return result
                

parser = argparse.ArgumentParser(description='Generates images of the Mandelbrot set.',
                                 epilog='Dedicated to my Powermac G5 Quad.')
parser.add_argument('--height', '-H', help='Pixel height of the generated image', required=True, type=int)
parser.add_argument('--width', '-W', help='Pixel width of the generated image', required=True, type=int)
parser.add_argument('--processes', '-p', help='Number of processes to use for image generation.', default=cpu_count(), type=int)
parser.add_argument('--iterations', '-i', help='Number of iterations for \'escape time\' test.', default=100, type=int)
parser.add_argument('--verbose', '-v', help='Verbose output', action='store_true', default=False)
parser.add_argument('--real-bounds', '-r', help='Bounds for the real part of the Mandelbrot calculations.', type=bounds, default=(-2.0, 1.0))
parser.add_argument('--imaginary-bounds', '-I', help='Bounds for the imaginary part of the Mandelbrot calculations.', type=bounds, default=(-1.0, 1.0))
parser.add_argument('--color-pallete', '-c', help='Color pallete for the generated image. Must be of the form "RRGGBB,RRGGBB,RRGGBB", where R, G, and B are hex digits.', type=colorlist, default=colors.pallete)

# TODO:
# * add color option for inside Mandelbrot set
# * add output file name option


def color_rows(data, color_pallete, default):
    num_colors = len(color_pallete)
    default = [p/255.0 for p in default]
    for row in data:
        color_data = []
        add_color = color_data.extend
        for escape_time in row:
            if math.isnan(escape_time):
                add_color(default)
            else:
                start_color = int(escape_time%num_colors)
                end_color = int((start_color + 1)%num_colors)
                fraction = escape_time%1.0
                normalized_color = colors.rgb_interp(color_pallete[start_color],
                                                     color_pallete[end_color],
                                                     fraction)
                add_color(normalized_color)
        yield [int(255*p) for p in color_data]


def main():
    args = parser.parse_args()
    MandelProc.set_info(args.iterations,
                        args.width,
                        args.height,
                        args.processes,
                        args.real_bounds,
                        args.imaginary_bounds)
    procs, msg_q, data = MandelProc.begin_compute()
    img_file = open('mandelbrotG5-%dx%d.png'%(args.width,args.height), 'wb')
    writer = png.Writer(args.width, args.height)
    writer.write(img_file, color_rows(data, args.color_pallete, (0,0,0)))

if __name__ == '__main__':
    main()
