"""
Defines the abstract class BasicWood, class Wire and class Support.
"""

from abc import abstractmethod
from openalea.plantgl.all import *
import copy
import numpy as np
from openalea.plantgl.scenegraph.cspline import CSpline
import random as rd

import collections
eps = 1e-6

from abc import ABC, abstractmethod
# class Tree():
#   #branch_dict = {}
#   trunk_dict = {}
#   """ This class will have all the parameters required to grow the tree, i.e. the transition
#   prob, max trunk length, max branch length etc. Each tree will have its own children branch and trunk classes """
#   def __init__(self):
#     self.trunk_num_buds_segment = 5
#     self.branch_num_buds_segment = 5
#     self.trunk_bud_break_prob = 0.5
#     self.branch_bud_break_prob = 0.5
#     self.num_branches = 0
#     self.num_trunks = 0
    
    
# # BRANCH AND TRUNK SUBCLASS OF WOOD		

class BasicWood(ABC):

  @staticmethod
  def clone(obj):
    try:
        return copy.deepcopy(obj)
    except copy.Error:
        raise copy.Error(f'Not able to copy {obj}') from None

  def __init__(self, copy_from = None, max_buds_segment: int = 5, thickness: float = 0.1,\
               thickness_increment: float = 0.01, growth_length: float = 1., max_length: float = 7.,\
               tie_axis: list = (0,1,1),  order: int = 0, color: int = 0, material = 0, name: str = None):#,\
               #bud_break_prob_func: "Function" = lambda x,y: rd.random()):
                 
    #Location variables
    if copy_from:
      self.__copy_constructor__(copy_from)
      return
    self.start = Vector3(0,0,0)
    self.end = Vector3(0,0,0)
    #Tying variables    
    self.last_tie_location = Vector3(0,0,0)
    self.has_tied = False
    self.guide_points = []
    self.current_tied = False
    self.guide_target = -1#Vector3(0,0,0)
    self.tie_axis = tie_axis
    self.tie_updated = False
    #Information Variables
    self.__length = 0    
    self.age = 0    
    self.cut = False
    self.prunable = True
    self.order = order
    self.num_branches = 0
    self.branch_dict = collections.deque()
    self.color = color
    self.material = material
    #Growth Variables
    self.max_buds_segment = max_buds_segment
    self.thickness = thickness
    self.thickness_increment = thickness_increment
    self.growth_length = growth_length
    self.max_length = max_length
    
    
    
  def __copy_constructor__(self, copy_from):
    update_dict = copy.deepcopy(copy_from.__dict__)
    for k,v in update_dict.items():
      setattr(self, k, v)
    #self.__dict__.update(update_dict)
    
  @abstractmethod
  def is_bud_break(self) -> bool:
    """This method defines if a bud will break or not -> returns true for yes, false for not. Input can be any variables"""
    pass
    #Example
    # prob_break = self.bud_break_prob_func(num_buds, self.num_buds_segment)
    # #Write dummy probability function 
    # if prob_break > self.bud_break_prob:
    #   return True
    # return False
  
  @abstractmethod
  def grow(self) -> None:
    """This method can define any internal changes happening to the properties of the class, such as reduction in thickness increment etc."""
    pass
  @property
  def length(self):
    return self.__length
  
  @length.setter
  def length(self, length):
    self.__length = min(length, self.max_length)
    
  def grow_one(self):
    self.age+=1
    self.length+=self.growth_length
    self.grow()
  
  @abstractmethod
  def create_branch(self) -> "BasicWood Object":
    """Returns how a new order branch when bud break happens will look like if a bud break happens"""
    pass
    #new_object = BasicWood.clone(self.branch_object)
    #return new_object
    #return BasicWood(self.num_buds_segment/2, self.bud_break_prob, self.thickness/2, self.thickness_increment/2, self.growth_length/2,\
              # self.max_length/2, self.tie_axis, self.bud_break_max_length/2, self.order+1, self.bud_break_prob_func)
    
  def update_guide(self, guide_target):
    curve = []
    self.guide_target = guide_target
    if self.guide_target == -1:
      return
    if self.has_tied == False:
      curve, i_target = self.get_control_points(self.guide_target.point, self.start , self.end, self.tie_axis)
    else:
      curve, i_target= self.get_control_points(self.guide_target.point, self.last_tie_location , self.end, self.tie_axis)
    if i_target is not None:
      self.guide_points.extend(curve)
      #self.last_tie_location = copy.deepcopy(Vector3(i_target)) #Replaced by updating location at StartEach
  
  # def tie_lstring(self, lstring, index):
  #   #Lstring is the entire lstring
  #   #Index is where wood begins
  #   spline = CSpline(self.guide_points) 
  #   if str(spline.curve()) == "nan":
  #     raise ValueError("CURVE IS NAN", self.guide_points)
  #   remove_count = 0
  #   if not self.has_tied:
  #     if lstring[index+1].name in ['&','/','SetGuide']:
  #       del(lstring[index+1])
  #       remove_count+=1
  #     self.has_tied = True
  #   if lstring[index+1].name in ['&','/','SetGuide']:
  #     del(lstring[index+1])
  #     remove_count+=1
  #   lstring.insertAt(index+1, 'SetGuide({}, {})'.format(spline.curve(stride_factor = 100), self.length))
  #   return lstring,remove_count

  def tie_lstring(self, lstring, index):
    """Insert a SetGuide(...) after position `index` in `lstring`.

    - Removes any immediate following tokens whose .name is in ('&','/','SetGuide').
    - Builds a CSpline from `self.guide_points` and inserts the curve string and length.
    Returns (lstring, removed_count).
    """
    # Nothing to do if we don't have guide points
    if not self.guide_points:
        return lstring, 0
    # Build spline and get curve representation (may raise)
    try:
        spline = CSpline(self.guide_points)
        curve_repr = spline.curve(stride_factor=100)
    except Exception as exc:
        raise ValueError("Invalid spline from guide_points") from exc

    # Defensive check for 'nan' in the curve representation (preserve original check intent)
    if "nan" in str(curve_repr):
        raise ValueError("Curve is NaN", self.guide_points)

    # Remove any immediate tokens after index that match the removal set
    removal_names = {"&", "/", "SetGuide"}
    insert_pos = index + 1
    removed_count = 0
    
    # Remove while the next token exists and matches
    while insert_pos < len(lstring) and getattr(lstring[insert_pos], "name", None) in removal_names:
        del lstring[insert_pos]
        removed_count += 1

    # Mark tied (if not already)
    if not self.has_tied:
        self.has_tied = True

    # Insert the new SetGuide token at the computed insert position
    lstring.insertAt(insert_pos, f"SetGuide({curve_repr}, {self.length})")

    return lstring, removed_count
  
  def tie_update(self):
    self.last_tie_location = copy.deepcopy(self.end)
    self.tie_updated = True

  def deflection_at_x(self,d, x, L): 
    """d is the max deflection, x is the current location we need deflection on and L is the total length"""
    return (d/2)*(x**2)/(L**3)*(3*L - x)
  #return d*(1 - np.cos(*np.pi*x/(2*L))) #Axial loading

 
  def get_control_points(self, target, start, current, tie_axis):
    """
    Compute control points for a 3D curve from branch segment to tie point on wire.
    
    Uses vector projection to determine feasibility and compute the tie point location,
    then generates a deflected curve using beam theory.
    
    Args:
        target: Wire point (x, y, z) - a point on the wire
        start: Branch segment start point (x, y, z)
        current: Branch segment end point (x, y, z)
        tie_axis: Unit direction vector of the wire (axis along which wire extends)
        
    Returns:
        tuple: (control_points, tie_point) where:
            - control_points: List of (x,y,z) tuples for curve fitting
            - tie_point: Computed tie location on wire, or None if infeasible
            
    Geometry:
        The branch, perpendicular offset to wire, and travel along wire form a right triangle:
        - Hypotenuse = branch_length (||current - start||)
        - One leg = perpendicular_distance (shortest distance from start to wire)
        - Other leg = parallel_travel (distance to travel along wire to reach it)
    """
    # Convert inputs to numpy arrays
    start_arr = np.array([start[0], start[1], start[2]], dtype=float)
    current_arr = np.array([current[0], current[1], current[2]], dtype=float)
    wire_point = np.array([target[0], target[1], target[2]], dtype=float)
    wire_axis = np.array(tie_axis, dtype=float)
    
    # Normalize wire axis to unit vector
    wire_axis_norm = np.linalg.norm(wire_axis)
    if wire_axis_norm < eps:
      return [], None
    wire_axis_unit = wire_axis / wire_axis_norm
    
    # Calculate branch segment length
    segment_vector = current_arr - start_arr
    branch_length = np.linalg.norm(segment_vector)
    if branch_length < eps:
      return [], None  # Degenerate segment
    
    # Vector from branch start to wire point
    v = wire_point - start_arr
    
    # Decompose v into components parallel and perpendicular to wire axis
    parallel_component, perpendicular_component = self._get_parallel_and_perpendicular_components(v, wire_axis_unit)
    perpendicular_distance = np.linalg.norm(perpendicular_component)
    
    # Feasibility check: branch must be long enough to reach the wire
    if perpendicular_distance > branch_length:
      return [], None
    
    # Calculate distance to travel along wire (Pythagorean theorem)
    # branch_length² = perpendicular_distance² + parallel_travel²
    parallel_travel_sq = branch_length**2 - perpendicular_distance**2
    parallel_travel = np.sqrt(max(0.0, parallel_travel_sq))  # Clamp to avoid floating-point negatives
    
    # Compute tie point on wire
    # Start from perpendicular projection of start onto wire, then move parallel_travel along wire
    start_projection_on_wire = start_arr + perpendicular_component
    tie_point = start_projection_on_wire + parallel_travel * wire_axis_unit
    
    # Generate control points along deflected curve using beam deflection formula
    control_points = self._generate_deflected_curve(start_arr, current_arr, tie_point)
    
    return control_points, tuple(tie_point)

  def _generate_deflected_curve(self, start, current, tie_point):
    control_points = []
    deflection_vector = np.array(tie_point) - np.array(current)
    branch_length = np.linalg.norm(np.array(current) - np.array(start))
    for step in np.arange(0.1, 1.1, 0.1):
      # Parametric position along branch segment [0.1, 0.2, ..., 1.0]
      t = step
      
      # Base position: linear interpolation from start to current
      base_position = start + t * (current - start)

      # Add beam deflection (cantilever formula)
      deflection = self.deflection_at_x(deflection_vector, t * branch_length, branch_length)
      
      # Combine base position and deflection
      point = tuple(base_position + deflection)
      control_points.append(point)
    return control_points

  def _get_parallel_and_perpendicular_components(self, vec_a, vec_b):
    # Project vec_a onto vec_b to get parallel and perpendicular components
    vec_b_unit = vec_b / np.linalg.norm(vec_b)
    parallel_component = np.dot(vec_a, vec_b_unit) * vec_b_unit
    perpendicular_component = vec_a - parallel_component
    return parallel_component, perpendicular_component
  
  
      
