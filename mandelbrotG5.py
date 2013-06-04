import multiprocessing
import png

def pixproc(i0, isteps, iskip, rsteps, fname, cp):
    """This is the code that runs in each seperate process.
    i0 is the start row, and istep is the row after the last row
    (in keeping with python convention of using [start, end)
    intervals) and iskip is the number of rows to skip. rsteps and
    isteps are the number of points to use along the x and y axis
    (real and imaginary, respectively.) fname is a string containing
    the name to use for the temporary data file, and cp is the color
    palette to use."""
    def row(i_k):
        #this is a generator which yields the pixel values for
        #each column in the i_kth row. Everything in the mandelbrot
        #set is colored black
        for r in xrange(rsteps):
            c=complex(RMIN + RLEN*(1.*r/rsteps),
                      IMIN + ILEN*(1.*i_k/isteps))
            if abs(1-(1-4*c)**0.5) < 1.0: #the main cardioid
                yield 16
                continue
            if abs(c+1) < .25: #the biggest circle
                yield 16
                continue
            z=c
            for j in xrange(256):
                z = z*z + c
                if abs(z)>2: break
            if j<255:
                yield j%16
            else:
                yield 16
    
    RMIN, IMIN = -2, -1
    RLEN, ILEN = 3, 2
    writer = png.Writer(width=rsteps, height=(isteps/iskip), palette=cp)
    f = open(fname, 'wb')
    writer.write(f, (row(i) for i in xrange(i0, isteps, iskip)))
    f.close()
    return


def main(width, height, cp):
    """This main function chunks up the the graph so that
    each cpu gets and equal amount of points to check. xsteps
    and ysteps are the width and height respectively in pixels
    of the image you want to make."""
    pool = multiprocessing.Pool()
    n = multiprocessing.cpu_count()
    fnames = ["temp{}.png".format(i) for i in xrange(n)]
    for y_0 in xrange(n):
        pool.apply_async(pixproc, 
                         (y_0, 
                          height,
                          n,
                          width,
                          fnames[y_0],
                          cp))
    pool.close()
    pool.join()
    return fnames

def rowIter(fnames, columns, rows):
    """This function is a generator which for each
    row in your image, yields a generator which yields
    the data in each column of the specific row. fnames
    is a list of strings containing the names of the temporary
    files, and should be in order! columns and rows is the 
    width and the height respectively of the image in pixels.
    Also deletes the temporary files from disk."""
    files = [png.Reader(fname).read()[2] for fname in fnames]
    for _ in xrange(rows):
        yield files[_%4].next()
    

if __name__=="__main__":
    import sys
    
    #get the width and height from two arguments
    width, height = map(int, sys.argv[1:]) 

    cp = [(241, 233, 191),  #I stole this color pallete from:
          (248, 201, 95),   #http://www.pygame.org/project-Mandelbrot+Set+Viewer-698-.html
          (255, 170, 0), 
          (204, 108, 0), 
          (153, 87, 0), 
          (106, 52, 3),
          (66, 30, 15), 
          (25, 7, 26),  
          (9, 1, 47), 
          (4, 4, 73), 
          (0, 7, 100), 
          (12, 44, 138), 
          (24, 82, 177), 
          (57, 125, 209),
          (134, 181, 229), 
          (211, 236, 248),
          (0, 0, 0)]
    
    #get the file names of the temporary data files
    fnames = main(width, height, cp)
    
    #open the file to be used for the picture
    pic = open("mandelbrot.png", "wb")



    #create the writer object
    pic_writer = png.Writer(width=width, height=height, palette=cp)

    #write the data
    pic_writer.write(pic, rowIter(fnames, width, height))
