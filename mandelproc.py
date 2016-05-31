from multiprocessing import Process, Queue
from array import array
from math import log


class MandelProcException(Exception): pass


class MandelProc(Process):

    ITERATIONS = None
    PIXWIDTH = None
    PIXHEIGHT = None
    STEP = None

    def __init__(self, procnum, msg_q, *args, **kwds):
        """A helper process for generating the Mandelbrot set."""
        self.offset = procnum
        self.results = 'mandelproc-%d.dat' % self.offset
        self.msg_q = msg_q
        Process.__init__(self, *args, **kwds)

    @classmethod
    def set_info(cls, iters, width, height, num_procs):
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

    @classmethod
    def begin_compute(cls):
        """Starts the Mandelbrot set computation."""
        if cls.ITERATIONS is None:
            raise MandelProcException("No ITERATION value set!")
        if cls.PIXWIDTH is None:
            raise MandelProcException("No PIXWIDTH value set!")
        if cls.PIXHEIGHT is None:
            raise MandelProcException("No PIXHEIGHT value set!")
        if cls.STEP is None:
            raise MandelProcException("No STEP value set!")
        
        msg_q = Queue()
        procs = [cls(i, msg_q) for i in range(cls.STEP)]
        for p in procs:
            p.start()
        return procs, msg_q

    def run(self):
        ##### Constants #####
        PIXHEIGHT = MandelProc.PIXHEIGHT
        PIXWIDTH = MandelProc.PIXWIDTH
        ITERATIONS = MandelProc.ITERATIONS
        STEP = MandelProc.STEP
        LOG2 = log(2)
        BAILRADIUS = 1 << 16
        NaN = float('NaN') # Nan is used to signal "in the set"
        msg_q = self.msg_q
        #####################

        py = self.offset
        row = array('f', (NaN for _ in xrange(PIXWIDTH)))
        results = open(self.results, 'wb')

        while py < PIXHEIGHT:
            # scale y pixel to be between 1 and -1.
            # note: pixel y axis increases as cartesian y axis decreases,
            # which is why (pixheight - py) is used.
            y0 = 2.0*(PIXHEIGHT - py)/PIXHEIGHT - 1
            px = 0
            msg_q.put('Starting work for row %d/%d'%(py,PIXHEIGHT))
            while px < PIXWIDTH:
                # scale x pixel to be between -2 and 1.
                x0 = 3.0*px/PIXWIDTH - 2

                # cardiod test
                q = (x0 - .25)**2 + y0*y0
                if q*(q + (x0 - .25)) < .25*y0*y0:
                    px = px + 1
                    continue
                    
                # period 2 bulb test
                if (x0 + 1)**2 + y0*y0 < 0.0625:
                    px = px + 1
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
                    row[px] = i

                px = px + 1
            
            # write result row to file
            row.tofile(results)
            # reset row
            for _ in xrange(PIXWIDTH):
                row[_] = NaN
                
            py += STEP
        
        msg_q.put('done')
