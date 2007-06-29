#!/usr/bin/env python
import random
import curses
from util import StarvationError
from space import Space, _calories
from curses_sbonu import _stdscr

# Width and height of the "map".
DIMENSION = 50


# Support for picking a random direction to travel.
_R = (-1, 0, 1)
_spots = tuple((x, y) for x in _R for y in _R if x or y)
# _spots now contains deltas which, if added to x, y coordinates will let
# an NPC move one "space" in one of 8 directions.


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
        if chain is None: chain = []
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
            chain = [chain[0]] + chain[-6:]
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
            self.register(person)
            return True
        return False

    def register(self, person):
        self.chain.append(person)

    def spawn(self):
        '''
        Create and return a new spore of the genus of this spore and pass
        it self's chain of "vectors".
        '''
        return self.__class__(self.genus, self.chain)

    def act(self, person):
        if random.random() <= 0.05:
            if person.foods <= 100:
                return
##            print person, 'has acted on', self
            person.foods -= 20
            author = self.chain[0]
            cut = 6
            for ancestor in self.chain[:-7:-1]:
                if ancestor.foods: # not dead..  FIXME
                    ancestor.foods += 1
                    cut -= 1
            assert 0 <= cut <= 6
            author.foods += 14 + cut


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

        # Set when the person enters a Space.
        self.space = None

    def immuneResponse(self, spore):
        '''
        Resolve an attempt of spore to infect self.  Either an infection
        occurs, or the attempt fails and a resistance to the genus of the
        spore is built up somewhat.

        Returns bool indicating whether "immune system" has "fought off"
        the attempt: True for no infection, False for infection.
        '''
        infected = spore.infects(self)

        # Regardless, maybe we tithe..
        spore.act(self)

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
        Create a clone of self at location.
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
        Given self's current location, run a "program" of actions.
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


#########################################################################

from time import sleep

class VIP_NPC(NPC):
    def reproduce(self):
        pass

Alice = VIP_NPC()
Bob, Claire, Debbie, Eve = (NPC() for _ in range(4))

ppl = (Alice, Bob, Claire, Debbie, Eve)
NPCs = tuple(NPC() for _ in range(55)) + ppl

class testSpore(Spore):
    virulence = 0.05

S = Spawner('cats', Alice, testSpore)

##Alice.afflict(Bob)
##Bob.afflict(Claire)
##Claire.afflict(Debbie)
##Debbie.afflict(Eve)

s = Space(DIMENSION, food_growth_rate=30)

R = random.randint
for person in NPCs:
    x, y = R(0, DIMENSION - 1), R(0, DIMENSION - 1)
    s.enter(x, y, person)

for _ in range(3):
    s.generate()

##print str(s)


def onestep(n, w):
    s.run()
    s.generate()

    POP = list(s.yieldPeople())
    _N = float(len(POP))

    fud = sum(
        loc.food.amount
        for loc in s.space.itervalues()
        if loc.food
        )

    infected = sum(1 for npc in POP if npc.infections)/_N
    if infected < 0.008:
        return 'break'

    f = lambda npc: not npc.infections and npc.immunities.get('cats')  == 1
    immune = sum(1 for npc in POP if f(npc))/_N

##    print '%s %.02f %.02f %05i %-3i %i' % (str(s), infected, immune, n, int(_N), Alice.foods)
    global _stdscr
    s.refresh()
    status = '%.02f %.02f %05i %-i' % (infected, immune, n, int(_N))
    _stdscr.addstr(DIMENSION - 1, DIMENSION, status)
    _stdscr.refresh()

##    print '%s %.02f %.02f %05i %-i' % (str(s), infected, immune, n,
##                                       int(_N))
##    print '%.02f %.02f %05i %-i' % (infected, immune, n, int(_N))

##    row = (n, infected, immune, _N, fud)
##    w.writerow(row)

    if infected + immune == 1:
        return 'break'
##    print ' '.join('%04i' % (npc.foods,) for npc in NPCs)

def deinit_curses():
    global _stdscr
    _stdscr.clear();
    _stdscr.move(0,0);
    curses.nocbreak()
    _stdscr.keypad(0)
    curses.curs_set(1)
    curses.echo()
    curses.endwin()

def main():
##    import csv
##    writer = csv.writer(open("sbonu.csv", "wb"))
    writer = None

    step_delay = 1.0/23

    try:
        for n in range(10000):
            if onestep(n, writer):
                break
            else:
                key = _stdscr.getch()
                if (key == ord('q')) or (key == ord('Q')):
                    break
                elif key == ord('+'):
                    step_delay *= 0.5
                elif key == ord('-'):
                    step_delay *= 1.5
                sleep(step_delay)

        POP = list(s.yieldPeople())
        _N = float(len(POP))

    finally:
        deinit_curses()

    print 'Virulence:', testSpore.virulence
    print 'Initial Population:', len(NPCs)
    print 'Eventual Population:', _N
    print 'Iterations:', n + 1
    print 'Dimensions: %i x %i' % (DIMENSION, DIMENSION)
    print 'Total calories:', _calories
    print 'Average stored: %.01f' % (sum(npc.foods for npc in POP)/_N,)

if __name__ == '__main__':
    main()

