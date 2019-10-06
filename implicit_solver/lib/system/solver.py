"""
@author: Vincent Bonnet
@description : Solver to orchestrate the step of a solver
"""


import lib.common as cm

class Context:
    '''
    Context to store time, time stepping, etc.
    '''
    def __init__(self, time = 0.0, frame_dt = 1.0/24.0, num_substep = 4, num_frames = 1):
        self.time = time # current time (in seconds)
        self.start_time = time # start time (in seconds)
        self.end_time = time + (num_frames * frame_dt) # end time (in seconds)
        self.frame_dt = frame_dt # time step on a single frame (in seconds)
        self.num_substep = num_substep # number of substep per frame
        self.dt = frame_dt / num_substep # simulation substep (in seconds)
        self.num_frames = num_frames # number of simulated frame (doesn't include initial frame)

class SolverDetails:
    '''
    List of datablocks - WIP
    '''
    def __init__(self):
        self.dynamics_db = [] # dynamic objects
        self.conditions_db = [] # dynamic objects

class Solver:
    '''
    Base Solver
    '''
    def __init__(self, time_integrator = None):
        self.time_integrator = time_integrator

    def initialize(self, scene, context):
        '''
        Initialize the scene
        '''
        scene.init_kinematics(context.start_time)
        scene.init_conditions()

    @cm.timeit
    def solve_step(self, scene, context):
        '''
        Solve a single step (pre/step/post)
        '''
        self._pre_step(scene, context)
        self._step(scene, context)
        self._post_step(scene, context)

    @cm.timeit
    def _pre_step(self, scene, context):
        scene.update_kinematics(context.time, context.dt)
        scene.update_conditions()

    @cm.timeit
    def _step(self, scene, context):
        # TODO : convert solver into solverDetails
        if self.time_integrator:
            self.time_integrator.prepare_system(scene, context.dt)
            self.time_integrator.assemble_system(scene, context.dt)
            self.time_integrator.solve_system(scene, context.dt)

    @cm.timeit
    def _post_step(self, scene, context):
        pass