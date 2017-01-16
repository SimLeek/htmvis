from vtk_classes.vtk_animation_timer_callback import VTKAnimationTimerCallback
from vtk_classes.vtk_displayer import VTKDisplayer
import unittest
import random

#20 seconds is the approximate amount of time it would take to use up the extra memory and crash
test_time = 5

class TimedAnimationTester(VTKAnimationTimerCallback):
    def __init__(self):
        super(TimedAnimationTester, self).__init__()

        self.time_remaining = test_time

    def loop(self, obj, event):
        super(TimedAnimationTester, self).loop(obj, event)
        if self.time_remaining > 0:
            self.time_remaining -= self.loop_change_in_time
        else:
            self.time_remaining = test_time
            self.exit()
        pass

class TestIdArray(unittest.TestCase):

    def test_point_add(self):

        class PointAddTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(PointAddTester, self).loop(obj, event)
                self.add_points([[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                                [[random.randint(0,255), random.randint(0,255), random.randint(0,255)]])

        point_displayer = VTKDisplayer(PointAddTester)
        point_displayer.visualize()

    def test_line_add(self):

        class LineAddTester(TimedAnimationTester):
            def loop(self, obj, event):
                super(LineAddTester, self).loop(obj, event)
                self.add_points([[random.randint(-50, 50), random.randint(-50, 50), random.randint(-50, 50)]],
                                [[random.randint(0,255), random.randint(0,255), random.randint(0,255)]])
                if self.points.GetNumberOfPoints() > 2:
                    self.add_lines([2,random.randint(0,self.points.GetNumberOfPoints()-1),random.randint(0,self.points.GetNumberOfPoints()-1)],
                                   [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]])
                pass
        line_displayer = VTKDisplayer(LineAddTester)
        line_displayer.visualize()

    def test_point_field_add(self):
        class PointFieldTester(TimedAnimationTester):
            def at_start(self):
                self.add_point_field([20, 20, 2], [0, 1, 0], [0, 1, 0], [[int(128), int(66), int(21)]])

        line_displayer = VTKDisplayer(PointFieldTester)
        line_displayer.visualize()

if __name__ == '__main__':
    unittest.main()