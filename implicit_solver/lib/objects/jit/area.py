"""
@author: Vincent Bonnet
@description : Constraint base for the implicit solver
"""

import numpy as np
import numba # required by lib.common.code_gen

import lib.common.jit.math_2d as math2D
import lib.common.jit.data_accessor as db
import lib.common.code_gen as generate
import lib.objects.jit.utils.area_lib as area_lib
from lib.objects.jit import Constraint

class Area(Constraint):
    '''
    Describes a 2D area constraint between three nodes
    '''
    def __init__(self):
        Constraint.__init__(self, num_nodes = 3)
        self.rest_area = np.float64(0.0)

    # initialization functions
    @classmethod
    def pre_compute(cls):
        return None

    @classmethod
    def compute_rest(cls):
        return compute_area_rest

    # constraint functions (function, gradients, hessians)
    @classmethod
    def compute_function(cls):
        return None # TODO

    @classmethod
    def compute_gradients(cls):
        return None # TODO

    @classmethod
    def compute_hessians(cls):
        return None # TODO

    # force functions (forces and their jacobians)
    @classmethod
    def compute_forces(cls):
        return compute_area_forces

    @classmethod
    def compute_force_jacobians(cls):
        return compute_area_force_jacobians

@generate.vectorize
def compute_area_rest(area : Area, detail_nodes):
    x0 = db.x(detail_nodes, area.node_IDs[0])
    x1 = db.x(detail_nodes, area.node_IDs[1])
    x2 = db.x(detail_nodes, area.node_IDs[2])
    area.rest_area = np.float64(math2D.area(x0, x1, x2))

@generate.vectorize
def compute_area_forces(area : Area, detail_nodes):
    x0 = db.x(detail_nodes, area.node_IDs[0])
    x1 = db.x(detail_nodes, area.node_IDs[1])
    x2 = db.x(detail_nodes, area.node_IDs[2])
    forces = area_lib.elastic_area_forces(x0, x1, x2, area.rest_area, area.stiffness)
    area.f[0] = forces[0]
    area.f[1] = forces[1]
    area.f[2] = forces[2]

@generate.vectorize
def compute_area_force_jacobians(area : Area, detail_nodes):
    x0 = db.x(detail_nodes, area.node_IDs[0])
    x1 = db.x(detail_nodes, area.node_IDs[1])
    x2 = db.x(detail_nodes, area.node_IDs[2])
    jacobians = area_lib.elastic_area_numerical_jacobians(x0, x1, x2, area.rest_area, area.stiffness)
    area.dfdx[0][0] = jacobians[0]
    area.dfdx[1][1] = jacobians[1]
    area.dfdx[2][2] = jacobians[2]
    area.dfdx[0][1] = area.dfdx[1][0] = jacobians[3]
    area.dfdx[0][2] = area.dfdx[2][0] = jacobians[4]
    area.dfdx[1][2] = area.dfdx[2][1] = jacobians[5]
