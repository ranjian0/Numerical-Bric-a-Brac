"""
@author: Vincent Bonnet
@description : Array of Structures of Arrays (AoSoA)
Example :
data = DataBlock()
data.initialize(10)
print(data.field_a)
print(data.field_b)
"""

import math
import numpy as np
import keyword
import lib.common.node_accessor as na

class DataBlock:

    def __init__(self, class_type, block_size = 100):
        # Data
        self.blocks = []
        # Data type
        self.dtype_dict = {}
        self.dtype_dict['names'] = [] # list of names
        self.dtype_dict['formats'] = [] # list of tuples (data_type, data_shape)
        self.dtype_dict['defaults'] = [] # list of default values (should match formats)
        # Block size
        self.block_size = block_size
        # Set class
        self.__set_field_from_type(class_type)

    def num_blocks(self):
        return len(self.blocks)

    def clear(self):
        '''
        Clear the data on the datablock (it doesn't reset the datatype)
        '''
        self.blocks.clear()

    def __check_before_add(self, name):
        '''
        Raise exception if 'name' cannot be added
        '''
        if keyword.iskeyword(name):
            raise ValueError("field name cannot be a keyword: " + name)

        if name in self.dtype_dict['names']:
            raise ValueError("field name already used : " + name)

    def __set_field_from_type(self, class_type):
        '''
        Add fields
        '''
        inst = class_type()
        for name, value in inst.__dict__.items():
            self.__check_before_add(name)

            data_type = None
            data_shape = None

            if np.isscalar(value):
                data_type = type(value)
                data_shape = 1
            else:
                data_type = value.dtype.type
                data_shape = value.shape

            self.dtype_dict['names'].append(name)
            self.dtype_dict['formats'].append((data_type, data_shape))
            self.dtype_dict['defaults'].append(value)

    def dtype(self, num_elements, add_block_info):
        '''
        Returns the dtype of the datablock
        add_block_info is only used for blocks
        '''
        # create a new dictionnary to create an 'array of structure of array'
        dtype_aosoa_dict = {}
        dtype_aosoa_dict['names'] = []
        dtype_aosoa_dict['formats'] = []

        for field_name in self.dtype_dict['names']:
            dtype_aosoa_dict['names'].append(field_name)

        for field_format in self.dtype_dict['formats']:
            field_type = field_format[0]
            field_shape = field_format[1]

            # modify the shape to store data as 'array of structure of array'
            # x becomes (num_elements, x)
            # (x, y, ...) becomes (num_elements, x, y, ...)
            new_field_shape = tuple()
            if np.isscalar(field_shape):
                if field_shape == 1:
                    # The coma after num_elements is essential
                    # In case field_shape == num_elements == 1,
                    # it guarantees an array will be produced and not a single value
                    new_field_shape = (num_elements,)
                else:
                    new_field_shape = (num_elements, field_shape)
            else:
                list_shape = list(field_shape)
                list_shape.insert(0, num_elements)
                new_field_shape = tuple(list_shape)

            dtype_aosoa_dict['formats'].append((field_type, new_field_shape))

        if add_block_info:
            dtype_aosoa_dict['names'].append('blockInfo_numElements')
            dtype_aosoa_dict['formats'].append(np.int64)

        return np.dtype(dtype_aosoa_dict, align=True)

    def initialize_from_array(self, array):
        '''
        Allocate the fields from the array
        SLOW but generic - need more work
        '''
        # initialize local array
        num_constraints = len(array)
        aosoa_dtype = self.dtype(num_constraints, add_block_info=False)
        data = np.zeros(1, dtype=aosoa_dtype)[0] # a scalar
        for field_index, default_value in enumerate(self.dtype_dict['defaults']):
            data[field_index][:] = default_value

        for index, element in enumerate(array):
            for attribute_name, attribute_value in element.__dict__.items():
                if attribute_name in self.dtype_dict['names']:
                    field_index = self.dtype_dict['names'].index(attribute_name)
                    data[field_index][index] =  getattr(element, attribute_name)

        # initialize and set block
        self.initialize(num_constraints)

        data_type = self.dtype(self.block_size, add_block_info=False)
        num_fields = len(data_type.names)

        for block_id, block_data in enumerate(self.blocks):

            begin_index = block_id * self.block_size
            block_n_elements = block_data['blockInfo_numElements']
            end_index = begin_index + block_n_elements

            for field_id in range(num_fields):
                np.copyto(block_data[field_id][0:block_n_elements], data[field_id][begin_index:end_index])

    def initialize(self, num_elements):
        '''
        Allocate fields inside blocks
        numpy.array_split doesn't support structured array
        '''
        self.blocks.clear()

        data_type = self.dtype(self.block_size, add_block_info=False)
        block_dtype = self.dtype(self.block_size, add_block_info=True)

        num_fields = len(data_type.names)
        if num_fields == 0:
            return

        n_blocks = math.ceil(num_elements / self.block_size)
        for block_id in range(n_blocks):

            # allocate memory and blockInfo
            block_data = np.zeros(1, dtype=block_dtype)[0] # a scalar

            begin_index = block_id * self.block_size
            block_n_elements = min(self.block_size, num_elements-begin_index)
            block_data['blockInfo_numElements'] = block_n_elements

            # set default values
            for field_id, default_value in enumerate(self.dtype_dict['defaults']):
                block_data[field_id][:] = default_value

            self.blocks.append(block_data)

    '''
    Vectorize Functions on blocks
    '''
    def compute_num_elements(self):
        num_elements = 0
        for block_data in self.blocks:
            num_elements += block_data['blockInfo_numElements']
        return num_elements

    def set_indexing(self, object_id, node_global_offset):
        object_node_id = 0
        for block_id, block_data in enumerate(self.blocks):
            block_n_elements = block_data['blockInfo_numElements']
            node_ids = block_data['ID']
            for block_node_id in range(block_n_elements):
                global_node_id = node_global_offset + object_node_id
                na.set_node_id(node_ids[block_node_id], object_id, object_node_id, global_node_id, block_id, block_node_id)
                object_node_id += 1

    def copyto(self, field_name, values):
        for block_id, block_data in enumerate(self.blocks):
            begin_index = block_id * self.block_size
            block_n_elements = block_data['blockInfo_numElements']
            end_index = begin_index + block_n_elements
            np.copyto(block_data[field_name][0:block_n_elements], values[begin_index:end_index])

    def fill(self, field_name, value):
        for block in self.blocks:
            block[field_name].fill(value)

    def flatten(self, field_name):
        '''
        Convert block of array into a single array
        '''
        field_id = self.dtype_dict['names'].index(field_name)
        field_dtype = self.dtype_dict['formats'][field_id]

        num_elements = 0
        for block_data in self.blocks:
            num_elements += block_data['blockInfo_numElements']

        result = np.empty(num_elements, field_dtype)

        for block_id, block_data in enumerate(self.blocks):

            begin_index = block_id * self.block_size
            block_n_elements = block_data['blockInfo_numElements']
            end_index = begin_index + block_n_elements

            np.copyto(result[begin_index:end_index], block_data[field_id][0:block_n_elements])

        return result
