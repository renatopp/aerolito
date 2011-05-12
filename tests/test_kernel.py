# -*- coding:utf-8 -*-
import unittest

class TestKernel(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.kernel import Kernel
        return Kernel(*args, **kw)

    def test_init(self):
        pass

        
if __name__ == '__main__':
    unittest.main()
