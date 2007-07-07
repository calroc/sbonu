#!/usr/bin/env python
import unittest
import space


class Foo: pass


class TestSpace(unittest.TestCase):
    
    def setUp(self):
        self.space = space.Space(10, 1)

    def test_personMustBeInSpace(self):
        self.assertRaises(KeyError, self.space.newLife, None, None)
        self.assertRaises(KeyError, self.space.yieldNeighbours(None).next)
        self.assertRaises(KeyError, self.space.yieldNearbyFoods(None).next)
        self.assertRaises(KeyError, self.space.move, 1, 1, None)
        self.assertRaises(KeyError, self.space.forage, None)
        self.assertRaises(KeyError, self.space.leave, None)

    def test_enter(self):
        self.assert_(self.space.get(1, 1) is None)
        foo = Foo()
        self.space.enter(1, 1, foo)
        self.assert_(list(self.space.yieldPeople()) == [foo])
        self.assert_(self.space is foo.space)
        self.assert_(self.space.get(1, 1) is not None)

    def test_leave(self):
        foo = Foo()
        self.space.enter(1, 1, foo)
        self.space.leave(foo)
        self.failIf(list(self.space.yieldPeople()))
        self.assert_(foo.space is None)
        
    def tearDown(self):
        self.space = None


if __name__ == '__main__':
    unittest.main()
