# !/usr/bin/env python

import vtk
import math as m
import time
import bisect
import numpy as np
from vtk.util import numpy_support

from idarray import IdArray

global_keyDic = None

global_interactor_parent = None

global_camera = None
global_camera_renderWindow = None


def clamp(n, min_n, max_n):
    # http://stackoverflow.com/a/5996949
    return max(min(max_n, n), min_n)







class TimerCallback(object):
    __slots__ = ["points", "point_colors", "timer_count", "points_poly",
                 "lines", "lines_poly", "line_colors", "line_id_array"
                 "last_velocity_update", "unused_locations",
                 "last_color_velocity_update", "renderer", "last_bg_color_velocity_update"]

    def add_lines(self, lines, line_colors):
        ids = []
        np_data = numpy_support.vtk_to_numpy(self.lines.GetData())

        np_color_data = numpy_support.vtk_to_numpy(self.line_colors)
        if isinstance(lines[0], (list, tuple, np.ndarray, np.generic)):
            ids.append(range(int(len(np_data)/3), int((len(np_data)+len(lines))/3)))
            np_data = np.append(np_data, lines)
            if len(np_color_data)>0:
                np_color_data = np.append(np_color_data, line_colors, axis=0)
            else:
                np_color_data = line_colors
        else:
            ids.append(int(len(np_data) / 3))
            np_data = np.append(np_data, lines)
            if len(np_color_data)==0:
                np_color_data = [line_colors]
            else:
                np_color_data = np.append(np_color_data, [line_colors], axis=0)

        vtk_data = numpy_support.numpy_to_vtkIdTypeArray(np_data, deep=True)
        self.lines.SetCells(int(len(np_data) / 3), vtk_data)

        vtk_data = numpy_support.numpy_to_vtk(num_array=np_color_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        self.line_colors.DeepCopy(vtk_data)

        #self.lines_poly.SetPoints(self.points)
        #self.lines_poly.SetLines(self.lines)
        #self.lines_poly.GetCellData().SetScalars(self.line_colors)
        self.lines_poly.Modified()

        self.line_id_array.add_ids(ids)
        return ids

    def del_all_lines(self):
        vtk_data = numpy_support.numpy_to_vtkIdTypeArray(np.array([], dtype=np.int64), deep=True)
        self.lines.SetCells(0, vtk_data)

        vtk_data = numpy_support.numpy_to_vtk(num_array=np.array([]), deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        self.line_colors.DeepCopy(vtk_data)

        self.lines_poly.Modified()

    def del_lines(self, line_indices):
        np_data = numpy_support.vtk_to_numpy(self.lines.GetData())

        np_color_data = numpy_support.vtk_to_numpy(self.line_colors)

        if isinstance(line_indices, (tuple, list)):
            last_loc = -1
            loc = 0
            np_new_data = []
            np_new_color_data = []
            for i in range(len(line_indices)):
                loc = self.line_id_array.pop_id(line_indices[i])

                np_new_data = np.concatenate([np_new_data,np_data[(last_loc+1)*3:loc*3]])
                np_new_color_data = np.concatenate([np_new_color_data,np_color_data[(last_loc+1)*3:loc*3]])

                last_loc = loc

            last_loc = loc
            loc = len(np_data)/3

            np_data = np.concatenate([np_new_data, np_data[(last_loc + 1) * 3:loc * 3]])
            np_color_data = np.concatenate([np_new_color_data, np_color_data[(last_loc + 1) * 3:loc * 3]])

        else:
            loc = self.line_id_array.pop_id(line_indices)
            arr_1 = np_data[0:loc*3]
            arr_2 = np_data[(loc + 1) * 3:len(np_data)]
            np_data = np.concatenate([arr_1, arr_2])
            np_color_data = np.concatenate([np_color_data[0:loc*3], np_color_data[(loc + 1) * 3:len(np_color_data)]])

        vtk_data = numpy_support.numpy_to_vtkIdTypeArray(np_data, deep=True)
        self.lines.SetCells(int(len(np_data) / 3), vtk_data)

        vtk_data = numpy_support.numpy_to_vtk(num_array=np_color_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        self.line_colors.DeepCopy(vtk_data)

        self.lines_poly.Modified()


    def del_points(self, point_indices):
        if isinstance(point_indices, (tuple, list)):
            for i in range(len(point_indices)):
                # move point to cornfield so nobody sees it
                # todo:remove from displayer
                self.points.SetPoint(point_indices[i], (float("nan"), float("nan"), float("nan")))
                # self.points.SetPoint(point_indices[i], (float("-inf"),float("-inf"),float("-inf")))
                # self.points.SetPoint(point_indices[i], (float("inf"),float("inf"),float("inf")))

                bisect.insort_right(self.unused_locations, point_indices[i])
        else:
            self.points.SetPoint(point_indices, (float("nan"), float("nan"), float("nan")))
            bisect.insort_right(self.unused_locations, point_indices)
        self.points_poly.Modified()

    def add_points(self, points, point_indices=None):
        # todo: keep array of no longer used point locations
        ids=[]

        if isinstance(points[0], (list, tuple)):
            if point_indices is not None:
                for i in range(len(points)):
                    ids.append(self.points.InsertPoint(point_indices[i], points[i]))
            else:
                for i in range(len(points)):
                    if len(self.unused_locations) > 0:
                        ids.append(self.unused_locations.pop(0))
                        self.points.SetPoint(ids[-1], points[i])
                    else:
                        ids.append(self.points.InsertNextPoint(points[i]))
        else:
            if len(self.unused_locations) > 0:
                ids.append(self.unused_locations.pop(0))
                self.points.SetPoint(ids[-1], points)
            else:
                ids.append(self.points.InsertNextPoint(points))
        self.points_poly.Modified()

        return ids

    def set_bg_color(self, color):
        r, g, b = color
        self.renderer.SetBackground((clamp(r, 0, 1), clamp(g, 0, 1), clamp(b, 0, 1)))
        self.renderer.Modified()

    def move_bg_color(self, color):
        r, g, b = color
        r0, b0, g0 = self.renderer.GetBackground()
        self.renderer.SetBackground((clamp(r + r0, 0, 1), clamp(g + g0, 0, 1), clamp(b + b0, 0, 1)))
        self.renderer.Modified()

    def apply_velocity_to_bg_color(self, color):
        t = time.clock() - self.last_color_velocity_update
        r, g, b = color
        r0, b0, g0 = self.renderer.GetBackground()
        self.renderer.SetBackground((clamp(r * t + r0, 0, 1), clamp(g * t + g0, 0, 1), clamp(b * t + b0, 0, 1)))
        self.renderer.Modified()
        self.last_bg_color_velocity_update = time.clock()

    def set_all_point_colors(self, color):
        np_color_data = numpy_support.vtk_to_numpy(self.point_colors)
        np_color_data = np.tile(color, (np_color_data.shape[0],1))
        vtk_data = numpy_support.numpy_to_vtk(num_array=np_color_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        self.point_colors.DeepCopy(vtk_data)

    def set_point_colors(self, colors, point_indices=None):
        if point_indices==None:
            if isinstance(colors, (list, tuple)):
                vtk_data = numpy_support.numpy_to_vtk(num_array=colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
                self.point_colors.DeepCopy(vtk_data)
            else:
                r, g, b = colors
                self.point_colors.SetTypedTuple(point_indices, [int(r % 255), int(g % 255), int(b % 255)])
        elif isinstance(point_indices, (list, tuple,np.ndarray, np.generic)):
            np_color_data = numpy_support.vtk_to_numpy(self.point_colors)
            np_color_data[point_indices] = colors
            vtk_data = numpy_support.numpy_to_vtk(num_array=np_color_data, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
            self.point_colors.DeepCopy(vtk_data)

        # self.points_poly.GetPointData().GetScalars().Modified()
        self.points_poly.Modified()

    def setup_lerp_all_point_colors(self, color, fade_time):
        np_color_data = numpy_support.vtk_to_numpy(self.point_colors)
        self.next_colors = np.tile(color, (np_color_data.shape[0],1))
        self.prev_colors = numpy_support.vtk_to_numpy(self.point_colors)

        self.lerp_fade_time = fade_time
        self.remaining_lerp_fade_time = fade_time

    def lerp_point_colors(self, colors, fade_time, point_indices=None):
        if isinstance(self.next_colors, (np.ndarray, np.generic)):
            if isinstance(point_indices, (list, tuple,np.ndarray, np.generic)):
                self.next_colors[point_indices] = colors
            else:
                self.next_colors = colors
            self.next_color_indices = None
        elif isinstance(point_indices, (list, tuple,np.ndarray, np.generic)) or isinstance(colors, (list, tuple)):
            if self.lerp_fade_time > 0:
                self.next_colors = np.append(self.next_colors, colors)
                if point_indices is not None:
                    self.next_color_indices = np.append(self.next_color_indices, point_indices)
            else:
                self.next_colors = colors
                self.next_color_indices = point_indices
                #must should not already be lerping
                self.prev_colors = numpy_support.vtk_to_numpy(self.point_colors)
        #fade time in seconds, float
        self.lerp_fade_time = fade_time
        self.remaining_lerp_fade_time = fade_time

    def set_lerp_remainder(self, lerp_remainder):
        self.lerp_multiplier = 1 - lerp_remainder

    def _calculate_point_color_lerp(self):

        #print(self.remaining_lerp_fade_time)

        if self.remaining_lerp_fade_time >0:

            #print(self.lerp_fade_time, self.remaining_lerp_fade_time)

            lerp_val = self.lerp_multiplier*(self.lerp_fade_time - self.remaining_lerp_fade_time)/self.lerp_fade_time

            #print(lerp_val)

            diff_array = ( self.prev_colors - self.next_colors)

            lerp_diff_array = diff_array*lerp_val

            #print(lerp_diff_array)

            lerp_colors = self.prev_colors - lerp_diff_array

            #print(lerp_colors)

            if isinstance(lerp_colors, (np.ndarray, np.generic)):
                vtk_data = numpy_support.numpy_to_vtk(num_array=lerp_colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
                self.point_colors.DeepCopy(vtk_data)

            # self.points_poly.GetPointData().GetScalars().Modified()
            self.points_poly.Modified()

            self.remaining_lerp_fade_time -= self.loop_change_in_time
            #print(self.remaining_lerp_fade_time)


    def position_points(self, positions, point_indices=None):
        if point_indices==None:
            vtk_data = numpy_support.numpy_to_vtk(num_array=positions, deep=True, array_type=vtk.VTK_FLOAT)
            self.points.DeepCopy(vtk_data)
        elif isinstance(point_indices, (list, tuple)):
            if isinstance(positions, (list, tuple)):
                for i in range(len(point_indices)):
                    x, y, z = positions[i % len(positions)]
                    self.points.SetPoint(point_indices[i], (x, y, z))
            else:
                for i in range(len(point_indices)):
                    x, y, z = positions
                    self.points.SetPoint(point_indices[i], (x, y, z))
        else:
            x, y, z = positions
            self.points.SetPoint(point_indices, (x, y, z))
        self.points_poly.Modified()

    def add_key_input_functions(self, keydic):
        self.interactor_style.append_input_keydic(keydic)

    def __init__(self):
        self.timer_count = 0
        self.last_velocity_update = time.clock()
        self.last_color_velocity_update = time.clock()
        self.last_bg_color_velocity_update = time.clock()
        self._loop_time = time.clock()
        self.unused_locations = []
        self.remaining_lerp_fade_time = 0
        self.lerp_multiplier = 1
        self.line_id_array = IdArray()

    def start(self):
        pass

    def loop(self, obj, event):
        self.loop_change_in_time = time.clock() - self._loop_time
        self._loop_time = time.clock()
        self._calculate_point_color_lerp()
        pass

    def end(self):
        pass

    def execute(self, obj, event):
        self.start()
        self.loop(obj, event)

        self.points_poly.GetPointData().GetScalars().Modified()
        self.points_poly.Modified()

        interactive_renderer = obj
        interactive_renderer.GetRenderWindow().Render()


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, camera, render_window, parent=None):
        # should work with else statement, but doesnt for some reason

        global global_interactor_parent
        global_interactor_parent = vtk.vtkRenderWindowInteractor()
        if parent is not None:
            global_interactor_parent = parent

        #DO NOT REMOVE GLOBAL INSTANTIATIONS!
        #due to problems with vtk losing data when moving python classes through c++, these globals muse be used to pass
        # data between class functions
        #todo: try different python class types, such as inheriting from 'object' and defining class variables

        global global_camera
        global_camera = camera

        global global_camera_renderWindow
        global_camera_renderWindow = render_window

        global global_keyDic
        global_keyDic = {
            'RECALC': self.recalc_dic,
            'w': self._move_forward,
            's': self._move_backward,
            'a': self._yaw_left,
            'd': self._yaw_right,
            'Shift_L': self._pitch_up,
            'space': self._pitch_down
        }

        global global_keys_down
        global_keys_down = []

        self.AddObserver("KeyPressEvent", self.keyPress)
        self.AddObserver("KeyReleaseEvent", self.keyRelease)
        # self.RemoveObservers("LeftButtonPressEvent")
        # self.AddObserver("LeftButtonPressEvent", self.dummy_func)

        # todo: dummy func
        # self.RemoveObservers("RightButtonPressEvent")
        # self.AddObserver("RightButtonPressEvent", self.dummy_func_2)

    def dummy_func(self, obj, ev):
        self.OnLeftButtonDown()

    def dummy_func_2(self, obj, ev):
        pass

    def append_input_keydic(self, keydic):
        """Keydic must be a dictionary of vtk key strings containing either a keydic or a function"""
        global_keyDic.update(keydic)


    def _move_forward(self):
        # todo: change this to a velocity function with drag and let something else
        # interpolate the velocity over time
        norm = global_camera.GetViewPlaneNormal()
        pos = global_camera.GetPosition()
        global_camera.SetPosition(pos[0] - norm[0] * 10,
                                  pos[1] - norm[1] * 10,
                                  pos[2] - norm[2] * 10)
        global_camera.SetFocalPoint(pos[0] - norm[0] * 20,
                                    pos[1] - norm[1] * 20,
                                    pos[2] - norm[2] * 20)

    def _move_backward(self):
        # todo: change this to a velocity function with drag and let something else
        # interpolate the velocity over time
        norm = global_camera.GetViewPlaneNormal()
        pos = global_camera.GetPosition()
        global_camera.SetPosition(pos[0] + norm[0] * 10,
                                  pos[1] + norm[1] * 10,
                                  pos[2] + norm[2] * 10)
        global_camera.SetFocalPoint(pos[0] - norm[0] * 20,
                                    pos[1] - norm[1] * 20,
                                    pos[2] - norm[2] * 20)

    def _yaw_right(self):
        global_camera.Yaw(-10)
        global_camera_renderWindow.GetInteractor().Render()

    def _yaw_left(self):
        global_camera.Yaw(10)
        global_camera_renderWindow.GetInteractor().Render()

    def _pitch_up(self):
        global_camera.Pitch(10)
        global_camera_renderWindow.GetInteractor().Render()

    def _pitch_down(self):
        global_camera.Pitch(-10)
        global_camera_renderWindow.GetInteractor().Render()

    def recalc_dic(self):
        """calls all the functions in the key dictionary
        recursively goes through keydics containing keydics until a function is reached"""

        global global_keys_down
        print(global_keys_down)
        i = [0]
        key_dic = [global_keyDic]
        while True:
            if isinstance(key_dic[-1][global_keys_down[i[-1]]], dict):
                key_dic.append(key_dic[-1][global_keys_down[i[-1]]])
                i.append(0)
            elif callable(key_dic[-1][global_keys_down[i[-1]]]):
                key_dic[-1][global_keys_down[i[-1]]]()
            if i[-1] < len(global_keys_down)-1:
                i[-1]+=1
            elif len(i) > 1:
                i.pop()
                key_dic.pop()
            else:
                break

    # noinspection PyPep8Naming
    def keyPress(self, obj, event):
        key = global_interactor_parent.GetKeySym()
        if key not in global_keys_down:
            global_keys_down.append(key)
            global_keyDic['RECALC']()

    def keyRelease(self, obj, event):
        key = global_interactor_parent.GetKeySym()
        global_keys_down.remove(key)

class PointDisplayer:
    # adapted from:
    # http://www.vtk.org/Wiki/VTK/Examples/Python/GeometricObjects/Display/Point
    def __init__(self, callback_class, *args, **kwargs):
        self.points = vtk.vtkPoints()
        self.vertices = vtk.vtkCellArray()

        self.point_colors = vtk.vtkUnsignedCharArray()
        self.point_colors.SetNumberOfComponents(3)
        self.point_colors.SetName("Colors")

        self.lines = vtk.vtkCellArray()

        self.line_colors = vtk.vtkUnsignedCharArray()
        self.line_colors.SetNumberOfComponents(3)
        self.line_colors.SetName("Colors")

        assert issubclass(callback_class, TimerCallback)
        self.callback_class = callback_class
        self.callback_class_args = args
        self.callback_class_kwargs = kwargs

    # def add_point(self, x, y, z):
    #    point = [x,y,z]
    #    self.add_point(point)

    def add_point(self, point, color):
        point_id = self.points.InsertNextPoint(point)
        self.vertices.InsertNextCell(1)
        self.vertices.InsertCellPoint(point_id)

        self.point_colors.InsertNextTypedTuple(color)

        return point_id

    def add_line(self, point_a_index, point_b_index, color):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, point_a_index)
        line.GetPointIds().SetId(1, point_b_index)

        line_id = self.lines.InsertNextCell(line)

        self.line_colors.InsertNextTypedTuple(color)
        return line_id

    def set_poly_data(self):
        self.points_poly = vtk.vtkPolyData()
        self.points_poly.SetPoints(self.points)
        self.points_poly.SetVerts(self.vertices)

        self.points_poly.GetPointData().SetScalars(self.point_colors)

        self.lines_poly = vtk.vtkPolyData()
        self.lines_poly.SetPoints(self.points)
        self.lines_poly.SetLines(self.lines)

        self.lines_poly.GetCellData().SetScalars(self.line_colors)

    def visualize(self):
        point_mapper = vtk.vtkPolyDataMapper()
        line_mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            point_mapper.SetInput(self.points_poly)
            line_mapper.SetInput(self.lines_poly)
        else:
            point_mapper.SetInputData(self.points_poly)
            line_mapper.SetInputData(self.lines_poly)

        point_actor = vtk.vtkActor()
        line_actor = vtk.vtkActor()

        point_actor.SetMapper(point_mapper)
        line_actor.SetMapper(line_mapper)
        point_actor.GetProperty().SetPointSize(60)  # todo:allow modification
        # actor.GetProperty().SetPointColor

        renderer = vtk.vtkRenderer()

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window_interactor = vtk.vtkRenderWindowInteractor()
        interactor_style = KeyPressInteractorStyle(camera=renderer.GetActiveCamera(),
                                    render_window=render_window,
                                    parent=render_window_interactor)
        render_window_interactor.SetInteractorStyle(
            interactor_style
        )

        render_window_interactor.SetRenderWindow(render_window)

        renderer.AddActor(point_actor)
        renderer.AddActor(line_actor)

        # light brown = .6,.6,.4
        # light brown = .2,.2,.1
        # dark brown = .2, .1, 0
        # dusk = .05, .05, .1
        # calm blue sky = .1, .2, .4
        # day blue sky = .2, .4, .8
        # bright blue sky = .6, .8, 1.0 (bg attention activation)
        renderer.SetBackground(66/255.0,132/255.0,125/255.0)  # todo:allow modification

        render_window.Render()

        render_window_interactor.Initialize()

        cb = self.callback_class(*self.callback_class_args, **self.callback_class_kwargs)
        cb.interactor_style = interactor_style #allow adding/removing input functions
        cb.renderer = renderer
        cb.points = self.points
        cb.points_poly = self.points_poly
        cb.point_colors = self.point_colors
        cb.lines = self.lines
        cb.lines_poly = self.lines_poly
        cb.line_colors = self.line_colors

        render_window_interactor.AddObserver('TimerEvent', cb.execute)
        timer_id = render_window_interactor.CreateRepeatingTimer(10)
        render_window_interactor.Start()

        # after loop
        cb.end()


def show_landscape(point_displayer):
    from opensimplex import OpenSimplex
    import random

    simplex_r = OpenSimplex(seed=364)
    simplex_g = OpenSimplex(seed=535)
    simplex_b = OpenSimplex(seed=656)

    for i in range(100000):
        x = random.randint(0, 1000, 4237842 + i)
        y = random.randint(0, 1000, 5437474 + i)

        r1 = .0009765625 * (simplex_g.noise2d(x=x, y=y))
        r2 = .001953125 * (simplex_r.noise2d(x=x / 2.0, y=y / 2.0))
        r3 = .00390625 * (simplex_b.noise2d(x=x / 4.0, y=y / 4.0, ))
        r4 = .0078125 * (simplex_g.noise2d(x=x / 8.0, y=y / 8.0))
        r5 = .015625 * (simplex_r.noise2d(x=x / 16.0, y=y / 16.0))
        r6 = .03125 * (simplex_b.noise2d(x=x / 32.0, y=y / 32.0))
        r7 = .0625 * (simplex_g.noise2d(x=x / 64.0, y=y / 64.0))
        r8 = .125 * (simplex_r.noise2d(x=x / 128.0, y=y / 128.0))
        r9 = .25 * (simplex_b.noise2d(x=x / 256.0, y=y / 256.0))
        normalization_factor = .5
        val = ((r1 + r2 + r3 + r4 + r5 + r6 + r7 + r8 + r9) / 2.0)
        if val > 0:
            p = 1.0
        else:
            p = -1.0
        norm_val = (abs(val) ** normalization_factor) * p
        pos_val = (norm_val + 1.0) / 2.0
        z = pos_val * 254.0

        point_displayer.add_point([x - 100, y - 100, z - 100], [160, int(z), 20])


def show_cloud(point_displayer):
    from opensimplex import OpenSimplex
    import math
    import random

    simplex_r = OpenSimplex(seed=364)
    simplex_g = OpenSimplex(seed=535)
    simplex_b = OpenSimplex(seed=656)

    for i in range(100000):

        x = random.randint(0, 1000)
        y = random.randint(0, 1000)
        z = random.randint(0, 1000)

        d = math.sqrt((x - 500) ** 2 + (y - 500) ** 2 + (z - 500) ** 2) / 500.0

        r1 = .0009765625 * (simplex_g.noise3d(x=x, y=y, z=z))
        r2 = .001953125 * (simplex_r.noise3d(x=x / 2.0, y=y / 2.0, z=z / 2.0))
        r3 = .00390625 * (simplex_b.noise3d(x=x / 4.0, y=y / 4.0, z=z / 4.0))
        r4 = .0078125 * (simplex_g.noise3d(x=x / 8.0, y=y / 8.0, z=z / 8.0))
        r5 = .015625 * (simplex_r.noise3d(x=x / 16.0, y=y / 16.0, z=z / 16.0))
        r6 = .03125 * (simplex_b.noise3d(x=x / 32.0, y=y / 32.0, z=z / 32.0))
        r7 = .0625 * (simplex_g.noise3d(x=x / 64.0, y=y / 64.0, z=z / 64.0))
        r8 = .125 * (simplex_r.noise3d(x=x / 128.0, y=y / 128.0, z=z / 128.0))
        r9 = .25 * (simplex_b.noise3d(x=x / 256.0, y=y / 256.0, z=z / 256.0))
        r10 = .5 * (simplex_g.noise3d(x=x / 512.0, y=y / 512.0, z=z / 512.0))
        r11 = (simplex_r.noise3d(x=x / 1024.0, y=y / 1024.0, z=z / 1024.0))
        val = ((r1 + r2 + r3 + r4 + r5 + r6 + r7 + r8 + r9) / 2.0)
        if val > 0:
            p = 1.0
        else:
            p = -1.0

        # use ^d for cumulus clouds,
        # use distance from a certain height for a sky of clouds
        # use constant power <1 for endless 3d field of clouds
        # use distance from sets of points or lines for other shapes

        norm_val = (abs(val) ** d) * p
        pos_val = (norm_val + 1.0) / 2.0
        r = int(pos_val * 254.0)
        # r5 = int((r5)*255.0/2.0)
        # lim octaves->inf gives 1/2^x sum (=1)
        if r > 160:
            point_displayer.add_point([x, y, z], [r, r, r])


def show_rand_line_cube(point_displayer):
    import random as rand

    line_a = rand.sample(range(0, 500), 500)
    line_b = rand.sample(range(500, 1000), 500)

    for i in range(len(line_a)):
        r = rand.randint(0, 255, 5453476 + i)
        g = rand.randint(0, 255, 5983279 + i)
        b = rand.randint(0, 255, 9827312 + i)
        point_displayer.add_line(line_a[i], line_b[i], [r, g, b])


def normalize(a, axis=-1, order=2):
    # from: http://stackoverflow.com/a/21032099
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2 == 0] = 1
    return a / np.expand_dims(l2, axis)


def add_array(point_displayer, widths, normal, center, color):
    true_normal = normalize(normal)
    if not np.allclose(true_normal, [1, 0, 0]):
        zn = np.cross(true_normal, [1, 0, 0])
        xn = np.cross(true_normal, zn)
    else:
        xn = [1, 0, 0]
        zn = [0, 0, 1]
    for z in range(-int(m.floor(widths[2] / 2.0)), int(m.ceil(widths[2] / 2.0))):
        for y in range(-int(m.floor(widths[1] / 2.0)), int(m.ceil(widths[1] / 2.0))):
            for x in range(-int(m.floor(widths[0] / 2.0)), int(m.ceil(widths[0] / 2.0))):
                vector_space_matrix = np.column_stack((np.transpose(xn), np.transpose(true_normal), np.transpose(zn)))
                translation = np.matmul([x, y, z * 20], vector_space_matrix)
                point_location = [center[0], center[1], center[2]] + translation
                point_displayer.add_point(point_location, color)


def add_n_poly_prism(point_displayer, radius, normal, bottom_center, color):
    pass

import random
import colorsys
class TestPointLoop(TimerCallback):
    def __init__(self):
        #super().__init__()
        super(TestPointLoop, self).__init__()

    def loop(self, obj, event):
        rand_points=[2, random.randint(0,40*40*2-1),random.randint(0,40*40*2-1)]

        if len(self.line_id_array)>0 and random.randint(0,10)<9:
            self.del_lines(0)
        self.add_lines(rand_points, [128,99,21])

        if random.randint(0,40)==1:
            self.del_all_lines()
            self.set_all_point_colors([int(128), int(66), int(21)])

        rand_points = np.array([random.randint(0,40*40*2-1) for x in range(20)])
        rand_colors = np.array([[ 85,36,0] for x in range(10)])
        rand_colors = np.append( rand_colors, [([212,151,106])for x in range(10)], axis=0)

        self.set_point_colors(rand_colors, rand_points)

def display_test_point_loop():
    point_displayer = PointDisplayer(TestPointLoop)
    add_array(point_displayer, [40, 40, 2], [0, 1, 0], [0, 1, 0], [int(128), int(66), int(21)])
    point_displayer.set_poly_data()
    point_displayer.visualize()

import numpy as np

class TMVisualizer(TimerCallback):
    def __init__(self, tm, encoder):
        super(TMVisualizer, self).__init__()
        self.tm = tm
        self.encoder = encoder
        self.i=0
        self.j=0
        self.columns = np.zeros((tm.columnDimensions[0],))
        self.cells = np.zeros((tm.columnDimensions[0],tm.cellsPerColumn))

        self.change_time = .020
        self.current_time = time.clock()

        self.active_cell_color = [212, 151, 106]
        self.predicted_cell_color = [85, 36, 0]
        self.winner_cell_color = [255,232,170]
        self.default_cell_color = [128, 66, 21]

        # show default cells will be added when I can add/remove points well
        self.show_predicted_cells = True
        self.show_winner_cells = True
        self.show_active_cells = True
        self.show_matching_segments = False
        self.show_active_segments = False
        self.show_all_segments = False


        self.set_lerp_remainder(.5)

    def start(self):
        super(TMVisualizer, self).start()  # needed for getting called

        # this needs to be put in start rather than init because the key interactor
        # is added after initialization
        self.add_key_input_functions({'a': self.toggle_show_active_cells,
                                      'p': self.toggle_show_predicted_cells,
                                      'w': self.toggle_show_winner_cells,
                                      'plus': self.speed_up,
                                      'minus': self.slow_down,
                                      's': self.toggle_show_active_segments,
                                      'm':self.toggle_show_matching_segments,
                                      '1': self.toggle_show_all_segments})

    def toggle_show_all_segments(self):
        self.show_all_segments = not self.show_all_segments

    def toggle_show_active_segments(self):
        self.show_active_segments = not self.show_active_segments

    def toggle_show_matching_segments(self):
        self.show_matching_segments = not self.show_matching_segments

    def slow_down(self):
        self.change_time = self.change_time + .01

    def speed_up(self):
        self.change_time = max(self.change_time-.01, 0.02) # max 50 hz

    def toggle_show_active_cells(self):
        self.show_active_cells = not self.show_active_cells

    def toggle_show_predicted_cells(self):
        self.show_predicted_cells = not self.show_predicted_cells

    def toggle_show_winner_cells(self):
        self.show_winner_cells = not self.show_winner_cells

    def set_active_cell_color(self, new_color):
        assert(isinstance(new_color, (tuple, list, np.ndarray, np.generic)))
        assert(len(new_color) == 3)
        assert(isinstance(new_color[0], int))
        self.active_cell_color = new_color

    def set_predicted_cell_color(self, new_color):
        assert (isinstance(new_color, (tuple, list, np.ndarray, np.generic)))
        assert (len(new_color) == 3)
        assert (isinstance(new_color[0], int))
        self.predicted_cell_color = new_color

    def set_winner_cell_color(self, new_color):
        assert (isinstance(new_color, (tuple, list, np.ndarray, np.generic)))
        assert (len(new_color) == 3)
        assert (isinstance(new_color[0], int))
        self.winner_cell_color = new_color

    def set_default_cell_color(self, new_color):
        assert (isinstance(new_color, (tuple, list, np.ndarray, np.generic)))
        assert (len(new_color) == 3)
        assert (isinstance(new_color[0], int))
        self.default_cell_color = new_color

    def _show_segments(self, segments, color_func):
        #
        active_links = np.array([], dtype=np.int64)
        active_link_colors = np.array([], dtype=np.int64)
        if len(segments) > 0:
            for i in segments:
                for j in i._synapses:
                    active_links = np.append(active_links, [2, i.cell, j.presynapticCell], axis=0)
                    link_color = color_func(j)
                    link_color = [int(link_color[0] * 255), int(link_color[1] * 255), int(link_color[2] * 255)]
                    if len(active_link_colors) > 0:
                        active_link_colors = np.append(active_link_colors, [link_color], axis=0)
                    else:
                        active_link_colors = [link_color]

            self.add_lines(active_links, active_link_colors)

    def _show_cells(self, cells, color_func):
        if len(cells) > 0:
            cell_colors = [color_func(c) for c in cells]
            self.lerp_point_colors(cell_colors, self.change_time, cells)

    def loop(self, obj, event):
        super(TMVisualizer, self).loop(obj,event) #needed for lerping

        if time.clock() - self.current_time > self.change_time:

            self.encoder.encodeIntoArray(self.i, self.columns)
            activeColumns = set([a for a, b in enumerate(self.columns) if b == 1])
            self.tm.compute(activeColumns, learn=True)

            if self.i % 256 == 0:
                self.tm.reset()
                self.i = 0


            self.setup_lerp_all_point_colors(self.default_cell_color, self.change_time)
            self.del_all_lines()

            if self.show_active_cells:
                self._show_cells(np.array(self.tm.getActiveCells()), lambda q: self.active_cell_color)

            if self.show_predicted_cells:
                self._show_cells(np.array(self.tm.getPredictiveCells()), lambda q: self.predicted_cell_color)

            if self.show_winner_cells:
                self._show_cells(np.array(self.tm.getWinnerCells()), lambda q: self.winner_cell_color)

            if self.show_all_segments:
                self._show_segments(self.tm.connections._segmentForFlatIdx,
                                    lambda s: colorsys.hls_to_rgb(0.200, .75 - s.permanence * .5, .5))

            if self.show_matching_segments:
                self._show_segments(self.tm.getMatchingSegments(), lambda s: colorsys.hls_to_rgb(0.941, .75 - s.permanence * .5, .71))

            if self.show_active_segments:
                self._show_segments(self.tm.getActiveSegments(), lambda s: colorsys.hls_to_rgb(0.481, .75 - s.permanence * .5, .5))

            self.i+=1

            self.current_time = time.clock()
        else:
            pass



if __name__=="__main__":
    display_test_point_loop()