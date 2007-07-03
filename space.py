'''

space.py - Encapsulates the world.  (Which is currently a 2D plane Toroid.

'''
import random
from math import sqrt


# Global count of all "food" that has been put in play.
_calories = 0


class Space:
    '''
    Represents a 2-D grid and supports various behaviors.
    '''

    def __init__(self, dimension, food_growth_rate=30, pad=None):
        self.dim = dimension
        self.food_growth_rate = food_growth_rate
        self.pad=pad
        self.space = {}
        self.occupants = {}

    def newLife(self, parent, child):
        '''
        A parent has brought a child into the world, take note.
        '''
        location = self.occupants[parent]
        location.enter(child)
        self.occupants[child] = location
        child.space = self

    def yieldNeighbours(self, person, distance=1):
        '''
        Yield all neighbours within distance of person.
        '''
        location = self.occupants[person]
        for place in location.getNearby(distance, Location.occupied):
            for other in place.occupants:
                if other != person:
                    yield other

    def yieldNearbyFoods(self, person, distance=1):
        '''
        Yield (delta-x, delta-y) distance pairs of all food near person.
        '''
        location = self.occupants[person]
        nearby_food = location.getNearby(distance, lambda n: bool(n.food))
        x, y = location.coords
        for food_spot in nearby_food:
            xx, yy = food_spot.coords
            yield xx - x, yy - y

    def move(self, dx, dy, person):
        '''
        Move person by dx and dy, return distance travelled.
        '''

        location = self.occupants[person]

        x, y = location.coords
        x += dx; y += dy

        # Wrap at the borders.
        while x >= self.dim: x -= self.dim
        while x < 0: x += self.dim
        while y >= self.dim: y -= self.dim
        while y < 0: y += self.dim

        new_location = self.getOrMake(x, y)

        if new_location is location:
            return

        location.leave(person)
        new_location.enter(person)
        self.occupants[person] = new_location

        return int(round(sqrt(dx**2 + dy**2)))

    def forage(self, person):
        '''
        Person is looking for food, return some (as an int.)
        '''
        return self.occupants[person].eat()

    def enter(self, x, y, person):
        '''
        Person enters space at x, y.
        '''
        assert person not in self.occupants
        location = self.getOrMake(x, y)
        location.enter(person)
        self.occupants[person] = location
        person.space = self

    def leave(self, person):
        '''
        Person leaves space.
        '''
        location = self.occupants[person]
        location.leave(person)
        del self.occupants[person]
        person.space = None

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

    def _iterLocations(self):
        # Go through all locations.
        for key, location in list(self.space.items()):

            # Clean out any empty locations.
            if location.empty():
                del self.space[key]

            else:
                yield location

    def yieldPeople(self):
        '''
        Iterate through all the people in the space.
        '''
        for location in self._iterLocations():
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

    def getStats(self):
        POP = list(self.yieldPeople())
        N = float(len(POP))

        fud = sum(
            loc.food.amount
            for loc in self._iterLocations()
            if loc.food
            )

        infected = sum(1 for npc in POP if npc.infections) / N

        f = lambda npc: not npc.infections and npc.immunities.get('cats')  == 1
        immune = sum(1 for npc in POP if f(npc)) / N

        # Population, % infected, % immune
        return N, infected, immune


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
                    return '@'
                else:
                    return 'o'
            elif n > 9:
                return '+'
            else:
                return str(n)
        elif self.food:
            return 'f'
        return '.'

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
