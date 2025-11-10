from openalea.plantgl.all import NurbsCurve, Vector3, Vector4, Point4Array, Point2Array, Point3Array, Polyline2D, BezierCurve, BezierCurve2D
from openalea.lpy import Lsystem, newmodule
from random import uniform, seed
from numpy import linspace, pi, sin, cos
import numpy as np

def amplitude(x): return 2

def cut_from(pruning_id, s, path = None):
    """Check cut_string_from_manipulation for manual implementation"""
    # s.insertAt(pruning_id, newmodule('F'))
    s.insertAt(pruning_id+1, newmodule('%'))
    return s

def cut_using_string_manipulation(pruning_id, s, path = None):
  """Cuts starting from index pruning_id until branch 
        end signified by ']' or the entire subtrees if pruning_id starts from leader"""
  bracket_balance = 0
  cut_num = pruning_id
  #s[cut_num].append("no cut")
  cut_num += 1
  pruning_id +=1
  total_length = len(s)
  while(pruning_id < total_length):
      if s[cut_num].name == '[':
          bracket_balance+=1
      if s[cut_num].name == ']':
          if bracket_balance == 0:
              break
          else:
              bracket_balance-=1
      del s[cut_num]
      pruning_id+=1             # Insert new node cut at the end of cut
  if path != None:
      new_lsystem = Lsystem(path) #Figure out to include time in this
      new_lsystem.axiom = s
      return new_lsystem
  #s.insertAt(cut_num, newmodule("I(1, 0.05)"))
  return s

def pruning_strategy(it, lstring):
  if((it+1)%8 != 0):  
    return lstring
  cut = False
  curr = 0
  while curr < len(lstring):
    if lstring[curr] == '/':
      if not (angle_between(lstring[curr].args[0], 0, 50) or angle_between(lstring[curr].args[0], 130, 180)):
        if(len(lstring[curr].args) > 1):
          if lstring[curr].args[1] == "no cut":
            curr+=1
            continue
        
        # print("Cutting", curr, lstring[curr], (lstring[curr].args[0]+180))
        #lstring[curr].append("no cut")
        lstring = cut_from(curr+1, lstring)
    elif lstring[curr] == '&':
      if not (angle_between(lstring[curr].args[0], 0, 50) or angle_between(lstring[curr].args[0], 130, 180)):
        if(len(lstring[curr].args) > 1):
          if lstring[curr].args[1] == "no cut":
            curr+=1
            continue
        # print("Cutting", curr, lstring[curr], (lstring[curr].args[0]+180))
        #lstring[curr].append("no cut")
        lstring = cut_from(curr+1, lstring)
    curr+=1
  
  return lstring

def angle_between(angle, min, max):
  angle = (angle+90)
  if angle > min and angle < max:
    return True
  return False
  
def myrandom(radius): 
    return uniform(-radius,radius)

def gen_noise_branch(radius,nbp=20):
    return  NurbsCurve([(0,0,0,1),(0,0,1/float(nbp-1),1)]+[(myrandom(radius*amplitude(pt/float(nbp-1))),
                                     myrandom(radius*amplitude(pt/float(nbp-1))),
                                     pt/float(nbp-1),1) for pt in range(2,nbp)],
                        degree=min(nbp-1,3),stride=nbp*100)

def create_noisy_branch_contour(radius, noise_factor, num_points=100, seed=None):
  if seed is not None:
      seed(seed)
  t = linspace(0, 2 * pi, num_points, endpoint=False)
  points = []
  for angle in t:
      # Base circle points
      x = radius * cos(angle)
      y = radius * sin(angle)
      
      # Add noise
      noise_x = uniform(-noise_factor, noise_factor)
      noise_y = uniform(-noise_factor, noise_factor)
      
      noisy_x = x + noise_x
      noisy_y = y + noise_y
      
      points.append((noisy_x, noisy_y))
  
  # Ensure the curve is closed by adding the first point at the end
  points.append(points[0])
  
  # Create the PlantGL Point2Array and Polyline2D
  curve_points = Point2Array(points)
  curve = Polyline2D(curve_points)
  return curve

