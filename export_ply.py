# coding: UTF-8

import numpy as np
import pandas as pd
from masbpy import io_npy, io_ply
import sys

def generatePly():
    vertices = pd.read_pickle('./tmp/et-vertices.pickle')

    filename = sys.argv[1]
    threshold_mode = True
    # threshold_mode = False

    with open(filename) as f:
        with open('./dist/out.ply', mode='w') as f_out:
            while True:
                line = f.readline()

                f_out.write(line)

                if line.startswith("element vertex"):
				    vertexcount = line.split()[-1]

                # todo: 直す
                if line.startswith('property float nz'):
                    f_out.write('property uchar red\n')
                    f_out.write('property uchar green\n')
                    f_out.write('property uchar blue\n')
                    f_out.write('property uchar alpha\n')
                if line.startswith("end_header"):
				    break

                if line.startswith("element face"):
				    facecount = line.split()[-1]

            max_value = vertices.loc[vertices['et'] != float('inf')].max()['et']
            min_value = vertices.loc[vertices['et'] > 0].min()['et']

            print min_value, max_value

            length = max_value - min_value
            median = (max_value + min_value) / 2

            def getColor(val):
                if (val > max_value or val < min_value):
                    return ('0', '0', '0', '0')
                if (threshold_mode and (max_value * 0.2 + min_value * 0.8) > val):
                    return ('0', '0', '0', '0')
                if (val > median):
                    prop = (val - median) * 2 / length
                    red = int(round(255 * prop))
                    green = int(round(255 * (1 - prop)))
                    return (str(red), str(green), '0', '1')
                else:
                    prop = (median - val) * 2 / length
                    blue = int(round(255 * prop))
                    green = int(round(255 * (1 - prop)))
                    return ('0', str(green), str(blue), '1')

            for i in xrange(int(vertexcount)):
                if i % 500 == 0:
                    print 'vertex:', i
                line = f.readline()

                vertex = vertices.loc[i]

                et = vertex['et']

                r, g, b, a = getColor(et)

                f_out.write(line.replace('\n','') + ' ' + r + ' ' + g + ' ' + b + ' ' + a + '\n')

            for j in xrange(int(facecount)):
                if j % 500 == 0:
                    print 'face:', j
                text = f.readline()
                f_out.write(text)

if __name__ == '__main__':
    generatePly()