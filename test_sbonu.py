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

        result = self.npc.reproduce()
        self.assert_(bool(result))
        self.assert_(self.npc.immunities == result.immunities)
        self.assert_(self.npc.infections == result.infections)
        self.assert_(self.npc.foods == result.foods)
        self.assert_(not self.npc.turns_o_plenty)

    def tearDown(self):
        self.npc = None


if __name__ == '__main__':
    unittest.main()
