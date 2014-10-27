#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.DEBUG)

import struct
import sys
import time
import turtle

import bmp as bmp

TRY = 'Heisenberg-Weeds-and-Breaking-Bad.Monochrome.bmp'

def draw_it(data_lines):

    t = turtle.Pen()
    t.hideturtle()
    t.tracer(delay=1000)
    t.speed(0)
    logging.debug('Turtle speed: %d' % t.speed())
    t.lt( 90)
    t.fd(  1)
    t.rt( 90)
    frwd = 1 # Start with going right (-1 for left)

    for y in xrange(2, len(data_lines), 3):
        draw = 0 # Start with black
        cnts = data_lines[y]
        for segment in cnts if frwd else reversed(cnts):
            if draw == 0:
                for pixel in range(segment):
                    t.fd(  1)
                    t.lt( 90)
                    t.fd(  1)
                    t.bk(  2)
                    t.fd(  1)
                    t.rt( 90)
            else:
                t.fd(segment)
            draw = not draw
        if frwd:
            t.lt( 90)
            t.fd(  3)
            t.lt( 90)
        else:
            t.rt( 90)
            t.fd(  3)
            t.rt( 90)
        frwd = not frwd
    time.sleep(86400)
    del(t)

def main():
    ers = 0

    raw = bmp.get_bmp(TRY)
    dat = bmp.get_dat(raw)
    out = draw_it(dat)
    # turtle_example()
    # turtle_try(bmp1)

    return ers

def turtle_example():
    t = turtle.Pen()
    t.fd(50)
    time.sleep(1)
    del(t)

def turtle_try(bmp1):
    pass

if __name__ == '__main__':
    sys.exit(main())
