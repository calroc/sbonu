#!/usr/bin/env python
import random
from pprint import pprint as p


# Width and height of the "map".
DIMENSION = 50


# Support for picking a random direction to travel.
_R = (-1, 0, 1)
_spots = tuple((x, y) for x in _R for y in _R if x or y)
# _spots now contains deltas which, if added to x, y coordinates will let
# an NPC move one "space" in one of 8 directions.


# Global count of all "food" that has been put in play.
_calories = 0


class Spawner:
    '''
    Source of spores for a genus, tied to one author.
    '''
    def __init__(self, genus, Author, spore_class):
        self.genus = genus
        self.Author = Author
        self.spore_class = spore_class

        Author.infection(self.spawn())        

    def spawn(self):
        '''
        Create and return a new spore of this genus.
        '''
        return self.spore_class(self.genus, [self.Author])


class Spore:
    '''
    One "packet" of DNA.  Has genus and a lineage chain.
    '''

    virulence = 0.01

    def __init__(self, genus, chain=None):
        self.genus = genus
        self.chain = self.prepChain(chain)

    def prepChain(self, chain):
        '''
        Called by __init__() at spore creation time, prepChain() receives
        the chain of the parent spore and prepares it for the new spore.

        Subclasses can override this method to provide their own chain
        manipulation.

        The default implementation just returns up to six most recent
        parents, preserving the Author at the beginning.
        '''
        if len(chain) > 7:
            chain = chain[:1] + chain[-6:]
        return chain

    def infects(self, person):
        '''
        Return Boolean indictating success of an attepmt to infect person.
        '''
        suscept = person.susceptibilityTo(self.genus)

        if suscept:
            chance = suscept * self.virulence
            res = random.random() <= chance
        else:
            res = False

        return res

    def infect(self, person):
        '''
        Try to infect person, return a bool indicating success.
        '''
        if not person.immuneResponse(self):
            self.chain.append(person)
            return True
        return False

    def spawn(self):
        '''
        Create and return a new spore of the genus of this spore and pass
        it self's chain of "vectors".
        '''
        return self.__class__(self.genus, self.chain)


class Food:
    '''
    Represents the growth of "food" at a Location.  Supports growth with
    add() and "eating" with subtract().
    '''
    def __init__(self, amount=1):
        self.amount = amount

    def add(self, amount):
        '''Add amount of food to self.'''
        self.amount += amount

    def subtract(self, amount):
        '''
        Attempt to subtract amount from self and return int as follows:

            n > 0: success, amount available. (implies n == amount)
                            "Plant" lives.

            n = 0: success, but amount exhausted all available food.
                            "Plant" dies.

            n < 0: failure, amount was greater than available, -n = what
                            was actually "eaten".
                            "Plant" dies.

        (Note: Client code must take care of destroying "dead" Food.)
        '''
        if amount > self.amount:
            res = -self.amount
        elif amount == self.amount:
            res = self.amount = 0
        else:
            assert amount < self.amount
            res = amount
            self.amount -= amount
        return res


class Person:
    '''
    Base class for PCs and NPCs.
    '''
    def __init__(self):

        # Map from genus to immunity (0.0 to 1.0).
        self.immunities = {}

        # Spores that have infected this person and are now available to
        # be used to infect others.
        self.infections = []

        # Person's power supply.  Used to move, gotten from food and bonuses.
        self.foods = 100

    def immuneResponse(self, spore):
        '''
        Resolve an attempt of spore to infect self.  Either an infection
        occurs, or the attempt fails and a resistance to the genus of the
        spore is built up somewhat.

        Returns bool indicating whether "immune system" has "fought off"
        the attempt: True for no infection, False for infection.
        '''
        infected = spore.infects(self)

        if infected:
            self.infection(spore)
        else:
            self.buildResistance(spore)

        return not infected

    def buildResistance(self, spore):
        '''
        Increase self's resistance to the genus of spore.
        '''
        imm = self.immunities.get(spore.genus, 0.0)
        self.immunities[spore.genus] = min((imm + 0.01, 1.0))

    def infection(self, spore):
        '''
        Infect self with spore.
        '''
        self.infections.append(spore)
        self.immunities[spore.genus] = 1.0

    def susceptibilityTo(self, genus):
        '''
        Return a float between 0 and 1 indicating self's "susceptibility"
        to infection by spores of genus genus.
        '''
        try:
            imm = self.immunities[genus]
        except KeyError:
            imm = 0.0
        return 1 - imm

    def afflict(self, other, spore=None):
        '''
        Try to infect other with spore (if given) or, if infected with
        one or more genii, one those chosen at random.
        Return a bool indicating success.
        '''
        if not spore:
            if self.infections:
                spore = random.choice(self.infections)
                spore = spore.spawn()
            else:
                return False
        return spore.infect(other)