# class Branch(BasicWood):
#   def __init__(self, num_buds_segment: int = 5, bud_break_prob: float = 0.8, thickness: float = 0.1,\
#                thickness_increment: float = 0.01, growth_length: float = 1., max_length: float = 7.,\
#                tie_axis: tuple = (0,1,1), bud_break_max_length: int = 5, order: int = 0, bud_break_prob_func: "Function" = lambda x,y: rd.random()):
#     super().__init__(num_buds_segment, bud_break_prob, thickness, thickness_increment, growth_length,\
#                max_length, tie_axis, bud_break_max_length, order, bud_break_prob_func)
    
    
# class Trunk(BasicWood):
#   """ Details of the trunk while growing a tree, length, thickness, where to attach them etc """
#   def __init__(self, num_buds_segment: int = 5, bud_break_prob: float = 0.8, thickness: float = 0.1,\
#                thickness_increment: float = 0.01, growth_length: float = 1., max_length: float = 7.,\
#                tie_axis: tuple = (0,1,1), bud_break_max_length: int = 5, order: int = 0, bud_break_prob_func: "Function" = lambda x,y: rd.random()):
#      super().__init__(num_buds_segment, bud_break_prob, thickness, thickness_increment, growth_length,\
#                max_length, tie_axis, bud_break_max_length, order, bud_break_prob_func)

from dataclasses import dataclass
from typing import Tuple

@dataclass
class Wire:
    # All wires are horizontal, tying axis depends on wood definition
    id: int
    point: Tuple[float,float,float]  
    num_branch: int = 0

    def add_branch(self):
        self.num_branch += 1

class Support():
  """ All the details needed to figure out how the support is structured in the environment, it is a collection of wires"""
  def __init__(self, points: list, num_wires: int, spacing_wires: int, trunk_wire_pt: tuple,):
                  
    self.num_wires = num_wires
    self.spacing_wires = spacing_wires
    self.branch_supports = self.make_support(points)#Dictionary id:points
    self.trunk_wire = None
    if trunk_wire_pt:
      self.trunk_wire = Wire(-1, trunk_wire_pt)
      points.append(trunk_wire_pt)
      
    self.attractor_grid = Point3Grid((1,1,1),list(points))
    
    
  def make_support(self, points):
    supports = {}
    for id,pt in enumerate(points):
      supports[id] = Wire(id, pt)
    return supports
      
