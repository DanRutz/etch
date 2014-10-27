#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.DEBUG)

import struct

class BitmapFileError(Exception):
    pass

# http://en.wikipedia.org/wiki/BMP_file_format All of the integer values are
# stored in little-endian format (i.e. least-significant byte first).
FILE_H_SIZE = 14
FILE_HEADER= {
        'offset': 0,
        'inputs': { # Offset, Size, Purpose
            'header': (  0, 2, 'the header field used to identify the BMP & DIB file is 0x42 0x4D in hexadecimal, same as BM in ASCII'),
            'filsiz': (  2, 4, 'the size of the BMP file in bytes'),
        #   'resvd0': (  6, 2, 'reserved; actual value depends on the application that creates the image'),
        #   'resvd1': (  8, 2, 'reserved; actual value depends on the application that creates the image'),
            'offset': ( 10, 4, 'the offset, i.e. starting address, of the byte where the bitmap image data (pixel array) can be found.'),
        },
        'asserts': {
            'header': ( # Entry, Description
                'BM', # Windows 3.1x, 95, NT, ... etc.
            )
        }
    }
# This is kind of messed up. It currently only supports BITMAPINFOHEADER BMPs.
INFO_HEADER = {
        'offset': 0 - FILE_H_SIZE,
        'inputs': { # Offset, Size, Purpose
            'hedsiz': ( 14, 4, 'the size of this header (40 bytes)'),
            'widpix': ( 18, 4, 'the bitmap width in pixels (signed integer)'),
            'hgtpix': ( 22, 4, 'the bitmap height in pixels (signed integer)'),
            'planes': ( 26, 2, 'the number of color planes must be 1'),
            'bperpx': ( 28, 2, 'the number of bits per pixel, which is the color depth of the image. Typical values are 1, 4, 8, 16, 24 and 32.'),
            'method': ( 30, 4, 'the compression method being used. See the next table for a list of possible values'),
            'imgsiz': ( 34, 4, 'the image size. This is the size of the raw bitmap data; a dummy 0 can be given for BI_RGB bitmaps.'),
            'horres': ( 38, 4, 'the horizontal resolution of the image. (pixel per meter, signed integer)'),
            'verres': ( 42, 4, 'the vertical resolution of the image. (pixel per meter, signed integer)'),
            'colors': ( 46, 4, 'the number of colors in the color palette, or 0 to default to 2**n'),
            'iptcol': ( 50, 4, 'the number of important colors used, or 0 when every color is important; generally ignored'),
        },
        'asserts': {
            'hedsiz': ( # Size, Header Name
                  40, # BITMAPINFOHEADER
            ),
            'bperpx': ( # Bits per Pixel
                   1, # Black and White
            ),
            'method': ( # Value, Identified by, Compression method, Comments
                   0, # BI_RGB, none, Most common
            )
        }
    }

def unpack_header(data, structure):
    head = {}

    for k, v in structure['inputs'].iteritems():
        # v[0, 1, 2] are Offset, Size, Purpose
        padding = '\x00\x00' if v[1] == 2 else ''
        offset  = v[0] + structure['offset']
        item    = data[offset: offset + v[1]]
        head[k] = item if k in ('header',) else \
                struct.unpack('<L', item + padding)[0] # little-endian

        logging.debug('Unpack headers: %s: %8s: %s' % (k, head[k], v[2]))

    for k, v in structure['asserts'].iteritems():
        assert head[k] in v

        logging.debug('Assert headers: %s: %8s: %s' % (k, head[k], v))

    return head
        
def get_bmp(nam):
    logging.debug('Get bitmap file: %s' % nam)

    with open(nam, 'rb') as f:
        file_headr = unpack_header(f.read(FILE_H_SIZE), FILE_HEADER)
        info_h_size = file_headr['offset'] - FILE_H_SIZE
        info_headr = unpack_header(f.read(info_h_size), INFO_HEADER)
        bmdata     = f.read()

    def byte_assert(msg, func, comp, a, b):
        logging.debug('Assert bytes of %s size specified: %d %s %d is %s'
                % (msg, a, comp, b, func(a,b)))
    byte_assert('info equals/exceeds', lambda a, b: a >= b, '>=',
            info_h_size, info_headr['hedsiz'])
    byte_assert('data equals image'  , lambda a, b: a == b, '==',
            len(bmdata), info_headr['imgsiz'])

    rowsiz = ((info_headr['bperpx'] * info_headr['widpix'] + 31) / 32) * 4
    logging.debug('Row size in bytes: %d' % rowsiz)

    return bmdata, rowsiz, info_headr['widpix'], info_headr['hgtpix']

def get_dat(bmdata, rowsiz, widpix, hgtpix):
    data_lines = []
    rwsz_words = rowsiz / 4

    for y in xrange(hgtpix):
        y_offset = y * rowsiz
        line = bmdata[y_offset: y_offset + rowsiz]
        bina = ''
        for x in xrange(rwsz_words):
            x_offset = x * 4
            item = struct.unpack('>L', line[x_offset: x_offset + 4])[0] # big-endian
            word = '{0:b}'.format(item)
            word = '0' * (32 - len(word)) + word
            bina += word
        bina = bina[0: widpix] # drop any padding pixels
        cnts, found, look_for = [], 0, '0'
        for char in bina:
            if char == look_for:
                found += 1
            else:
                cnts.append(found)
                found = 1
                look_for = str(int(not bool(int(look_for))))
        cnts.append(found)
        if len(cnts) % 2 == 0:
            cnts.append(0)
        data_lines.append(cnts)
        logging.debug('%s; Checksum: %d' % (cnts, sum(cnts)))

    return data_lines