def create_bezier_curve(num_control_points=6, x_range=(-2,2), y_range=(-2, 2), z_range = (0, 10), seed_val=None):
    if seed_val is not None:
        seed(seed_val)  # Set the random seed for reproducibility
    # Generate progressive control points within the specified ranges
    control_points = []
    zs = linspace(z_range[0], z_range[1], num_control_points)
    for i in range(num_control_points):
        x = uniform(*x_range)
        y = uniform(*y_range)
        control_points.append(Vector4(x, y, zs[i], 1))  # Set z to 0 for 2D curve
    # Create a Point3Array from the control points
    control_points_array = Point4Array(control_points)
    # Create and return the BezierCurve2D object
    bezier_curve = BezierCurve(control_points_array)
    return bezier_curve


 
def get_energy_mat(branches, arch, simulation_config):
    """
    Calculate the energy matrix for optimal branch-to-wire assignment.
    
    This function computes an energy cost matrix where each entry represents the
    "cost" of assigning a specific branch to a specific wire in the trellis system.
    The energy is based on the Euclidean distance from wire attachment points to
    both the start and end points of each branch, weighted by the simulation's
    distance weight parameter.
    
    The algorithm uses a greedy optimization approach where branches are assigned
    to the lowest-energy available wire that hasn't reached capacity.
    
    Args:
        branches: List of branch objects to be assigned to wires
        arch: Support architecture object containing wire information
        
    Returns:
        numpy.ndarray: Energy matrix of shape (num_branches, num_wires) where
                      matrix[i][j] is the energy cost of assigning branch i to wire j.
                      Untied branches and occupied wires have infinite energy (np.inf).
    """
    num_branches = len(branches)
    num_wires = len(arch.branch_supports)
    
    # Initialize energy matrix with infinite values (impossible assignments)
    energy_matrix = np.full((num_branches, num_wires), np.inf)
    
    # Calculate energy costs for all valid branch-wire combinations
    for branch_idx, branch in enumerate(branches):
        # Skip branches that are already tied
        if branch.tying.has_tied:
            continue
            
        for wire_id, wire in arch.branch_supports.items():
            # Skip wires that already have a branch attached
            if wire.num_branch >= 1:
                continue
                
            # Calculate weighted distance energy for this branch-wire pair
            # Energy considers distance from wire to both branch endpoints
            wire_point = np.array(wire.point)
            branch_start = np.array(branch.location.start)
            branch_end = np.array(branch.location.end)
            
            start_distance_energy = np.sum((wire_point - branch_start) ** 2)
            end_distance_energy = np.sum((wire_point - branch_end) ** 2)
            
            total_energy = (start_distance_energy + end_distance_energy) * simulation_config.energy_distance_weight
            
            energy_matrix[branch_idx, wire_id] = total_energy
    
    return energy_matrix

def decide_guide(energy_matrix, branches, arch, simulation_config):
    """
    Perform greedy assignment of branches to wires based on energy matrix.
    
    This function implements a greedy optimization algorithm that iteratively assigns
    the branch-wire pair with the lowest energy cost. Once a branch is assigned to
    a wire, both that branch and wire are marked as unavailable (infinite energy)
    to prevent further assignments.
    
    The algorithm continues until no valid assignments remain (all remaining energies
    are infinite or above the threshold).
    
    Args:
        energy_matrix: numpy.ndarray of shape (num_branches, num_wires) with energy costs
        branches: List of branch objects to be assigned
        arch: Support architecture containing wire information
        
    Returns:
        None: Modifies branches and arch in-place with new assignments
    """
    num_branches, num_wires = energy_matrix.shape
    
    # Early return if no branches or wires to assign
    if num_branches == 0 or num_wires == 0:
        return
    
    # Continue making assignments until no valid ones remain
    while True:
        # Find the minimum energy value and its position
        min_energy_indices = np.argwhere(energy_matrix == np.min(energy_matrix))
        
        # If no valid indices found or matrix is empty, stop
        if len(min_energy_indices) == 0:
            break
            
        # Get the first (and typically only) minimum energy position
        branch_idx, wire_id = min_energy_indices[0]
        min_energy = energy_matrix[branch_idx, wire_id]
        
        # Stop if minimum energy is infinite (no valid assignments) or above threshold
        if np.isinf(min_energy) or min_energy > simulation_config.energy_threshold:
            break
            
        # Get the branch and wire objects
        branch = branches[branch_idx]
        wire = arch.branch_supports[wire_id]
        
        # Skip if branch is already tied (defensive check)
        if branch.tying.has_tied:
            # Mark this assignment as invalid and continue
            energy_matrix[branch_idx, wire_id] = np.inf
            continue
            
        # Perform the assignment
        branch.tying.guide_target = wire
        wire.add_branch()
        
        # Mark branch and wire as unavailable for future assignments
        # Set entire row (branch) to infinity - this branch can't be assigned again
        energy_matrix[branch_idx, :] = np.inf
        # Set entire column (wire) to infinity - this wire can't accept more branches
        energy_matrix[:, wire_id] = np.inf


