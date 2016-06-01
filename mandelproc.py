from multiprocessing import Process, Queue, RawArray
import numpy as np
from array import array
from math import log


class MandelProcException(Exception): pass


class MandelProc(Process):

    ITERATIONS = None
    PIXWIDTH = None
    PIXHEIGHT = None
    STEP = None
    RMIN = None
    RMAX = None
    IMIN = None
    IMAX = None

    def __init__(self, procnum, msg_q, data, *args, **kwds):
        """A helper process for generating the Mandelbrot set."""
        Process.__init__(self, *args, **kwds)
        self.offset = procnum
        self.msg_q = msg_q
        self.data = data


    @classmethod
    def set_info(cls, iters, width, height, num_procs, rbounds, ibounds):
        """Sets constants for the parallel computation.

        Argument:
        iters - the number of iterations to use for the escape time test.
        width - the width of the image being generated in pixels.
        height - the height of the image being generated in pixels.
        num_procs - the number of helper processes that will run."""
        cls.ITERATIONS = iters
        cls.PIXWIDTH = width
        cls.PIXHEIGHT = height
        cls.STEP = num_procs
        cls.RMIN = rbounds[0]
        cls.RMAX = rbounds[1]
        cls.IMIN = ibounds[0]
        cls.IMAX = ibounds[1]

    @classmethod
    def begin_compute(cls):
        """Starts the Mandelbrot set computation."""
        no_val = "No {} value set!"
        essential_values = [
            "ITERATIONS",
            "PIXWIDTH",
            "PIXHEIGHT",
            "STEP",
            "RMIN",
            "RMAX",
            "IMIN",
            "IMAX",
        ]

        for v in essential_values:
            if getattr(cls, v, None) is None:
                raise MandelProcException(no_val.format(v))
        
        shared_array = RawArray('f', cls.PIXWIDTH*cls.PIXHEIGHT)
        np_array = np.frombuffer(shared_array, dtype='f')
        np_array = np_array.reshape(cls.PIXHEIGHT, cls.PIXWIDTH)
        msg_q = Queue()
        procs = [cls(i, msg_q, np_array) for i in range(cls.STEP)]
        for p in procs:
            p.start()
        return procs, msg_q, np_array

    def run(self):
        ##### Constants #####
        PIXHEIGHT = MandelProc.PIXHEIGHT
        PIXWIDTH = MandelProc.PIXWIDTH
        ITERATIONS = MandelProc.ITERATIONS
        STEP = MandelProc.STEP
        RMIN = MandelProc.RMIN
        RMAX = MandelProc.RMAX
        IMIN = MandelProc.IMIN
        IMAX = MandelProc.IMAX
        LOG2 = log(2)
        BAILRADIUS = 1 << 16
        msg_q = self.msg_q
        data = self.data
        NaN = float('NaN') # Nan is used to signal "in the set"
        #####################

        for py in np.arange(self.offset, PIXHEIGHT, STEP):
            # scale y pixel to be between 1 and -1.
            # note: pixel y axis increases as cartesian y axis decreases,
            # which is why (pixheight - py) is used.
            y0 = IMIN + (IMAX - IMIN)*(PIXHEIGHT - py)/PIXHEIGHT
            msg_q.put('Starting work for row %d/%d'%(py,PIXHEIGHT))
            data[py,:] = NaN

            for px in np.arange(PIXWIDTH):
                # scale x pixel to be between -2 and 1.
                x0 = (RMAX - RMIN)*px/PIXWIDTH + RMIN
                # cardiod test
                q = (x0 - .25)**2 + y0*y0
                if q*(q + (x0 - .25)) < .25*y0*y0:
                    continue
                    
                # period 2 bulb test
                if (x0 + 1)**2 + y0*y0 < 0.0625:
                    continue

                # escape time test
                i = 0
                x = 0.0
                y = 0.0
                while (x*x + y*y < BAILRADIUS) and (i < ITERATIONS):
                    # a simple periodicity check
                    xtemp = x*x - y*y + x0
                    ytemp = 2*x*y + y0
                    if x==xtemp and y==ytemp:
                        i = ITERATIONS
                        break
                      
                    x = xtemp
                    y = ytemp
                    i = i + 1

                # smooth iteration count
                if i < ITERATIONS:
                    log_zn = log(x*x + y*y)/2
                    nu = log(log_zn/LOG2)/LOG2
                    i = i + 1 - nu
                    data[py,px] = i
        
        msg_q.put('done')
