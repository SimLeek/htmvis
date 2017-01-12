from nupic.data import SENTINEL_VALUE_FOR_MISSING_DATA

from nupic.data.fieldmeta import FieldMetaType
from nupic.encoders.base import Encoder, EncoderResult

import numbers
import math
import numpy as np

import choice_numbers as cn

class ChoiceNumberEncoder(Encoder):

# todo: alt chooser: https://www.wolframalpha.com/input/?i=solve+for+x:+ceil(x)+choose+max(floor(x*.02),2)+%3E+2%5E8
    def __init__(self,
                 n=24,
                 on_bits=2,
                 verbosity=0,
                 name=None,
                 clipInput=True):

        assert isinstance(n, numbers.Integral)
        self.encoders = None
        self.verbosity = verbosity
        self.n = n
        self.on_bits = on_bits

        self.resolution = 1
        self.radius = float('nan')  # okay, I'll admit, this is just me having fun

        self.clipInput = clipInput


        if name is not None:
            self.name = name
        else:
            self.name = "[%s:%s]" % (0, 1)

        self._topDownMappingM = None
        self._topDownValues = None

        self._bucketValues = None

    def getDecoderOutputFieldTypes(self):
        return (FieldMetaType.integer,)

    def getWidth(self):
        return self.n

    def _recalcParams(self):
        pass

    def getDescription(self):
        return [(self.name, 0)]

    def encodeIntoArray(self, input, output, learn=True):
        if input is not None and not isinstance(input, numbers.Number):
            raise TypeError("Expected a scalar input but got input of type %s" % type(input))

        if type(input) is float and math.isnan(input):
            input = SENTINEL_VALUE_FOR_MISSING_DATA

        if len(output)>self.n:
            for j in range(int(len(output)/self.n)):
                tmp_out = cn.nth_perm(input+j, self.on_bits, self.n, clamp=True)
                output[j*self.n:(j+1)*self.n] = tmp_out[:]
        else:
            tmp_out = cn.nth_perm(input, self.on_bits, self.n, clamp=True)
            output[:self.n] = tmp_out[:]

    def decode(self, encoded, parentFieldName=''):
        tmpOutput = numpy.array(encoded[:self.n] > 0).astype(encoded.dtype)
        if not tmpOutput.any():
            return (dict(), [])

        bool_str = ''
        for i in range(len(encoded)):
            bool_str = bool_str + str(encoded[i])

        n = int(bool_str, 2)

        f_2.seek(18 * n)
        d = int(f.read(16), 2)

        if parentFieldName != '':
            fieldName = "%s.%s" % (parentFieldName, self.name)
        else:
            fieldName = self.name

        return ({fieldName: (d)}, [fieldName])

# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------


'''print """
This program shows how to access the Temporal Memory directly by demonstrating
how to create a TM instance, train it with vectors, get predictions, and
inspect the state.

The code here runs a very simple version of sequence learning, with one
cell per column. The TP is trained with the simple sequence A->B->C->D->E

HOMEWORK: once you have understood exactly what is going on here, try changing
cellsPerColumn to 4. What is the difference between once cell per column and 4
cells per column?

PLEASE READ THROUGH THE CODE COMMENTS - THEY EXPLAIN THE OUTPUT IN DETAIL

"""'''

# Can't live without numpy
import numpy

# izip for maximum efficiency
from itertools import izip as zip, count

# Python implementation of Temporal Memory

from nupic.research.temporal_memory import TemporalMemory as TM


# Utility routine for printing the input vector
def formatRow(x):
    s = ''
    for c in range(len(x)):
        if c > 0 and c % 10 == 0:
            s += ' '
        s += str(x[c])
    s += ' '
    return s


# Step 1: create Temporal Pooler instance with appropriate parameters

tm = TM(columnDimensions=(24,),
        cellsPerColumn=4,
        initialPermanence=0.5,
        connectedPermanence=0.5,
        minThreshold=2,
        maxNewSynapseCount=20,
        permanenceIncrement=0.13,
        permanenceDecrement=0.06,
        activationThreshold=2,
        )

mgc_e = ChoiceNumberEncoder()

import htmvis

point_displayer = htmvis.PointDisplayer(htmvis.TMVisualizer, tm, mgc_e)

if len(tm.columnDimensions)>1:
    height = tm.columnDimensions[1]
else:
    height = 1

htmvis.add_array(point_displayer, [tm.cellsPerColumn, tm.columnDimensions[0], height], [0, 1, 0], [0, 1, 0], [int(128), int(66), int(21)])
point_displayer.set_poly_data()
point_displayer.visualize()