class PC(Person):
    pass


class NPC(Person):

    a = 100 # If I've had this much food
    b = 10 #  for this many turns
    #         then it's cool to reproduce.

    def reproduce(self, location):
        '''
        Clone self at location.
        '''
        # Get the number of turns we've had enough food.
        try:
            turns_o_plenty = self.turns_o_plenty
        except AttributeError:
            self.turns_o_plenty = self.foods > self.a
            return

        delta = cmp(self.foods, self.a)
        assert delta in (-1, 0, 1)

        turns_o_plenty += delta

        if turns_o_plenty > self.b:
            self.clone(location)
            turns_o_plenty = 0

        elif turns_o_plenty < 0:
            turns_o_plenty = 0

        self.turns_o_plenty = turns_o_plenty

    def clone(self, location):
        '''
        Create a clone of self at location.
        '''
        clone = NPC()
        clone.immunities.update(self.immunities)
        clone.infections[:] = [spore.spawn() for spore in self.infections]
        for spore in clone.infections: spore.chain.append(clone)
        clone.foods = self.foods = self.foods / 2
        location.enter(clone)
        return clone

    def program(self, location):
        '''
        Given self's current location, run a "program" of actions.
        '''

        # Try to eat some food.
        food = location.eat()
        self.foods += food

        # Look around, see who's nearby.
        People = []
        for place in location.getNearby(2, Location.occupied):
            People.extend(place.occupants)
        People.remove(self)

        # Try to afflict one nearby person.
        if People:
            person = random.choice(People)
            self.afflict(person)

        # If you didn't eat this turn, wander around a bit.
        if not food:

            # Get our bearings and pick a direction.
            x, y = location.coords
            dx, dy = self.whichWay(location)

            # Don't wander into dragon territory.
            x = max((min((x + dx, DIMENSION)), 0))
            y = max((min((y + dy, DIMENSION)), 0))

            # Scout the terrain.
            new_location = location.space.getOrMake(x, y)

            # Make your move.
            location.leave(self)
            new_location.enter(self)

            # Boy that was exhausting.
            self.foods -= 1

        else:
            self.reproduce(location)

    def whichWay(self, location):
        '''
        Pick a direction of travel, return (dx, dy).

        This version looks for food in the immediate vicinity and moves
        towards it.  If there's no food it picks a direction at random.
        '''

        nearby_food = location.getNearby(1, lambda loc: bool(loc.food))

        if nearby_food:
            xx, yy = random.choice(nearby_food).coords
            x, y = location.coords
            dx = xx - x
            dy = yy - y

        else:
            dx, dy = random.choice(_spots)

        return dx, dy


class Space:
    '''
    Represents a 2-D grid and supports various behaviors.
    '''

    def __init__(self,
        dimension=DIMENSION,
        food_growth_rate=30,
        ):
        self.dim = dimension
        self.food_growth_rate = food_growth_rate
        self.space = {}

    def getOrMake(self, x, y):
        '''
        Return the Location at x, y creating it first if there's not one.
        '''
        coords = x, y
        location = self.space.get(coords)
        if not location:
            location = Location(self, coords)
            self.space[coords] = location
        return location

    def get(self, x, y):
        '''
        Return the Location at x, y or None if there's not one.
        '''
        return self.space.get((x, y))

    def one_food(self):
        '''
        Randomly place a food somewhere.
        '''

        # Pick a random location.
        x = random.randint(0, self.dim - 1)
        y = random.randint(0, self.dim - 1)

        # Find all food stuffs within 4.
        nearby = [
            location
            for location in self.within(x, y, 4)
                if location.food
            ]

        if nearby:
            location = random.choice(nearby)
        else:
            location = self.getOrMake(x, y)

        location.addFood()

    def generate(self):
        '''
        Add food_growth_rate foods to the space.
        '''
        for _ in range(self.food_growth_rate):
            self.one_food()

    def within(self, x, y, distance):
        '''
        Return list of Location objects within distance from x, y.
        '''

        left = x - distance
        right = x + distance
        top = y - distance
        bottom = y + distance

        return [
            value
            for (xx, yy), value in self.space.iteritems()
            if (xx >= left) and (xx <= right) and \
               (yy >= top) and (yy <= bottom)
        ]

    def run(self):
        '''
        Crude simulation loop.
        '''
        # Go through all locations.
        for key, location in list(self.space.items()):

            # Clean out any empty locations.
            if location.empty():
                del self.space[key]
                continue

            # If there's anybody there, run their program.
            for person in location.occupants:
                person.program(location)

    def yieldPeople(self):
        '''
        Iterate through all the people in the space.
        '''
        for location in self.space.itervalues():
            for person in location.occupants:
                yield person

    def __str__(self):
        return '\n'.join(''.join(self._row(x)) for x in range(self.dim))

    def _row(self, x):
        for y in range(self.dim):
            L = self.get(x, y)
            if L:
                yield str(L)
            else:
                yield ' '


