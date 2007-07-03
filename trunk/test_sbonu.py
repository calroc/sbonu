#!/usr/bin/env python
import unittest
import sbonu


class TestSim(unittest.TestCase):
    
    def setUp(self):
        self.sim = sbonu.SbonuSimulation(25, 10, 0, 0)

    def test_step(self):
        self.sim.step()
        pop, infected, immune, fud = self.sim.space.getStats()

        self.assert_(fud == 10)

    def tearDown(self):
        self.sim = None


class TestNPC(unittest.TestCase):
    
    def setUp(self):
        self.npc = sbonu.NPC()

    def test_whichWay(self):
        self.npc.space = DummySpace()
        self.assert_(self.npc.whichWay() in sbonu._spots)
        self.npc.space.setValues('banana')
        self.assert_(self.npc.whichWay() == 'banana')

    def test_wander(self):
        self.npc.space = DummySpace((1, 1))
        self.npc.space.testor = self
        n = self.npc.foods
        self.npc.wander()
        self.assert_(self.npc.foods == n - 1)

    def test_clone(self):
        clone = self.npc.clone()
        self.assert_(self.npc.immunities == clone.immunities)
        self.assert_(self.npc.infections == clone.infections)
        self.assert_(self.npc.foods == clone.foods)

    def test_reproduce(self):
        self.assert_(not hasattr(self.npc, 'turns_o_plenty'))
        result = self.npc.reproduce()
        self.assert_(result is None)
        self.assert_(hasattr(self.npc, 'turns_o_plenty'))
        self.assert_(not self.npc.turns_o_plenty)

        for n in range(3):
            result = self.npc.reproduce()
            self.assert_(result is None)
            self.assert_(not self.npc.turns_o_plenty)

        self.npc.foods = self.npc.a + 1

        for n in range(3):
            result = self.npc.reproduce()
            self.assert_(result is None)
            self.assert_(self.npc.turns_o_plenty == n + 1)

        self.npc.foods = self.npc.a

        for n in range(3):
            result = self.npc.reproduce()
            self.assert_(result is None)
            self.assert_(self.npc.turns_o_plenty == 3)

        self.npc.foods = self.npc.a - 1

        for n in range(2, -1, -1):
            result = self.npc.reproduce()
            self.assert_(result is None)
            self.assert_(self.npc.turns_o_plenty == n)

        result = self.npc.reproduce()
        self.assert_(result is None)
        self.assert_(self.npc.turns_o_plenty == 0)

        self.npc.foods = self.npc.a + 1

        for n in range(self.npc.b):
            result = self.npc.reproduce()
            self.assert_(result is None)
            self.assert_(self.npc.turns_o_plenty == n + 1)

        clone = self.npc.reproduce()
        self.assert_(bool(clone))
        self.assert_(self.npc.immunities == clone.immunities)
        self.assert_(self.npc.infections == clone.infections) # I.e. none.
        self.assert_(self.npc.foods == clone.foods)
        self.assert_(not self.npc.turns_o_plenty)

    def tearDown(self):
        self.npc = None


class DummySpace:

    def __init__(self, *values):
        self.values = values

    def setValues(self, *values):
        self.values = values

    def yieldNearbyFoods(self, npc):
        for n in self.values:
            yield n

    def move(self, dx, dy, npc):
        self.testor.assert_((dx, dy) == (1, 1))
        self.testor.assert_(npc is self.testor.npc)
        return 1


if __name__ == '__main__':
    unittest.main()
