import unittest
import sbonu


class TestSim(unittest.TestCase):
    
    def setUp(self):
        self.sim = sbonu.SbonuSimulation(25, 10, 0, 0)

    def test_step(self):
        self.sim.step()
        pop, infected, immune, fud = self.sim.space.getStats()

        self.assert_(fud == 10)


if __name__ == '__main__':
    unittest.main()
