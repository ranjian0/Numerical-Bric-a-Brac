"""
@author: Vincent Bonnet
@description : This class provides a mapping between data identifiers and DataBlock layout
Format : [global_node_id, block_handle, block_node_id]'
This file could be auto-generated based on DataBlock
"""

import numba
import numpy as np

ID_SIZE = 2

@numba.njit
def empty_data_ids(num_nodes):
    return np.empty((num_nodes, ID_SIZE), dtype=np.int32)

@numba.njit
def empty_data_id():
    return np.empty(ID_SIZE, dtype=np.int32)

@numba.njit
def set_data_id(ID, block_handle, index):
    ID[0] = block_handle
    ID[1] = index

@numba.njit
def x(blocks, ID):
    block_handle = ID[0]
    index = ID[1]
    return blocks[block_handle][0]['x'][index]

@numba.njit
def v(blocks, ID):
    block_handle = ID[0]
    index = ID[1]
    return blocks[block_handle][0]['v'][index]

@numba.njit
def xv(blocks, ID):
    block_handle = ID[0]
    index = ID[1]

    x = blocks[block_handle][0]['x'][index]
    v = blocks[block_handle][0]['v'][index]
    return (x, v)

@numba.njit
def add_f(blocks, ID, force):
    block_handle = ID[0]
    index = ID[1]

    f = blocks[block_handle][0]['f'][index]
    f += force

@numba.njit
def systemIndex(blocks, ID):
    block_handle = ID[0]
    index = ID[1]
    return blocks[block_handle][0]['systemIndex'][index]
