"""
@author: Vincent Bonnet
@description : Area constraint helper functions
"""

import numpy as np
import numba
import lib.common.jit.math_2d as math2D

@numba.njit
def elastic_area_anergy(x0, x1, x2, rest_area, stiffness):
    area = math2D.area(x0, x1, x2)
    return 0.5 * stiffness * ((area - rest_area)**2)

@numba.njit
def elastic_area_forces(x0, x1, x2, rest_area, stiffness, enable_force = (True, True, True)):
    forces = np.zeros((3, 2))

    u = x0 - x1
    v = x1 - x2
    w = x0 - x2
    det = u[0]*w[1] - w[0]*u[1]

    if enable_force[0] or enable_force[1]:
        forces[0][0] = v[1]
        forces[0][1] = v[0] * -1.0
        forces[0] *= 0.5*stiffness*(rest_area - 0.5*np.abs(det))*np.sign(det)

    if enable_force[2] or enable_force[1]:
        forces[2][0] = u[1]
        forces[2][1] = u[0] * -1.0
        forces[2] *= 0.5*stiffness*(rest_area - 0.5*np.abs(det))*np.sign(det)

    if enable_force[1]:
        forces[1] -= (forces[0] + forces[2])

    return forces

@numba.njit
def elastic_area_numerical_jacobians(x0, x1, x2, rest_area, stiffness):
    '''
    Returns the six jacobians matrices in the following order
    df0dx0, df1dx1, df2dx2, df0dx1, df0dx2, df1dx2
    dfdx01 is the derivative of f0 relative to x1
    etc.
    '''
    jacobians = np.zeros(shape=(6, 2, 2))
    STENCIL_SIZE = 1e-6

    # derivate of f0 relative to x0
    for g_id in range(2):
        x0_ = math2D.copy(x0)
        x0_[g_id] = x0[g_id]+STENCIL_SIZE
        forces = elastic_area_forces(x0_, x1, x2, rest_area, stiffness, (True, False, False))
        grad_f0_x0 = forces[0]
        x0_[g_id] = x0[g_id]-STENCIL_SIZE
        forces = elastic_area_forces(x0_, x1, x2, rest_area, stiffness, (True, False, False))
        grad_f0_x0 -= forces[0]
        grad_f0_x0 /= (2.0 * STENCIL_SIZE)
        jacobians[0, 0:2, g_id] = grad_f0_x0

    # derivate of f0, f1 relative to x1
    for g_id in range(2):
        x1_ = math2D.copy(x1)
        x1_[g_id] = x1[g_id]+STENCIL_SIZE
        forces = elastic_area_forces(x0, x1_, x2, rest_area, stiffness, (True, True, False))
        grad_f0_x1 = forces[0]
        grad_f1_x1 = forces[1]
        x1_[g_id] = x1[g_id]-STENCIL_SIZE
        forces = elastic_area_forces(x0, x1_, x2, rest_area, stiffness, (True, True, False))
        grad_f0_x1 -= forces[0]
        grad_f1_x1 -= forces[1]
        jacobians[1, 0:2, g_id] = grad_f1_x1 / (2.0 * STENCIL_SIZE)
        jacobians[3, 0:2, g_id] = grad_f0_x1 / (2.0 * STENCIL_SIZE)

    # derivate of f0, f1, f2 relative to x2
    for g_id in range(2):
        x2_ = math2D.copy(x2)
        x2_[g_id] = x2[g_id]+STENCIL_SIZE
        forces = elastic_area_forces(x0, x1, x2_, rest_area, stiffness, (True, True, True))
        grad_f0_x2 = forces[0]
        grad_f1_x2 = forces[1]
        grad_f2_x2 = forces[2]
        x2_[g_id] = x2[g_id]-STENCIL_SIZE
        forces = elastic_area_forces(x0, x1, x2_, rest_area, stiffness, (True, True, True))
        grad_f0_x2 -= forces[0]
        grad_f1_x2 -= forces[1]
        grad_f2_x2 -= forces[2]
        jacobians[4, 0:2, g_id] = grad_f0_x2 / (2.0 * STENCIL_SIZE)
        jacobians[5, 0:2, g_id] = grad_f1_x2 / (2.0 * STENCIL_SIZE)
        jacobians[2, 0:2, g_id] = grad_f2_x2 / (2.0 * STENCIL_SIZE)

    return jacobians