# coding=utf-8
# !/usr/bin/env python

import math as m
import time

import numpy as np

from util.numpy_helpers import normalize
from vtk_classes.vtk_animation_timer_callback import VTKAnimationTimerCallback


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
                translation = np.matmul([x, y, z], vector_space_matrix)
                point_location = [center[0], center[1], center[2]] + translation
                print(point_location)
                point_displayer.add_point(point_location, color)


def add_n_poly_prism(point_displayer, radius, normal, bottom_center, color):
    pass


import colorsys


class TMVisualizer(VTKAnimationTimerCallback):
    def __init__(self, tm, encoder):
        super(TMVisualizer, self).__init__()
        self.tm = tm
        self.encoder = encoder
        self.i = 0
        self.j = 1.1
        self.columns = np.zeros(np.multiply.reduce(tm.columnDimensions))
        self.cells = np.zeros((np.multiply.reduce(tm.columnDimensions), tm.cellsPerColumn))

        self.change_time = .020
        self.current_time = time.clock()

        self.active_cell_color = [212, 151, 106]
        self.predicted_cell_color = [85, 36, 0]
        self.winner_cell_color = [255, 232, 170]
        self.default_cell_color = [128, 66, 21]

        # show default cells will be added when I can add/remove points well
        self.show_predicted_cells = True
        self.show_winner_cells = True
        self.show_active_cells = True
        self.show_matching_segments = False
        self.show_active_segments = False
        self.show_all_segments = False

        self.set_lerp_remainder(0.6)

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
                                      'm': self.toggle_show_matching_segments,
                                      'Shift_L': {'exclam': self.toggle_show_all_segments}})

        self.set_bg_color([128. / 255, 66. / 255, 21. / 255])

    def toggle_show_all_segments(self):
        self.show_all_segments = not self.show_all_segments

    def toggle_show_active_segments(self):
        self.show_active_segments = not self.show_active_segments

    def toggle_show_matching_segments(self):
        self.show_matching_segments = not self.show_matching_segments

    def slow_down(self):
        self.change_time = self.change_time + .01

    def speed_up(self):
        self.change_time = max(self.change_time - .01, 0.02)  # max 50 hz

    def toggle_show_active_cells(self):
        self.show_active_cells = not self.show_active_cells

    def toggle_show_predicted_cells(self):
        self.show_predicted_cells = not self.show_predicted_cells

    def toggle_show_winner_cells(self):
        self.show_winner_cells = not self.show_winner_cells

    def set_active_cell_color(self, new_color):
        assert (isinstance(new_color, (tuple, list, np.ndarray, np.generic)))
        assert (len(new_color) == 3)
        assert (isinstance(new_color[0], int))
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
            # todo: this for loop is slowing things down. Replace with numpy or gpu op somehow.
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
        super(TMVisualizer, self).loop(obj, event)  # needed for lerping

        if time.clock() - self.current_time > self.change_time:

            self.encoder.encodeIntoArray(self.i, self.columns)
            activeColumns = set([a for a, b in enumerate(self.columns) if b == 1])
            self.tm.compute(activeColumns, learn=True)

            if self.i >= 256:
                if self.j >= 1.1:
                    self.j = 1.005
                else:
                    self.j+=.005
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
                self._show_segments(self.tm.getMatchingSegments(),
                                    lambda s: colorsys.hls_to_rgb(0.941, .75 - s.permanence * .5, .71))

            if self.show_active_segments:
                self._show_segments(self.tm.getActiveSegments(),
                                    lambda s: colorsys.hls_to_rgb(0.481, .75 - s.permanence * .5, .5))

            self.i = (self.i+1)**self.j
            print(self.i)

            self.current_time = time.clock()
        else:
            pass
