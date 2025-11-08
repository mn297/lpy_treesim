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
    self.location = LocationState()
    #Tying variables    
    self.tying = TyingState(tie_axis=tie_axis)
    self.current_tied = False
    #Information Variables
    self.info = InfoState(order=order, color=color, material=material)
    self.__length = 0
    #Growth Variables
    self.growth = GrowthState(
        max_buds_segment=max_buds_segment,
        thickness=thickness,
        thickness_increment=thickness_increment,
        growth_length=growth_length,
        max_length=max_length
    )
    
    
    
  def __copy_constructor__(self, copy_from):
    update_dict = copy.deepcopy(copy_from.__dict__)
    for k,v in update_dict.items():
      setattr(self, k, v)
    #self.__dict__.update(update_dict)
  
  # ===== Location property accessors for backward compatibility =====
  @property
  def start(self):
    """Get the start location."""
    return self.location.start
  
  @start.setter
  def start(self, value):
    """Set the start location."""
    self.location.start = value
  
  @property
  def end(self):
    """Get the end location."""
    return self.location.end
  
  @end.setter
  def end(self, value):
    """Set the end location."""
    self.location.end = value
  
  @property
  def last_tie_location(self):
    """Get the last tie location."""
    return self.location.last_tie_location
  
  @last_tie_location.setter
  def last_tie_location(self, value):
    """Set the last tie location."""
    self.location.last_tie_location = value
  
  # ===== Tying property accessors for backward compatibility =====
  @property
  def has_tied(self):
    """Get whether this wood object has been tied."""
    return self.tying.has_tied
  
  @has_tied.setter
  def has_tied(self, value):
    """Set whether this wood object has been tied."""
    self.tying.has_tied = value
  
  @property
  def guide_points(self):
    """Get the guide control points list."""
    return self.tying.guide_points
  
  @guide_points.setter
  def guide_points(self, value):
    """Set the guide control points list."""
    self.tying.guide_points = value
  
  @property
  def guide_target(self):
    """Get the guide target (Wire object or -1)."""
    return self.tying.guide_target
  
  @guide_target.setter
  def guide_target(self, value):
    """Set the guide target."""
    self.tying.guide_target = value
  
  @property
  def tie_axis(self):
    """Get the tie axis direction vector."""
    return self.tying.tie_axis
  
  @tie_axis.setter
  def tie_axis(self, value):
    """Set the tie axis direction vector."""
    self.tying.tie_axis = value
  
  @property
  def tie_updated(self):
    """Get whether the tie has been updated."""
    return self.tying.tie_updated
  
  @tie_updated.setter
  def tie_updated(self, value):
    """Set whether the tie has been updated."""
    self.tying.tie_updated = value
  
  # ===== Growth property accessors for backward compatibility =====
  @property
  def max_buds_segment(self):
    """Get the maximum buds per segment."""
    return self.growth.max_buds_segment
  
  @max_buds_segment.setter
  def max_buds_segment(self, value):
    """Set the maximum buds per segment."""
    self.growth.max_buds_segment = value
  
  @property
  def thickness(self):
    """Get the current thickness."""
    return self.growth.thickness
  
  @thickness.setter
  def thickness(self, value):
    """Set the current thickness."""
    self.growth.thickness = value
  
  @property
  def thickness_increment(self):
    """Get the thickness increment per step."""
    return self.growth.thickness_increment
  
  @thickness_increment.setter
  def thickness_increment(self, value):
    """Set the thickness increment per step."""
    self.growth.thickness_increment = value
  
  @property
  def growth_length(self):
    """Get the growth length per step."""
    return self.growth.growth_length
  
  @growth_length.setter
  def growth_length(self, value):
    """Set the growth length per step."""
    self.growth.growth_length = value
  
  @property
  def max_length(self):
    """Get the maximum total length."""
    return self.growth.max_length
  
  @max_length.setter
  def max_length(self, value):
    """Set the maximum total length."""
    self.growth.max_length = value
  
  # ===== Info property accessors for backward compatibility =====
  @property
  def age(self):
    """Get the age of this wood object."""
    return self.info.age
  
  @age.setter
  def age(self, value):
    """Set the age of this wood object."""
    self.info.age = value
  
  @property
  def cut(self):
    """Get whether this wood object has been cut."""
    return self.info.cut
  
  @cut.setter
  def cut(self, value):
    """Set whether this wood object has been cut."""
    self.info.cut = value
  
  @property
  def prunable(self):
    """Get whether this wood object is prunable."""
    return self.info.prunable
  
  @prunable.setter
  def prunable(self, value):
    """Set whether this wood object is prunable."""
    self.info.prunable = value
  
  @property
  def order(self):
    """Get the hierarchical order of this wood object."""
    return self.info.order
  
  @order.setter
  def order(self, value):
    """Set the hierarchical order of this wood object."""
    self.info.order = value
  
  @property
  def num_branches(self):
    """Get the number of branches from this wood object."""
    return self.info.num_branches
  
  @num_branches.setter
  def num_branches(self, value):
    """Set the number of branches from this wood object."""
    self.info.num_branches = value
  
  @property
  def branch_dict(self):
    """Get the branch dictionary/deque."""
    return self.info.branch_dict
  
  @branch_dict.setter
  def branch_dict(self, value):
    """Set the branch dictionary/deque."""
    self.info.branch_dict = value
  
  @property
  def color(self):
    """Get the color code for this wood object."""
    return self.info.color
  
  @color.setter
  def color(self, value):
    """Set the color code for this wood object."""
    self.info.color = value
  
  @property
  def material(self):
    """Get the material code for this wood object."""
    return self.info.material
  
  @material.setter
  def material(self, value):
    """Set the material code for this wood object."""
    self.info.material = value
    
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
  def create_branch(self):
    """Returns how a new order branch when bud break happens will look like if a bud break happens"""
    pass
    #new_object = BasicWood.clone(self.branch_object)
    #return new_object
    #return BasicWood(self.num_buds_segment/2, self.bud_break_prob, self.thickness/2, self.thickness_increment/2, self.growth_length/2,\
              # self.max_length/2, self.tie_axis, self.bud_break_max_length/2, self.order+1, self.bud_break_prob_func)
    
  def update_guide(self, guide_target):
    """Compute and append guide control points for this wood object.
    
    Args:
        guide_target: Wire object (with .point attribute) or None/-1 (no-op).
    
    Notes:
        - If infeasible (tie point cannot be reached), silently returns.
        - Appends control points incrementally to self.guide_points.
        - Uses self.start as base if not yet tied; self.last_tie_location otherwise.
    """
    self.guide_target = guide_target
    if guide_target is None or guide_target == -1:
      return
    
    # Select base point: use last tie location if already tied, otherwise start
    base_point = self.last_tie_location if self.has_tied else self.start
    
    # Compute control points and tie point in one call
    curve, tie_point = self.get_control_points(
        guide_target.point, base_point, self.end, self.tie_axis
    )
    
    # Append only if feasible (tie_point is not None)
    if tie_point is not None and curve:
      self.guide_points.extend(curve)
      # Note: last_tie_location updated at StartEach hook, not here
  
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
    direction_to_wire = np.sign(np.dot(wire_point, wire_axis_unit))
    tie_point = start_projection_on_wire + parallel_travel * wire_axis_unit * direction_to_wire
    
    
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
  

