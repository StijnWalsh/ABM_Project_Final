# Importing necessary libraries
import random
from mesa import Agent
from shapely.geometry import Point
from shapely import contains_xy
import math 

# Import functions from functions.py
from functions import generate_random_location_within_map_domain, get_flood_depth, calculate_basic_flood_damage, floodplain_multipolygon


# Define the Households agent class
class Households(Agent):
    """
    An agent representing a household in the model.
    Each household has a flood depth attribute which is randomly assigned for demonstration purposes.
    In a real scenario, this would be based on actual geographical data or more complex logic.
    """

    def __init__(self, unique_id, model, stubbornness, weight, current_step, avg_diff_agent):
        super().__init__(unique_id, model)
        self.is_adapted = False  # Initial adaptation status set to False
        ##self.belief = initial_belief #agents initial belief or opinion 
        self.stubbornness = stubbornness #coefficient ranging from 0 to 1
        self.friends = []
        self.weights = {}
        self.avg_diff_agent = []
        self.current_step = 0
        self.running = True
        self.weight = weight
        self.current_step = current_step
        # getting flood map values
        # Get a random location on the map
        loc_x, loc_y = generate_random_location_within_map_domain()
        self.location = Point(loc_x, loc_y)

        # Check whether the location is within floodplain
        self.in_floodplain = False
        if contains_xy(geom=floodplain_multipolygon, x=self.location.x, y=self.location.y):
            self.in_floodplain = True

        # Get the estimated flood depth at those coordinates. 
        # the estimated flood depth is calculated based on the flood map (i.e., past data) so this is not the actual flood depth
        # Flood depth can be negative if the location is at a high elevation
        self.flood_depth_estimated = get_flood_depth(corresponding_map=model.flood_map, location=self.location, band=model.band_flood_img)
        # handle negative values of flood depth
        if self.flood_depth_estimated < 0:
            self.flood_depth_estimated = 0
        
        # calculate the estimated flood damage given the estimated flood depth. Flood damage is a factor between 0 and 1
        self.flood_damage_estimated = calculate_basic_flood_damage(flood_depth=self.flood_depth_estimated)
        self.belief = self.flood_damage_estimated

        # Add an attribute for the actual flood depth. This is set to zero at the beginning of the simulation since there is not flood yet
        # and will update its value when there is a shock (i.e., actual flood). Shock happens at some point during the simulation
        self.flood_depth_actual = 0
        
        #calculate the actual flood damage given the actual flood depth. Flood damage is a factor between 0 and 1
        self.flood_damage_actual = calculate_basic_flood_damage(flood_depth=self.flood_depth_actual)

    def define_friends(self, radius):
        """Get all agents in adjacent nodes."""
        neighborhood = self.model.grid.get_neighborhood(self.pos, include_center=False, radius=radius)
        self.friends = self.model.grid.get_cell_list_contents(neighborhood)
        print(f"Agent {self.unique_id} has friends {[friend.unique_id for friend in self.friends]}")

    # Function to count friends who can be influencial.
    def count_friends(self, radius):
        """Count the number of neighbors within a given radius (number of edges away). This is social relation and not spatial"""
        friends = self.model.grid.get_neighborhood(self.pos, include_center=False, radius=radius)
        return len(friends)
    
    def step(self):
        self.current_step += 1
        #herziene eigen belief bepaald adapted of niet
        self.calculate_belief()
        if self.belief > 0.5: #and random.random() < 0.2: 
            self.is_adapted = True  # Agent adapts to flooding
        self.get_belief_friends()
        belief_differences = [abs(self.belief - friend.belief) for friend in self.friends]

        # Calculate the average difference in belief
        average_belief_difference = sum(belief_differences) / len(belief_differences) if belief_differences else  0
        self.avg_diff_agent.append(average_belief_difference)
        print('')
        print('')        
        print("The average belief difference at this step is", average_belief_difference)
    
        
        
    def get_belief_friends(self):
        for friend in self.friends:
            print(f'Friend', friend.unique_id, 'has belief', friend.belief)


    def calculate_distance(self):
        self.friends_distance = {}
        for friend in self.friends: 
            distance = math.sqrt((self.location.x - friend.location.x)**2 + (self.location.y - friend.location.y)**2)
            self.friends_distance[friend] = distance
        print_dict = {f'friend {friend.unique_id}':distance for friend,distance in self.friends_distance.items()}
        print( f"Agent {self.unique_id}: {print_dict}" )    
                
    def calculate_weight(self):
        smallest_distance = min(self.friends_distance.values())
        largest_distance = max(self.friends_distance.values())
    
    # To handle the case when all distances are the same (prevent division by zero)
        if smallest_distance == largest_distance:
            for friend in self.friends:
                self.weights[friend] = 1 if smallest_distance == 0 else 0
            return
    
        for friend in self.friends:
            normalized_distance = (self.friends_distance[friend] - smallest_distance) / (largest_distance - smallest_distance)    
            self.weights[friend] = normalized_distance
        print_dictionary = {f'friend {friend.unique_id}': weight for friend, weight in self.weights.items()}
        #print_dictionary2 = {f'friend {friend.unique_id}' : belief for friend, belief in self.belief.items()}
        print(f'')
        print(f"Weights of agent {self.unique_id}: {print_dictionary}")
        print(f'Agents initial belief =', self.belief)
        print(f'Agents stubbornness =', self.stubbornness)
        #print(print_dictionary2)

    
    def calculate_belief(self):
        for friend in self.friends:
            if abs(self.belief - friend.belief) <= 1:   
                self.belief = ((self.stubbornness * self.belief + (friend.belief * self.weights[friend])) / (self.stubbornness + self.weights[friend]))
            else: 
                self.belief = self.belief
        print('')
        print('At step:', self.current_step, 'agent', self.unique_id, 'has belief:', self.belief)

# Define the Government agent class
class Government(Agent):
    """
    A government agent that currently doesn't perform any actions.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # The government agent doesn't perform any actions.
        pass
 


