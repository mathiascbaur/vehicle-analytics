"""
Trace representation for relevance calculations on vehicle traces.

@since: 30.06.2010
@version: 15.02.2012
@status: final
@author: Mathias Baur
@contact: mathias@smartlane.de
"""

import math


class Vector(object):

	x = 0
	y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

	def angle(a,b):
		"""Return the angle between b-a and the positive x-axis.
		Values go from 0 to pi in the upper half-plane, and from 
		0 to -pi in the lower half-plane.
		"""
		return math.atan2(b.y-a.y, b.x-a.x)

	def distance(a,b):
		return math.hypot(b.x-a.x, b.y-a.y)