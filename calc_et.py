# coding: UTF-8

import numpy as np
import pandas as pd
from pykdtree.kdtree import KDTree
from masbpy import io_npy, io_ply
import sys

def calcEt(original_data):
    point_kd_tree = KDTree(original_data['coords'])

    vertices = pd.read_pickle('./tmp/burned-vertices.pickle')

    def getEt(row):
        index = row['index']

        if index % 500 == 0:
            print 'et:', index

        time = row['time']
        
        here = row.values[:3].reshape([1, 3]).astype(np.float32)
        neighbor, idx = point_kd_tree.query(here, k=3)

        radii = np.linalg.norm(here - neighbor)

        return time - radii


    vertices.loc[:, 'et'] = vertices.apply(getEt, axis=1)

    vertices.to_pickle('./tmp/et-vertices.pickle')

if __name__ == '__main__':
    original_data = io_ply.read_ply(sys.argv[1])
    calcEt(original_data)
