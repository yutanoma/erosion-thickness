from masbpy.ma import MASB
from masbpy import io_npy, io_ply
import sys

from graph import generateGraph

def main():
    datadict = io_ply.read_ply(sys.argv[1])
    original_data = io_ply.read_ply(sys.argv[2])

    generateGraph(datadict, original_data)

if __name__ == '__main__':
    main()
