from vtk_classes.vtk_animation_timer_callback import VTKAnimationTimerCallback
from vtk_classes.vtk_displayer import VTKDisplayer
import unittest
import random

class TestIdArray(unittest.TestCase):

    def test_add(self):

        class AddTester(VTKAnimationTimerCallback):
            def __init__(self):
                super(AddTester, self).__init__()

            def loop(self, obj, event):
                super(AddTester, self).loop(obj, event)
                self.add_points([[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                                [[0, 0, 0]])
                pass
        point_displayer = VTKDisplayer(AddTester)
        point_displayer.add_point([0,0,0],[0,0,0])
        point_displayer.set_poly_data()
        point_displayer.visualize()



if __name__ == '__main__':
    unittest.main()