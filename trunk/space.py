'''

space.py - Encapsulates the world.  (Which is currently a 2D plane Toroid.

'''
import random
import curses
from util import StarvationError
from curses_sbonu import (
    _stdscr,
    RED_BLACK,
    GREEN_BLACK,
    BLUE_BLACK,
    BLACK_BLACK
    )


# Global count of all "food" that has been put in play.
_calories = 0


class Space:
    '''
    Represents a 2-D grid and supports various behaviors.
    '''

    def __init__(self, dimension, food_growth_rate=30):
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
            for person in location.occupants[:]:
                try:
                    person.program(location)
                except StarvationError:
                    location.leave(person)
                    # This should be sufficient to cause the person to be
                    # garbage-collected.

    def yieldPeople(self):
        '''
        Iterate through all the people in the space.
        '''
        for location in self.space.itervalues():
            for person in location.occupants:
                yield person

    def __str__(self):
        return '\n'.join(''.join(self._row(x)) for x in range(self.dim))

    def refresh(self):
        global _stdscr
        for y in range(self.dim):
            _stdscr.move(y, 0)
            _stdscr.clrtoeol()
            for x in range(self.dim):
                L = self.get(x,y)
                if L:
                    _stdscr.addstr(y, x, str(L), L.colour())

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

    def colour(self):
        # Returns a color_pair (possibly with attribute).
        n = len(self.occupants)
        if n:
            if n == 1:
                occ = self.occupants[0]
                if occ.infections:
                    return curses.color_pair(RED_BLACK)
                else:
                    return curses.color_pair(BLUE_BLACK)
            elif n > 9:
                return curses.color_pair(BLUE_BLACK)
            else:
                return curses.color_pair(BLUE_BLACK)
        elif self.food:
            return curses.color_pair(GREEN_BLACK)
        return curses.color_pair(BLACK_BLACK) | curses.A_BOLD

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
