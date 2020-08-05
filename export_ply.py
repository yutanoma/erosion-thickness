# coding: UTF-8

import numpy as np
import pandas as pd
from masbpy import io_npy, io_ply
import sys

def generatePly():
    vertices = pd.read_pickle('./tmp/et-vertices.pickle')

    filename = sys.argv[1]

    with open(filename) as f:
        with open('./dist/out.ply', mode='w') as f_out:
            while True:
                line = f.readline()

                f_out.write(line + '\n')

                if line.startswith("element vertex"):
				    vertexcount = line.split()[-1]

                # todo: 直す
                if line.startswith('property float nz'):
                    f_out.write('property uchar red\n')
                    f_out.write('property uchar green\n')
                    f_out.write('property uchar blue\n')
                if line.startswith("end_header"):
				    break

                if line.startswith("element face"):
				    facecount = line.split()[-1]

            max_value = vertices.loc[vertices['et'] != float('inf')].max()
            min_value = vertices.loc[vertices['et'] > 0].min()
            length = max_value - min_value
            median = (max_value + min_value) / 2

            def getColor(val):
                if (val > max_value or val < min_value):
                    return ('0', '0', '0')
                if (val > median):
                    prop = (val - median) * 2 / length
                    red = round(255 * (1 - prop))
                    green = round(255 * prop)
                    return (str(red), str(green), '0')
                else:
                    prop = (median - val) * 2 / length
                    blue = round(255 * (1 - prop))
                    green = round(255 * prop)
                    return ('0', str(green), str(blue))

            for i in xrange(int(vertexcount)):
                if i % 500 == 0:
                    print 'vertex:', i
                text = f.readline()

                vertex = vertices.loc[i]

                et = vertex['et']

                print et

                r, g, b = getColor(et)

                f_out.write(text + ' ' + r + ' ' + g + ' ' + b + '\n')

            for j in xrange(int(facecount)):
                if j % 500 == 0:
                    print 'face:', j
                text = f.readline()
                f_out.write(text + '\n')

if __name__ == '__main__':
    generatePly()