from dataclasses import dataclass
from typing import Tuple

@dataclass
class LocationState:
    """Location tracking for a wood object: start point, end point, and last tie location."""
    start: any = None  # Vector3
    end: any = None    # Vector3
    last_tie_location: any = None  # Vector3
    
    def __post_init__(self):
        """Initialize Vector3 points if not provided."""
        if self.start is None:
            self.start = Vector3(0, 0, 0)
        if self.end is None:
            self.end = Vector3(0, 0, 0)
        if self.last_tie_location is None:
            self.last_tie_location = Vector3(0, 0, 0)

@dataclass
class TyingState:
    """Tying and guiding state for a wood object."""
    has_tied: bool = False
    guide_points: list = None  # List of (x,y,z) tuples for spline control points
    guide_target: any = -1  # Wire object or -1 (no target)
    tie_axis: tuple = (0, 1, 1)  # Direction vector for the wire axis
    tie_updated: bool = False
    
    def __post_init__(self):
        """Initialize guide_points as empty list if not provided."""
        if self.guide_points is None:
            self.guide_points = []

@dataclass
class GrowthState:
    """Growth parameters for a wood object."""
    max_buds_segment: int = 5
    thickness: float = 0.1
    thickness_increment: float = 0.01
    growth_length: float = 1.0
    max_length: float = 7.0

@dataclass
class InfoState:
    """Information/metadata for a wood object."""
    age: int = 0
    cut: bool = False
    prunable: bool = True
    order: int = 0
    num_branches: int = 0
    color: int = 0
    material: int = 0
    branch_dict: any = None  # collections.deque
    
    def __post_init__(self):
        """Initialize branch_dict if not provided."""
        if self.branch_dict is None:
            self.branch_dict = collections.deque()

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
      
