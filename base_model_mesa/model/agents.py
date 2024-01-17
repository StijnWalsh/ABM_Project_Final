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

    def __init__(self, unique_id, model, initial_belief, stubbornness, weight):
        super().__init__(unique_id, model)
        self.is_adapted = False  # Initial adaptation status set to False
        self.belief = initial_belief #agents initial belief or opinion 
        self.stubbornness = stubbornness #coefficient ranging from 0 to 1
        self.influence_radius = 100
        self.friends = []
        # getting flood map values
        # Get a random location on the map
        loc_x, loc_y = generate_random_location_within_map_domain()
        self.location = Point(loc_x, loc_y)
        weight = 0

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

        # Add an attribute for the actual flood depth. This is set to zero at the beginning of the simulation since there is not flood yet
        # and will update its value when there is a shock (i.e., actual flood). Shock happens at some point during the simulation
        self.flood_depth_actual = 0
        
        #calculate the actual flood damage given the actual flood depth. Flood damage is a factor between 0 and 1
        self.flood_damage_actual = calculate_basic_flood_damage(flood_depth=self.flood_depth_actual)

    def define_friends(self):
        self.friends = self.model.grid.get_neighborhood(self.pos, include_center=False, radius=1)
    
    # Function to count friends who can be influencial.
    def count_friends(self, radius):
        """Count the number of neighbors within a given radius (number of edges away). This is social relation and not spatial"""
        friends = self.model.grid.get_neighborhood(self.pos, include_center=False, radius=radius)
        return len(friends)

    def step(self):
        # Assuming self.model.other_agents() returns a list of other agent objects
        self.friends.append(friends)
        # Calculate the weighted average of beliefs, including the agent's own belief
        total_weight = self.stubbornness
        weighted_belief_sum = self.belief * self.stubbornness

        for friends in self.friends:
            # Assuming a function that calculates the weight given to others' beliefs
            if self.belief - friends.belief <= 0.5:   
                weight == self.calculate_weight(friends)
                total_weight += weight
                weighted_belief_sum += friends.belief * weight
            else: 
                weight = 0        

        # Update the agent's belief based on the weighted sum of beliefs
        self.belief = weighted_belief_sum / total_weight
        # Logic for adaptation based on estimated flood damage and a random chance.
        # These conditions are examples and should be refined for real-world applications.
        if self.flood_damage_estimated > 0.15 and random.random() < 0.2:
            self.is_adapted = True  # Agent adapts to flooding

    def calculate_weight(self, friends): 
        distance = math.sqrt((self.location[0]- friends.location[0]**2) + (self.location[1]-friends.location[1]**2))
        if distance > self.influence_radius:
            return 0 
        weight = 1 / (distance + 1)
        return weight

        
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

# More agent classes can be added here, e.g. for insurance agents.
