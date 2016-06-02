mandelbrotG5
============

A Python 2.7 script for creating arbitrarily hi resolution images of the Mandelbrot set. It works by spawning processes that create rows of escape time values in a big shared arary. The main process starts all the workers and then iterates through the shared array, generates colors from the escape time values, and then writes the data to a file.

The code has two dependencies: pypng and numpy. 

This project is dedicated to my beautiful PowerMac G5 Quad (R.I.P.)
