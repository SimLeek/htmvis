import vtk

global_keyDic = None
global_keys_down = None

global_interactor_parent = None

global_camera = None
global_camera_renderWindow = None

class VTKKeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, camera, render_window, parent=None):
        # should work with else statement, but doesnt for some reason

        global global_interactor_parent
        global_interactor_parent = vtk.vtkRenderWindowInteractor()
        if parent is not None:
            global_interactor_parent = parent

        # DO NOT REMOVE GLOBAL INSTANTIATIONS!
        # due to problems with vtk losing data when moving python classes through c++, these globals muse be used to pass
        # data between class functions
        # todo: try different python class types, such as inheriting from 'object' and defining class variables

        global global_camera
        global_camera = camera

        global global_camera_renderWindow
        global_camera_renderWindow = render_window

        # todo: add screenshot function:
        #   http://www.vtk.org/Wiki/VTK/Examples/Python/Screenshot
        #   http://doc.qt.io/qt-4.8/qpixmap.html#grabWindow
        # todo: add window record function if ffmpeg is installed
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
            try:
                if isinstance(key_dic[-1][global_keys_down[i[-1]]], dict):
                    key_dic.append(key_dic[-1][global_keys_down[i[-1]]])
                    i[-1] += 1
                    i.append(0)
                    continue
                elif callable(key_dic[-1][global_keys_down[i[-1]]]):
                    key_dic[-1][global_keys_down[i[-1]]]()
            except KeyError:
                pass
            except IndexError:
                pass
            if i[-1] < len(global_keys_down):
                i[-1] += 1
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