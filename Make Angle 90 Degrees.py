from __future__ import print_function
#MenuTitle: Make Angle at Selected Point 90 Degrees
# -*- coding: utf-8 -*-
__doc__ = """
Makes the angle at the selected corner point 90 degrees. Moves the selected point
along the longer of the two neighboring segments to find the 90 degree point.
"""
from math import sqrt

def get_selected_glyphs():
	"""Helper method to get the currently selected layers
	in the current edit view.
	"""
	return list(map(lambda l: (l, l.parent, get_relevant_selected_segments(l)), Glyphs.font.selectedLayers))


def get_relevant_selected_segments(layer):
	"""From a selected layer, get 3-point sequences surrounding a
	selected node. For example, a selecting a smooth oncurve and
	running this function on it will return the previous offcurve,
	the selected oncurve, and the next offcurve.

	In general, this method returns triples of (prev, curr, next)
	where curr is a selected node, and order is determined by the
	orientation of contour.
	"""
	segments = []
	for i, path in enumerate(layer.paths):
		for node in path.nodes:
			contour_length = len(path.nodes)
			if node.selected:
				# get the surrounding segment points of the selection
				prev = path.nodes[node.index - 1]
				next = path.nodes[(node.index + 1) % contour_length]

				segments.append((i, prev, node, next))

	return segments

def get_vector_length(A):
	"""Gets the length of a given vector
	"""
	return sqrt(A[0]**2 + A[1]**2)


def get_unit_vector(A):
	"""Given 2d vector compenents x and y as floats,
	returns the unit vector in the same direction
	as the given vector (x, y).
	"""
	length = get_vector_length(A)
	return A[0] / length, A[1] / length


def dot_product(A, B):
	"""Calculates the dot product of the given vectors to
	Check how close to orthogonal they are.
	"""
	return (A[0] * B[0]) + (A[1] * B[1])



def project_onto(A, B):
	"""Projects one vector onto another. The order of the vectors is
	Important: A is the vector you want to project, B is the vector
	you want to project onto.
	"""
	proj_numerator = dot_product(A, B)
	proj_denominator = dot_product(B, B)

	scale_factor = proj_numerator / proj_denominator

	return scale_factor * B[0], scale_factor * B[1]



data = get_selected_glyphs()

for layer, glyph, segments in data:

	if len(segments) == 0: print("nothing selected")

	for i, P, C, N in segments:

		CP = (P.x - C.x, P.y - C.y)
		CN = (N.x - C.x, N.y - C.y)

		CP_length = get_vector_length( CP )
		CN_length = get_vector_length( CN )

		if CP_length > CN_length:
			projection = project_onto(CN, CP)

		elif CP_length < CN_length:
			projection = project_onto(CP, CN)

		else:
			print("They're the same! Fail.")
			projection = 0, 0

		C.x = C.x + projection[0]
		C.y = C.y + projection[1]
