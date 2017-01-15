from vtk_classes.vtk_animation_timer_callback import VTKAnimationTimerCallback
import unittest

class TestIdArray(unittest.TestCase):

    def test_add_del(self):
        point_displayer = vtk_classes.VTKDisplayer(htmvis.TMVisualizer, tm, mgc_e)

        if len(tm.columnDimensions) > 1:
            height = tm.columnDimensions[1]
        else:
            height = 1

        htmvis.add_array(point_displayer, [tm.cellsPerColumn, tm.columnDimensions[0], height], [0, 1, 0], [0, 1, 0],
                         [int(128), int(66), int(21)])
        point_displayer.set_poly_data()
        point_displayer.visualize()



if __name__ == '__main__':
    unittest.main()