def prune(lstring, simulation_config):
    """
    Prune old branches that exceed the age threshold and haven't been tied to wires.

    This function implements the pruning strategy for the tree training simulation.
    It identifies branches that have grown too old (exceeding the pruning age threshold)
    but haven't been successfully tied to trellis wires. Such branches are considered
    unproductive and are removed from the L-System to encourage new growth.

    The pruning criteria are:
    1. Branch age exceeds the configured pruning threshold
    2. Branch has not been tied to any trellis wire
    3. Branch has not already been marked for cutting

    When a branch meets all criteria, it is:
    - Marked as cut (to prevent re-processing)
    - Removed from the L-System string using cut_from()

    Args:
        lstring: The current L-System string containing modules and their parameters

    Returns:
        bool: True if a branch was pruned, False if no eligible branches found

    Note:
        This function processes one branch at a time and returns immediately after
        pruning a single branch. It should be called repeatedly (e.g., in a while loop)
        until no more pruning operations are possible. The cut_from() function handles
        the actual removal of the branch and any dependent substructures from the string.
    """
    for position, symbol in enumerate(lstring):
        # Check if this is a WoodStart module (represents a branch)
        if symbol.name == 'WoodStart':
            branch = symbol[0].type

            # Check pruning criteria
            age_exceeds_threshold = branch.info.age > simulation_config.pruning_age_threshold
            not_tied_to_wire = not branch.tying.has_tied
            not_already_cut = not branch.info.cut

            # Prune if all criteria are met
            if age_exceeds_threshold and not_tied_to_wire and not_already_cut:
                # Mark branch as cut to prevent re-processing
                branch.info.cut = True

                # Remove the branch from the L-System string
                lstring = cut_from(position, lstring)

                return True

    return False



def tie(lstring, simulation_config):
    """
    Perform tying operation on eligible branches in the L-System string.
    
    This function searches through the L-System string for 'WoodStart' modules that
    represent branches ready for tying to trellis wires. It identifies branches that:
    1. Have tying properties (tying attribute exists)
    2. Have a defined tie axis (tie_axis is not None)
    3. Have not been tied yet (tie_updated is False)
    4. Have guide points available for wire attachment
    
    When an eligible branch is found, it performs the tying operation by:
    - Marking the branch as tied (tie_updated = False)
    - Adding the branch to the target wire
    - Calling the branch's tie_lstring method to modify the L-System string
    
    Args:
        lstring: The current L-System string containing modules and their parameters
        
    Returns:
        bool: True if a tying operation was performed, False if no eligible branches found
        
    Note:
        This function processes one branch at a time and returns immediately after
        tying a single branch. It should be called repeatedly (e.g., in a while loop)
        until no more tying operations are possible.
    """
    for position, symbol in enumerate(lstring):
        # Check if this is a WoodStart module with tying capabilities
        if (symbol == 'WoodStart' and 
            hasattr(symbol[0].type, 'tying') and 
            getattr(symbol[0].type.tying, 'tie_axis', None) is not None):
            
            branch = symbol[0].type
            
            # Skip branches that have already been processed for tying
            if not branch.tying.tie_updated:
                continue
                
            # Check if branch has guide points for wire attachment
            if branch.tying.guide_points:
                # Perform the tying operation
                branch.tying.tie_updated = False
                branch.tying.guide_target.add_branch()
                
                # Update the L-System string with tying modifications
                lstring, modifications_count = branch.tie_lstring(lstring, position)
                
                return True
    
    return False