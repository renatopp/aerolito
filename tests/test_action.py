# -*- coding:utf-8 -*-
import unittest

class TestAction(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.pattern import Action
        return Action(*args, **kw)

    def getStub(self):
        return lambda x, y: x+y

    def test_init(self):
        stub = self.getStub()
        action = self.getTarget(stub)
        
        assert action._function == stub

    def test_run(self):
        stub = self.getStub()
        action = self.getTarget(stub)

        assert action.run([2, 3]) == 5
        
if __name__ == '__main__':
    unittest.main()
