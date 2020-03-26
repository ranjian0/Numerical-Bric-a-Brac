"""
@author: Vincent Bonnet
@description : Kinematic object describes animated objects
"""

import math
import numpy as np
from lib.common import Shape
import lib.common.jit.geometry_2d as geo

class Kinematic:
    '''
    Kinematic describes an animated object
    '''
    class ParametricPoint:
        __slots__  = ['index', 't']

        def __init__(self, index : int, t : float):
            self.index = index # simplex index
            self.t = t # parametrix value

    class State:
        '''
        State of a kinematic object
        '''
        def __init__(self, position, rotation):
            self.position = np.zeros(2)
            self.rotation = np.float(0.0)
            self.linear_velocity = np.zeros(2)
            self.angular_velocity = np.float(0.0)
            self.rotation_matrix = np.zeros((2,2))
            self.inverse_rotation_matrix = np.zeros((2,2))
            self.update_matrices(position, rotation)

        def update_velocities(self, position = (0.0, 0.0), rotation = 0.0, dt = 0.0):
            '''
            Updates the state
            '''
            # Updates linear and angular velocity
            if dt > 0.0:
                inv_dt = 1.0 / dt
                self.linear_velocity = np.subtract(position, self.position) * inv_dt
                shortest_angle = (rotation - self.rotation) % 360.0
                if (math.fabs(shortest_angle) > 180.0):
                    shortest_angle -= 360.0
                    self.angular_velocity = shortest_angle * inv_dt

        def update_matrices(self, position = (0.0, 0.0), rotation = 0.0):
            # Updates position and rotation
            self.position = np.asarray(position)
            self.rotation = np.float(rotation)

            # Update rotation matrices
            theta = np.radians(self.rotation)
            c, s = np.cos(theta), np.sin(theta)
            self.rotation_matrix = np.array(((c, -s), (s, c)))

            c, s = np.cos(-theta), np.sin(-theta)
            self.inverse_rotation_matrix = np.array(((c, -s), (s, c)))

    def __init__(self, details, shape, position = (0., 0.), rotation = 0.):
        self.state = Kinematic.State(position = position, rotation = rotation)
        self.local_vertex = np.copy(shape.vertex)
        self.face_ids = np.copy(shape.face)
        self.surface_edge_ids, self.surface_edge_normals = shape.get_edge_surface_data()
        self.index = 0 # set after the object is added to the scene - index in the scene.kinematics[]
        self.vertex = np.copy(shape.vertex)
        self.meta_data = {} # Metadata
        self.update(position, rotation)

    def set_indexing(self, index):
        self.index = index

    def get_as_shape(self):
        shape = Shape(len(self.vertex), len(self.surface_edge_ids), len(self.face_ids))
        np.copyto(shape.vertex, self.vertex)
        np.copyto(shape.edge, self.surface_edge_ids)
        np.copyto(shape.face, self.face_ids)
        return shape

    def update(self, position, rotation, dt = 0.0):
        # Update state
        self.state.update_velocities(position, rotation, dt)
        self.state.update_matrices(position, rotation)
        # Update vertices
        np.matmul(self.local_vertex, self.state.rotation_matrix, out=self.vertex)
        np.add(self.vertex, self.state.position, out=self.vertex)

    def get_closest_parametric_value(self, point):
        '''
        Returns a pair [edgeId, line parameter (t)] which define
        the closest point on the convex hull
        '''
        edge_id, edge_t = geo.get_closest_parametric_value(point, self.vertex, self.surface_edge_ids)
        return Kinematic.ParametricPoint(edge_id, edge_t)

    def get_position_from_parametric_point(self, param):
        edge_vtx = np.take(self.vertex, self.surface_edge_ids[param.index], axis=0)
        return edge_vtx[0] * (1.0 - param.t) + edge_vtx[1] * param.t

    def get_normal_from_parametric_point(self, param):
        return self.surface_edge_normals[param.index]

    def is_inside(self, point):
        '''
        Returns whether or not the point is inside the kinematic
        '''
        return geo.is_inside(point, self.vertex, self.face_ids)

