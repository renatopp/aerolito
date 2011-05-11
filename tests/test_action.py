# -*- coding:utf-8 -*-
import unittest

class TestAction(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.pattern import Action
        return Action(*args, **kw)

    def getStub(self):
        return lambda x, y, environ: x+y

    def test_init(self):
        stub = self.getStub()
        action = self.getTarget(stub, [1, 2, 3])
        
        assert action._function == stub
        assert len(action._params) == 3

    def test_run(self):
        stub = self.getStub()
        action = self.getTarget(stub, None)

        assert action.run([2, 3], None) == 5
        
if __name__ == '__main__':
    unittest.main()
