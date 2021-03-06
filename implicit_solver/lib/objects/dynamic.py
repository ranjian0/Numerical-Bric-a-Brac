"""
@author: Vincent Bonnet
@description : Dynamic object describes simulated objects
"""

import numpy as np
import core

class Dynamic:
    '''
    Dynamic describes a simulated object
    '''
    def __init__(self, details, shape, node_mass):
        # Allocate node data
        self.total_nodes = shape.num_vertices()
        db_nodes = details.db['node']
        self.block_handles = db_nodes.append_empty(self.total_nodes)
        self.node_ids = db_nodes.flatten('ID', self.block_handles)

        # Set node data
        db_nodes.copyto('x', shape.vertex, self.block_handles)
        db_nodes.fill('v', 0.0, self.block_handles)
        db_nodes.fill('m', node_mass, self.block_handles)
        db_nodes.fill('im', 1.0 / node_mass, self.block_handles)

        # Initialize node connectivities
        self.edge_ids = np.copy(shape.edge)
        self.face_ids = np.copy(shape.face)
        # Metadata
        self.meta_data = {}

    def num_nodes(self):
        return self.total_nodes

    def num_blocks(self):
        return len(self.block_handles)

    def get_node_id(self, vertex_index):
        return self.node_ids[vertex_index]

    def get_as_shape(self, details):
        '''
        Create a simple shape from the dynamic datablock and
        node connectivities
        '''
        num_vertices = self.num_nodes()
        num_edges = len(self.edge_ids)
        num_faces = len(self.face_ids)
        shape = core.Shape(num_vertices, num_edges, num_faces)
        shape.vertex = details.db['node'].flatten('x', self.block_handles)
        shape.edge = np.copy(self.edge_ids)
        shape.face = np.copy(self.face_ids)

        return shape

    def metadata(self):
        meta_data = self.meta_data.copy()
        meta_data['num_nodes'] = self.num_nodes()
        meta_data['num_blocks'] = self.num_blocks()
        return meta_data

