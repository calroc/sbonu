#!/usr/bin/env python
import unittest
import spores


class Test_appendWeakref(unittest.TestCase):
    
    def test_appendWeakref(self):
        class Foo: pass
        foo = Foo()
        el = []

        n = spores._appendWeakref(el, foo)

        self.assert_(n is el)
        self.assert_(len(n) == 1)

        w = n[0]
        self.assert_(isinstance(w, spores.ref))
        self.assert_(w() is foo)

        del foo
        self.assert_(len(n) == 0)
        self.assert_(w() is None)


class DummyNPC:
    def infection(self, spore):
        self.testor.assert_(spore.genus == 'genus')
        self.testor.assert_(isinstance(spore, DummySpore))


class DummySpore:
    def __init__(self, genus, chain):
        self.genus = genus
        npc = chain[0]()
        npc.testor.assert_(len(chain) == 1)
        npc.testor.assert_(genus == 'genus')


class TestSpawner(unittest.TestCase):
    
    def test_Spawner(self):
        npc = DummyNPC()
        npc.testor = self
        spores.Spawner('genus', npc, DummySpore)


if __name__ == '__main__':
    unittest.main()
