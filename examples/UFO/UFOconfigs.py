import sys
sys.path.append('../../')
from stochastic_tree import Support, BasicWood, TreeBranch, BasicWoodConfig
import numpy as np
import random as rd
from dataclasses import dataclass
import copy
from helper import *
class Spur(TreeBranch):
  def __init__(self, config=None, copy_from=None, prototype_dict: dict = {}):
    super().__init__(config, copy_from, prototype_dict)

  def is_bud_break(self, num_buds_segment):
    if num_buds_segment >= self.growth.max_buds_segment:
      return False
    return (rd.random() < 0.1)
    
  def create_branch(self):
    return None
    
   
class TertiaryBranch(TreeBranch):
  def __init__(self, config=None, copy_from=None, prototype_dict: dict = {}):
    super().__init__(config, copy_from, prototype_dict)

  def is_bud_break(self, num_buds_segment):
    if num_buds_segment >= 2:
      return False
    if (rd.random() < 0.005*self.growth.growth_length*(1 - self.num_buds/self.growth.max_buds_segment)):
      self.num_buds +=1
      return True  
      
  def create_branch(self):
      if rd.random()>0.8:
        new_ob = Branch(copy_from = self.prototype_dict['side_branch'])
      else:
        new_ob = Spur(copy_from = self.prototype_dict['spur'])
      return new_ob  
    
class Branch(TreeBranch):
  def __init__(self, config=None, copy_from=None, prototype_dict: dict = {}):
    super().__init__(config, copy_from, prototype_dict)

  def is_bud_break(self, num_buds_segment):
      if num_buds_segment >= 2:
        return False
      if (rd.random() < 0.2*(1 - self.num_buds/self.growth.max_buds_segment)):

        return True  
      
  def create_branch(self):
    try:
      if rd.random()>0.9:
        new_ob = TertiaryBranch(copy_from = self.prototype_dict['side_branch'])
      else:
        new_ob = Spur(copy_from = self.prototype_dict['spur'])
    except:
      return None
    return new_ob  
 
    
class Trunk(TreeBranch):
  """ Details of the trunk while growing a tree, length, thickness, where to attach them etc """
  def __init__(self, config=None, copy_from=None, prototype_dict: dict = {}):
    super().__init__(config, copy_from, prototype_dict)

  def is_bud_break(self, num_buds_segment):
    if num_buds_segment >= self.growth.max_buds_segment:
      return False
    if (rd.random() > 0.05*self.length/self.growth.max_length*(1 - self.num_buds/self.growth.max_buds_segment)):
      return False
    self.num_buds+=1
    return True
    
  def create_branch(self):
    if rd.random() > 0.1:
      return Branch(copy_from = self.prototype_dict['branch'])
               


# growth_length = 0.1
basicwood_prototypes = {}

# Create configs for cleaner prototype setup
spur_config = BasicWoodConfig(
    max_buds_segment=5,
    tie_axis=None, 
    max_length=0.1, 
    thickness=0.003, 
    growth_length=0.05, 
    thickness_increment=0., 
    color=[0, 255, 0],
    bud_spacing_age=2,  # Spurs bud every 1 age unit
    curve_x_range=(-0.2, 0.2),  # Tighter bounds for spur curves
    curve_y_range=(-0.2, 0.2),  # Tighter bounds for spur curves
    curve_z_range=(-1, 1)       # Same Z range
)

side_branch_config = BasicWoodConfig(
    max_buds_segment=40,
    tie_axis=None, 
    max_length=0.25, 
    thickness=0.003, 
    growth_length=0.05, 
    thickness_increment=0.00001, 
    color=[0, 255, 0],
    bud_spacing_age=2,  # Tertiary branches bud every 3 age units
    curve_x_range=(-0.5, 0.5),  # Moderate bounds for tertiary branches
    curve_y_range=(-0.5, 0.5),  # Moderate bounds for tertiary branches
    curve_z_range=(-1, 1)       # Same Z range
)

trunk_config = BasicWoodConfig(
    max_buds_segment=60,
    tie_axis=(1, 0, 0), 
    max_length=3, 
    thickness=0.02, 
    thickness_increment=0.00001, 
    growth_length=0.1, 
    color=[255, 0, 0],
    bud_spacing_age=2,  # Trunk buds every 4 age units
    curve_x_range=(-0.3, 0.3),  # Conservative bounds for trunk
    curve_y_range=(-0.3, 0.3),  # Conservative bounds for trunk
    curve_z_range=(-0.5, 0.5)   # Tighter Z range for trunk
)

branch_config = BasicWoodConfig(
    max_buds_segment=140,
    tie_axis=(0, 0, 1), 
    max_length=2.5, 
    thickness=0.01, 
    thickness_increment=0.00001, 
    growth_length=0.1, 
    color=[255, 150, 0],
    bud_spacing_age=2,  # Branches bud every 2 age units
    curve_x_range=(-0.4, 0.4),  # Moderate bounds for primary branches
    curve_y_range=(-0.4, 0.4),  # Moderate bounds for primary branches
    curve_z_range=(-1, 1)       # Same Z range
)

# Setup prototypes using configs
basicwood_prototypes['spur'] = Spur(config=spur_config, prototype_dict=basicwood_prototypes)
basicwood_prototypes['side_branch'] = TertiaryBranch(config=side_branch_config, prototype_dict=basicwood_prototypes)
basicwood_prototypes['trunk'] = Trunk(config=trunk_config, prototype_dict=basicwood_prototypes)
basicwood_prototypes['branch'] = Branch(config=branch_config, prototype_dict=basicwood_prototypes)



@dataclass
class UFOSimulationConfig:
    """Configuration for UFO trellis tree simulation parameters."""
    
    # Tying and Pruning
    num_iteration_tie: int = 8
    num_iteration_prune: int = 16
    
    # Display
    label: bool = True
    
    # Support Structure
    support_trunk_wire_point: tuple = (0.6, 0, 0.4)
    support_num_wires: int = 7
    support_spacing_wires: int = 1
    
    # Point Generation
    ufo_x_range: tuple = (0.65, 3)
    ufo_x_spacing: float = 0.3
    ufo_z_value: float = 1.4
    ufo_y_value: float = 0
    
    # Energy and Tying Parameters
    energy_distance_weight: float = 0.5  # Weight for distance in energy calculation (was hardcoded /2)
    energy_threshold: float = 1.0  # Maximum energy threshold for tying
    
    # Pruning Parameters
    pruning_age_threshold: int = 8  # Age threshold for pruning untied branches
    
    # L-System Parameters
    derivation_length: int = 160  # Number of derivation steps
    
    # Growth Parameters
    thickness_multiplier: float = 1.2  # Multiplier for internode thickness
    bud_age_tolerance: float = 0.01  # Tolerance for age-based bud spacing
    
    # Visualization Parameters
    attractor_point_width: int = 10  # Width of attractor points in visualization