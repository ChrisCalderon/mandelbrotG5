#!/usr/bin/env python
from mandelproc import MandelProc
from multiprocessing import cpu_count
import colors
import png
import argparse
from array import array
import math
import os
import sys

parser = argparse.ArgumentParser(description='Generates images of the Mandelbrot set.',
                                 epilog='Dedicated to my Powermac G5 Quad.')
parser.add_argument('--height', '-H', help='Pixel height of the generated image', required=True, type=int)
parser.add_argument('--width', '-W', help='Pixel width of the generated image', required=True, type=int)
parser.add_argument('--processes', '-p', help='Number of processes to use for image generation.', default=cpu_count(), type=int)
parser.add_argument('--iterations', '-i', help='Number of iterations for \'escape time\' test.', default=100, type=int)
parser.add_argument('--verbose', '-v', help='Verbose output', action='store_true', default=False)


# TODO: 
# * add real/imag axis bound option for zooming/generating specific sections.
# * add color pallete option; e.g. --colors #ff0000,#00ff00,#0000ff


def row_color(row, pallete, default):
    """Makes color data suitable for a png.Writer.

    Arguments:
    row - An iterable of smoothed iteration escape times.
    pallete - A list of colors to use for interpolation.
    default - The default color to use for NaN values; i.e. for values in the set."""

    NaN = float('NaN')
    result = []
    l = len(pallete)
    for iter_val in row:
        if math.isnan(iter_val):
            result.extend(default)
        else:
            p = iter_val % 1
            i = int(iter_val % l)
            rgb = colors.rgb_interp(pallete[i], pallete[(i + 1)%l], p)
 #           print rgb
            result.extend([int(255*c) for c in rgb])
#    print result
    return result


def yield_rows(data_files, height, width, colors, default, v):
    """Generates rows of color data from a list of data files."""
    n = len(data_files)
    for i in xrange(height):
        df = data_files[i%n]
        iter_vals = array('f')
        iter_vals.fromstring(df.read(4*width)) # each float is 4 bytes.
        yield row_color(iter_vals, colors, default)
        if v:
            sys.stdout.write('\rWrote row %d/%d' % (i, height))
            sys.stdout.flush()
    print


def main():
    args = parser.parse_args()
    MandelProc.set_info(args.iterations,
                        args.width,
                        args.height,
                        args.processes)
    procs, msg_q = MandelProc.begin_compute()

    
    done = 0
    while done < args.processes:
        r = msg_q.get()
        if r == 'done':
            done += 1
        if args.verbose:
            print r

    for p in procs:
        p.join()

    data_files = [open(p.results, 'rb') for p in procs]
    img_file = open('mandelbrotG5-%dx%d.png'%(args.width,args.height), 'wb')
    writer = png.Writer(args.width, args.height)
    row_generator = yield_rows(data_files,
                               args.height,
                               args.width,
                               colors.pallete,
                               (0,0,0),
                               args.verbose)
    writer.write(img_file, row_generator)
    for f in data_files:
        f.close()
        os.remove(f.name)
        

if __name__ == '__main__':
    main()
