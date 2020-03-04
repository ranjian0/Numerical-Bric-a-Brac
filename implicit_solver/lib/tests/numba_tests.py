"""
@author: Vincent Bonnet
@description : Unit tests to evaluate Numba capabilities
"""

import numba
import unittest
import numpy as np
import lib.common as common

class ComponentTest:

    def __init__(self):
        self.field_0 = np.float64(0.5)
        self.field_1 = np.ones((2, 2), dtype = np.int64)

def create_datablock(num_elements, block_size = 100):
    datablock = common.DataBlock(ComponentTest, block_size, dummy_block=False)
    datablock.initialize(num_elements)
    return datablock

@numba.njit
def create_block_data(block_dtype, num_elements):
    block_data = np.zeros(1, dtype=block_dtype)
    item = block_data[0]
    item.field_0[:] = np.float64(0.5)
    item.field_1[:] = np.ones((2, 2), dtype = np.int64)
    item['blockInfo_numElements'] = num_elements
    item['blockInfo_active'] = True
    return block_data

@numba.njit
def create_typed_list(block_dtype, num_blocks):
    array = numba.typed.List()
    for _ in range(num_blocks):
        block_data = create_block_data(block_dtype, num_elements=10)
        array.append(block_data)
    return array

class Tests(unittest.TestCase):
    def test_typed_list(self):
        datablock = create_datablock(num_elements = 0, block_size = 100)
        block_dtype = datablock.get_block_dtype()
        blocks = create_typed_list(block_dtype, num_blocks = 15)
        block_data = blocks[0]
        item = block_data[0]
        componentTest = ComponentTest()

        self.assertEqual(len(blocks), 15)
        self.assertEqual(item['blockInfo_numElements'], 10)
        self.assertEqual(item['blockInfo_active'], True)
        self.assertTrue(item['field_0'][0] == componentTest.field_0)
        self.assertTrue((item['field_1'][0] == componentTest.field_1).all())

    def setUp(self):
        print(" Numba Test:", self._testMethodName)

if __name__ == '__main__':
    unittest.main(Tests())
