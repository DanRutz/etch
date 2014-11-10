#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.DEBUG)

import struct
import sys
import time
import turtle
import easydriver as ed

import bmp as bmp

TRY = 'Heisenberg-Weeds-and-Breaking-Bad.Monochrome.bmp'

DNLT, UPRT = False, True
RT, UP, LT, DN = 0, 1, 2, 3

class Pen(object):

    def __init__(self):
        self.h = ed.easydriver(24, .0001, 25, 9, 14, 15)
        self.v = ed.easydriver(18, .0001, 23, 4, 17, 27)
        self.h.set_full_step()
        self.v.set_full_step()
        self.h.set_direction(UPRT)
        self.v.set_direction(UPRT)
        self.direction = RT

    def hideturtle(self):
        pass

    def tracer(self, **kwargs):
        pass

    def speed(self, *args):
        return 0

    def fd(self, pix):
        axis = (           self.h if self.direction in (RT, LT) else
                           self.v)
        axis.set_direction(DNLT   if self.direction in (DN, LT) else
                           UPRT  )
        for i in range(10 * pix):
            axis.step()

    def bk(self, pix):
        self.direction = (self.direction + 2) % 4
        self.fd(pix)
        self.direction = (self.direction + 2) % 4

    def rt(self, *args):
        self.direction = (self.direction + 3) % 4

    def lt(self, *args):
        self.direction = (self.direction + 1) % 4

    # Liiiindsayyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

def draw_it(data_lines):

    if False:
        t = turtle.Pen()
        h_scale, v_scale =  0, 1
    else:
        t = Pen()
        h_scale, v_scale = 12, 8
    t.hideturtle()
    t.tracer(delay=1000)
    t.speed(0)
    logging.debug('Turtle speed: %d' % t.speed())
    t.lt( 90)
    t.fd(  1)
    t.rt( 90)
    frwd = 1 # Start with going right (-1 for left)

    for y in xrange(2, len(data_lines), 3):
        t.fd(h_scale)
        draw = 0 # Start with black
        cnts = data_lines[y]
        for segment in cnts if frwd else reversed(cnts):
            if draw == 0:
                for pixel in range(segment):
                    t.fd(  1)
                    t.lt( 90)
                    t.fd(  1 * v_scale)
                    t.bk(  2 * v_scale)
                    t.fd(  1 * v_scale)
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
