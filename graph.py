# coding: UTF-8

import numpy as np
import pandas as pd
from pykdtree.kdtree import KDTree
from itertools import chain

import gc
import sys

def generateGraph(datadict, original_data):
    point_kd_tree = KDTree(original_data['coords'])

    print 'import completed.'

    faces = pd.DataFrame(np.array(datadict['faces'], dtype=np.uint32))
    faces.columns = ['col1', 'col2', 'col3']

    def getFaces(index):
        idStr = str(index)

        if (index % 500 == 0):
            print 'face: ', index

        return faces.query('col1 == ' + idStr + ' | col2 == ' + idStr + ' | col3 == ' + idStr)
    
    def getTime(obj):
        neighboringFaces = obj['faces']
        index = obj['index']

        if (index % 500 == 0):
            print 'time: ', index

        neighboringNodes = np.ravel(neighboringFaces)

        points, counts = np.unique(neighboringNodes[~(neighboringNodes == index)], return_counts=True)

        if (min(counts) <= 1):
            here = obj.values[:3].reshape([1, 3]).astype(np.float32)
            neighbor, idx = point_kd_tree.query(here, k=3)
            return np.linalg.norm(here - neighbor)
        else:
            return float('inf')

    def getSectorTime(sector):
        return [float('inf')] * len(sector)
        
    def getBurned(sector):
        return [False] * len(sector)

    def getPrimeArc(sector):
        return [None] * len(sector)
    
    def getSectors(obj):
        neighboringFaces = obj['faces']
        index = obj['index']

        if (index % 500 == 0):
            print 'sector: ', index

        neighboringNodes = np.ravel(neighboringFaces)

        points, counts = np.unique(neighboringNodes[~(neighboringNodes == index)], return_counts=True)

        if (min(counts) <= 2 and max(counts) <= 2):
            return [points]

        else:
            # 3つ以上の三角形で共有されている
            threeFaceEdges = np.where(counts >= 3)

            sectors = {}
            sectorNum = 0

            for rootEdge in threeFaceEdges[0]:
                rootId = points[rootEdge]
                rootIdStr = str(rootId)
                rootEdgeTriangles = neighboringFaces.query('col1 == ' + rootIdStr + ' | col2 == ' + rootIdStr + ' | col3 == ' + rootIdStr)

                for face in rootEdgeTriangles.itertuples():
                    indexPos = face.index(index)
                    rootIdPos = face.index(rootId)

                    neighboringEdge = face[6 - indexPos - rootIdPos]

                    tmp = neighboringEdge
                    newEdge = [rootId]

                    while True:
                        newEdge.append(tmp)
                        tmpStr = str(tmp)

                        allNeighboringEdges = np.unique(np.ravel(neighboringFaces.query('col1 == ' + tmpStr + ' | col2 == ' + tmpStr + ' | col3 == ' + tmpStr)))

                        nextEdge = allNeighboringEdges[(allNeighboringEdges != tmp) & (allNeighboringEdges != index)].tolist()

                        if (len(nextEdge) >= 3):
                            break
                        elif (len(nextEdge) == 1):
                            break
                        else:
                            # 前に戻らないようにする
                            if nextEdge[0] == newEdge[-2]:
                                tmp = nextEdge[1]
                            else:
                                tmp = nextEdge[0]

                            ## 最初に戻ってきた場合
                            if tmp == rootId:
                                # appendする
                                newEdge.append(tmp)
                                break

                    if not ((newEdge[0], newEdge[1], newEdge[-2], newEdge[-1]) in sectors or (newEdge[-1], newEdge[-2], newEdge[1], newEdge[0]) in sectors):
                        sectors[(newEdge[0], newEdge[1], newEdge[-2], newEdge[-1])] = newEdge

            sectorValues = sectors.values()

            sectorList = list(chain.from_iterable(sectors.values()))

            notIns = list(set(points.tolist()) - set(sectorList))

            if len(notIns) > 0:
                sectorValues.append(notIns)

            # print index, points, counts, a, sectors.values(), rootEdge, neighboringFaces, threeFaceEdges
                
            return sectorValues


    vertices = pd.DataFrame(datadict['coords'])

    vertices['index'] = vertices.index
    vertices['burned'] = False
    vertices['primeSector'] = None
    vertices.loc[:, 'faces'] = vertices.index.map(getFaces)
    vertices.to_pickle('./tmp/faces-vertices.pickle')

    # vertices = pd.read_pickle('./tmp/sectors-vertices.pickle')

    vertices.loc[:, 'sectors'] = vertices.apply(getSectors, axis=1)
    vertices.to_pickle('./tmp/sectors-vertices.pickle')

    print('a')

    vertices.loc[:, 'time'] = vertices.apply(getTime, axis=1)
    vertices.to_pickle('./tmp/time-vertices.pickle')

    vertices.loc[:, 'sectorTime'] = vertices.sectors.map(getSectorTime)
    vertices.loc[:, 'sectorBurned'] = vertices.sectors.map(getBurned)
    vertices.loc[:, 'sectorPrimeArc'] = vertices.sectors.map(getPrimeArc)

    vertices.to_pickle('./tmp/complete-vertices.pickle')

