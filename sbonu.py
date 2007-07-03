#!/usr/bin/env python
import random
from util import StarvationError
from space import Space
from spores import Spore, Spawner, Infectable

# Width and height of the "map".
DIMENSION = 50


# Support for picking a random direction to travel.
_R = (-1, 0, 1)
_spots = tuple((x, y) for x in _R for y in _R if x or y)
# _spots now contains deltas which, if added to x, y coordinates will let
# an NPC move one "space" in one of 8 directions.


class NPC(Infectable):

    a = 100 # If I've had this much food
    b = 10 #  for this many turns
    #         then it's cool to reproduce.

    def __init__(self):
        Infectable.__init__(self)

    def reproduce(self):
        '''
        Clone self if conditions are right.
        '''
        # Get the number of turns we've had enough food.
        try:
            turns_o_plenty = self.turns_o_plenty
        except AttributeError:
            self.turns_o_plenty = self.foods > self.a
            return

        turns_o_plenty += cmp(self.foods, self.a)

        if turns_o_plenty > self.b:
            self.turns_o_plenty = 0
            return self.clone()

        self.turns_o_plenty = max((turns_o_plenty, 0))

    def clone(self):
        '''
        Create a clone of self.
        '''
        clone = NPC()
        clone.immunities.update(self.immunities)
        clone.infections[:] = [spore.spawn() for spore in self.infections]
        for spore in clone.infections:
            spore.register(clone)
        clone.foods = self.foods = self.foods / 2
        return clone

    def program(self):
        '''
        Run a "program" of actions.
        '''

        # Try to eat some food.
        food = self.space.forage(self)
        self.foods += food
        if self.foods <= 0:
            raise StarvationError(repr(self))

        # Maybe we tithe to some worthy cause.
        if self.infections:
            random.choice(self.infections).act(self)

        # Try to afflict one nearby person.
        People = list(self.space.yieldNeighbours(self, 2))
        if People:
            self.afflict(random.choice(People))

        # If you didn't eat this turn, wander around a bit.
        if not food:
            self.wander()

        # If you did, consider having a child.
        else:
            clone = self.reproduce()
            if clone:
                self.space.newLife(self, clone)

    def wander(self):
        '''
        Wander around.
        '''
        # Get our bearings and pick a direction.
        dx, dy = self.whichWay()

        # Make our move.
        self.foods -= self.space.move(dx, dy, self)

    def whichWay(self):
        '''
        Pick a direction of travel, return (dx, dy).

        This version looks for food in the immediate vicinity and moves
        towards it.  If there's no food it picks a direction at random.
        '''
        nearby_food = tuple(self.space.yieldNearbyFoods(self))
        return random.choice(nearby_food or _spots)


class PC(NPC):
    pass


class SbonuSimulation:

    def __init__(
        self,
        dimension,
        food_growth_rate,
        number_of_npcs,
        initial_food_cycles=3
        ):
        self.space = Space(dimension, food_growth_rate)

        random_coord = lambda : random.randint(0, dimension - 1)

        NPCs = tuple(NPC() for _ in xrange(number_of_npcs))

        for person in NPCs:
            self.space.enter(random_coord(), random_coord(), person)

        for _ in range(initial_food_cycles):
            self.space.generate()

    def step(self):
        '''
        Simulation "step".  Run every NPC's program() once.
        '''
        # If there's anybody there, run their program.
        for person in self.space.yieldPeople():
            try:
                person.program()
            except StarvationError:
                self.space.leave(person)
                # This should be sufficient to cause the person to be
                # garbage-collected.
        self.space.generate()

#########################################################################

def setup_sim():

    class VIP_NPC(NPC):
        def reproduce(self):
            pass

    Alice = VIP_NPC()

    class testSpore(Spore):
        virulence = 0.05

    S = Spawner('cats', Alice, testSpore)

    sim = SbonuSimulation(DIMENSION, 30, 59)
    sim.space.enter(DIMENSION/2, DIMENSION/2, Alice)

    return Alice, S, sim

def main():
    print "run 'nice ./curses_sbonu.py' to see UI"

if __name__ == '__main__':
    main()

