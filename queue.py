# coding: UTF-8

import pandas as pd
import numpy as np
from itertools import chain
from pykdtree.kdtree import KDTree

def burn():
    vertices = pd.read_pickle('./tmp/complete-vertices.pickle')

    iterc = -1

    while True:
        iterc += 1

        unburnedVertices = vertices.query('burned == False')

        if len(unburnedVertices) == 0:
            break

        if iterc % 500 == 0:
            print 'burn: ', iterc


        vertexIndex = unburnedVertices['time'].idxmin()



        vertex = vertices.loc[vertexIndex]

        if (vertex['primeSector'] != None):
            oldVal = vertex['sectorBurned']
            oldVal[vertex['primeSector']] = True
            vertices.iat[vertexIndex, vertices.columns.get_loc('sectorBurned')] = oldVal

        for i, sector in enumerate(vertex['sectors']):
            # sectorへの残り本数が自分だけになっていたら燃やす

            burnFlag = False

            if vertex['sectorBurned'][i]:
                # すでに燃えている
                burnFlag = True
            elif (sector[0] == sector[-1]):
                # 一周しているタイプのもの
                burnFlag = False
            elif (len(sector) == 0):
                # 一周していないのに自分が唯一
                burnFlag = True
            else:
                # 両側の辺を共有するunburnedなsectorがいるかどうか
                firstOK = False
                lastOK = False
                for j, _sector in enumerate(vertex['sectors']):
                    if (i == j):
                        continue
                    if (_sector[0] == sector[0]) and not vertex['sectorBurned'][j]:
                        firstOK = True
                    if (_sector[-1] == sector[-1]) and not vertex['sectorBurned'][j]:
                        lastOK = True
                if (firstOK and lastOK):
                    burnFlag = False
                else:
                    burnFlag = True

            if burnFlag:
                sectorBurned = vertex['sectorBurned']
                sectorBurned[i] = True

                sectorTime = vertex['sectorTime']
                sectorTime[i] = vertex['time']

                sectorPrimeArc = vertex['sectorPrimeArc']
                sectorPrimeArc[i] = None

                vertices.iat[vertexIndex, vertices.columns.get_loc('sectorBurned')] = sectorBurned
                vertices.iat[vertexIndex, vertices.columns.get_loc('sectorTime')] = sectorTime

                vertices.iat[vertexIndex, vertices.columns.get_loc('sectorPrimeArc')] = sectorPrimeArc

        unburnedSectorIndexes = [i for i, x in enumerate(vertex['sectorBurned']) if not x]
        unburnedSectors = [vertex['sectors'][i] for i in unburnedSectorIndexes if True]
        
        if (len(unburnedSectors) == 0):
            vertices.iat[vertexIndex, vertices.columns.get_loc('burned')] = True

            endNodes = list(chain.from_iterable(vertex['sectors']))

            for endNodeIndex in endNodes:
                endNode = vertices.loc[endNodeIndex]
                endNodeSectors = endNode['sectors']
                sectorIdx = None

                for idx, ens in enumerate(endNodeSectors):
                    if vertexIndex in ens:
                        sectorIdx = idx
                        break

                if sectorIdx == None:
                    raise 'sector not found'
    
                sectorBurned = endNode['sectorBurned'][sectorIdx]

                if not endNode['burned'] and not sectorBurned:
                    here = endNode.values[:3].reshape([1, 3]).astype(np.float32)
                    there = vertex.values[:3].reshape([1, 3]).astype(np.float32)
                    length = np.linalg.norm(here - there)

                    h = length + vertex['time']

                    endNodeSectorTime = endNode['sectorTime'][sectorIdx]

                    if h < endNodeSectorTime:
                        oldVals = endNode['sectorTime']
                        oldVals[sectorIdx] = h

                        vertices.iat[endNodeIndex, vertices.columns.get_loc('sectorTime')] = oldVals

                        oldPrimeArcs = endNode['sectorPrimeArc']
                        oldPrimeArcs[sectorIdx] = vertexIndex

                        vertices.iat[endNodeIndex, vertices.columns.get_loc('sectorPrimeArc')] = oldPrimeArcs

                        if h < endNode['time']:
                            vertices.iat[endNodeIndex, vertices.columns.get_loc('time')] = h
                            vertices.iat[endNodeIndex, vertices.columns.get_loc('primeSector')] = sectorIdx

        else:
            unburnedSectorTimes = [vertex['sectorTime'][i] for i in unburnedSectorIndexes if True]
            minVal = min(unburnedSectorTimes)
            vertices.iat[vertexIndex, vertices.columns.get_loc('time')] = minVal
            vertices.iat[vertexIndex, vertices.columns.get_loc('primeSector')] = unburnedSectorTimes.index(minVal)

    vertices.to_pickle('./tmp/burned-vertices.pickle')

        
if __name__ == '__main__':
    burn()