import random
from weakref import ref


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
        return self.spore_class(self.genus, [ref(self.Author)])


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
        chain = [wref for wref in chain if wref()]
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
	def callback(wref):
            try:
                self.chain.remove(wref)
            except ValueError:
                pass
        self.chain.append(ref(person, callback))

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

            author = self.chain[0]()
            if not author:
                return

            person.foods -= 20
            cut = 6
            for ancestor in self.chain[:-7:-1]:
                ancestor = ancestor()
                if ancestor:
                    ancestor.foods += 1
                    cut -= 1

            author.foods += 14 + cut


class Infectable:
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


