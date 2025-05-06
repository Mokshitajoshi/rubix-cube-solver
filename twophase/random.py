import random
import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from twophase.cubes.cubiecube import CubieCube
from twophase.tables import Tables


def random_cube():
    cc = CubieCube()
    cc.flip = random.randint(0, Tables.FLIP)
    cc.twist = random.randint(0, Tables.TWIST)
    while True:
        cc.corner = random.randint(0, Tables.CORNER)
        cc.edge = random.randint(0, Tables.EDGE)
        if cc.edge_parity == cc.corner_parity:
            break
    fc = cc.to_facecube()
    return fc.to_string()
