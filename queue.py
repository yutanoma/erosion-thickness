import pandas as pd
import numpy as np
from pykdtree.kdtree import KDTree

def burn():
    point_kd_tree = KDTree(original_data['coords'])

    vertices = pd.read_pickle('./tmp/vertices.pickle')

    def getTime(idx):
        if vertices[idx, 'time'] == 0:
            here = np.ndarray([row[0], row[1], row[2]])
            neighbor = point_kd_tree.query(here)
            return np.linalg.norm(here - neighbor)
        else:
            return row['sectorPrimeArc']

    vertices.loc[:, 'time'] = vertices.index.map(getTime)

    while True:
        vertexIndex = vertices['time'].idxmin()
