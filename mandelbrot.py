import numpy as np
import png

R = np.poly1d([
    10625.3986106,
    -28392.7860511,
    25110.8741911,
    -8168.63378107,
    917.694067345,
    -9.68969369835,
])
G = np.poly1d([
    2165.7913046,
    -334.108199316,
    -4444.3438771,
    2516.57316178,
    146.487773784,
    1.89461476371,
])
B = np.poly1d([
    -731.914318985,
    -2671.97359649,
    8708.6975545,
    -7049.30845895,
    1708.99764799,
    46.1831334215,
])

def mandelbrot(iterations=10, width=600, height=400):
    i, r = np.ogrid[-1.0:1.0:height*1j, -2.0:1.0:width*1j]
    c = r+i*1j
    z = np.copy(c)
    escape_times = np.zeros((height, width), np.uint8) + iterations
    for n in np.arange(iterations, dtype=np.uint8):
        z = z*z + c
        divergant_zs = np.abs(z) > 2.0
        diverging_now = np.logical_and(divergant_zs, escape_times==iterations)
        escape_times[diverging_now] = n
        z[divergant_zs] = 0
        c[divergant_zs] = 0
    return escape_times

def color_pallete(n):
    indices = np.arange(n-1)
    indices.resize((n-1, 1))
    return np.concatenate((
    
    
    

if __name__ == '__main__':
    #print '\n'.join(''.join(' ' if np.isnan(z) else '*' for z in r) for r in mandelbrot())
    #plt.imshow(mandelbrot(40, 2400, 1600))
    #plt.savefig('mandel_1.png')
    #print is_color_like(LinearSegmentedColormap.from_list('my_colormap', ['blue','green','red'], N=40))