class Location:
    '''
    Represents one location in the space sparse matrix.
    '''

    def __init__(self, space, coords):
        self.space = space
        self.coords = coords
        self.food = None
        self.occupants = []

    def empty(self):
        '''
        Return bool indicating if this Location is empty.
        '''
        return True not in (bool(attr) for attr in (
            self.food,
            self.occupants,
            ))

    def occupied(self):
        '''
        Return bool indicating if this Location has any people in it.
        '''
        return bool(self.occupants)

    def enter(self, person):
        '''
        Move person into Location
        '''
        assert person not in self.occupants
        self.occupants.append(person)

    def leave(self, person):
        '''
        Remove person from Location.
        '''
        assert person in self.occupants
        self.occupants.remove(person)

    def getNearby(self, distance, predicate=None):
        '''
        Return a list of all Location objects within distance.  If
        predicate is given, it should be a filter callable that takes a
        Location and returns True or False to indicate whether the
        Location should be included in the list.
        '''
        x, y = self.coords
        nearby = self.space.within(x, y, distance)

        if predicate:
            nearby = [loc for loc in nearby if predicate(loc)]

        return nearby

    def addFood(self, amount=1):
        '''
        Add amount food to Location, creating Food object if needed.
        Tracks total food added using global _calories.
        '''
        if not self.food:
            self.food = Food(amount)
        else:
            self.food.add(amount)
        global _calories
        _calories += amount

    def eat(self, amount=1):
        '''
        Attempt to return amount from Location's food.
        '''
        res = 0

        if self.food:

            # Try to eat some food..
            res = self.food.subtract(amount)

            # We exhausted the food..
            if res <= 0:

                # Delete the empty food object.
                self.food = None

                if res == 0:
                    res = amount # We finished off the food exactly.
                else:
                    res = -res # We only got this much food.
        return res

    def __str__(self):
        # Support for string representation.
        n = len(self.occupants)
        if n:
            if n == 1:
                occ = self.occupants[0]
                if occ.infections:
                    return '*'
                else:
                    return 'O'
            elif n > 9:
                return '+'
            else:
                return str(n)
        elif self.food:
            return 'f'
        return '.'


#########################################################################

from time import sleep

Alice, Bob, Claire, Debbie, Eve = (NPC() for _ in range(5))

ppl = (Alice, Bob, Claire, Debbie, Eve)
NPCs = tuple(NPC() for _ in range(55)) + ppl

class testSpore(Spore):
    virulence = 0.05

S = Spawner('cats', Alice, testSpore)

##Alice.afflict(Bob)
##Bob.afflict(Claire)
##Claire.afflict(Debbie)
##Debbie.afflict(Eve)

s = Space(food_growth_rate=30)
for person in NPCs:
    location = s.getOrMake(
        random.choice(range(DIMENSION)),
        random.choice(range(DIMENSION))
        )
    location.enter(person)

for _ in range(3):
    s.generate()

##print str(s)

_N = float(len(NPCs))

def onestep(n):
    s.run()
    s.generate()

    population = sum(1 for npc in s.yieldPeople())
    infected = sum(1 for npc in NPCs if npc.infections)/_N
    if infected < 0.008:
        return 'break'

    f = lambda npc: not npc.infections and npc.immunities.get('cats')  == 1
    immune = sum(1 for npc in NPCs if f(npc))/_N

    print '%s %.02f %.02f %05i %-i' % (str(s), infected, immune, n, population)
##    print '%.02f %.02f %05i %-i' % (infected, immune, n, population)

    if infected + immune == 1:
        return 'break'
##    print ' '.join('%04i' % (npc.foods,) for npc in NPCs)

    sleep(1.0/23)


def main():
    for n in range(10000):
        if onestep(n):
            break

    print 'Virulence:', testSpore.virulence
    print 'Population:', int(_N)
    print 'Iterations:', n + 1
    print 'Dimensions: %i x %i' % (DIMENSION, DIMENSION)
    print 'Total calories:', _calories
    print 'Average stored: %.01f' % (sum(npc.foods for npc in NPCs)/_N,)

if __name__ == '__main__':
    main()


##for person in (Alice, Bob, Claire, Debbie, Eve):
##    print person
##    print person.immunities
##    print person.infections
##    print

##p([sorted((l.food.amount, l.coords) for l in N)])


##
##    >>> l = s.get(21, 40)
##    >>> l
##    <__main__.Location instance at 0xb663122c>
##    >>> l.occupants.append(Alice)
##    >>> m = s.getOrMake(21, 42)
##    >>> m.occupants.append(Bob)
##    >>> 
##    [DEBUG ON]
##    >>> Alice.program(l)
