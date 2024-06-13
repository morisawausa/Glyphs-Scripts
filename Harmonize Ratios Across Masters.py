#MenuTitle: Harmonize Ratios Across Masters...
# -*- coding: utf-8 -*-
__doc__="""
(GUI) Aligns the ratios of the offcurve points in other selected masters to those for currently selected oncurve point. 
"""

from math import sqrt
import vanilla


class HarmonizeRatios( object ):
	"""#This script responds to a selected oncurve point by measuring
	the length ratio of the surrounding offcurves and solving for
	the same ratio in all other masters, up to numerical precision.
	"""
	def __init__(self):
		# Window 'self.w':
		windowWidth  = 200
		windowHeight = 500
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 100   # user can resize height by this value

		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default self, window size
			"Harmonize Ratios", # window title
			minSize = ( 200, 200 ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.motsuka.HarmonizeRatios.mainwindow" # stores last window position and size
		)

		self.font = Glyphs.font
		self.masters = Glyphs.font.masters
		self.masterCount = len(self.masters)

		#Open window and focus on it:		
		Glyphs.showMacroWindow()
		
		self.setup_masterlist()
		self.loadPreferences()
		self.w.open()
		self.w.makeKey()

	def setup_masterlist(self):
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 20
		view = self.w
		view.masterLabel = vanilla.TextBox( (inset, linePos, -inset, lineHeight*2), u"Select relevant masters", sizeStyle='small')
		linePos += lineHeight

		for i in range(self.masterCount):
			checkboxID = "checkbox%i" % i
			setting = "com.motsuka.HarmonizeRatios.checkbox%i" % i
			setattr(view, checkboxID, vanilla.CheckBox( (inset, linePos, -inset, 20), self.masters[i].name, value=False, callback=self.savePreferences, sizeStyle='small' ) )
			linePos += lineHeight

		view.buttonHarmonize = vanilla.Button((inset, linePos, -inset, 30), "Harmonize", sizeStyle='regular', callback=self.runHarmonize )
		view.setDefaultButton( view.buttonHarmonize )

	def loadPreferences( self ):
		try:
			for i in range(self.masterCount):
				checkboxID = "checkbox%i" % i
				setting = "com.motsuka.HarmonizeRatios.checkbox%i" % i
				Glyphs.registerDefault(setting, False)
				getattr(self.w, checkboxID).set( Glyphs.defaults[setting] )
		except:
			return False
		return True

	def savePreferences( self, sender ):
		for i in range(self.masterCount):
			checkboxID = "checkbox%i" % i
			setting = "com.motsuka.HarmonizeRatios.checkbox%i" % i
			Glyphs.defaults[setting] = getattr(self.w, checkboxID).get()
		return True

	def selectedMasters(self):
		masterList = []
		try:
			for i in range(self.masterCount):
				checkboxID = "checkbox%i" % i
				checkbox = getattr(self.w, checkboxID)
				if( bool(checkbox.get()) ):					
					masterName = self.masters[i].name
					masterList.append( masterName )						
		except Exception as e:
			print(("Error getting master selection", e))
			return False
		return masterList


	def runHarmonize(self, sender):
		masters = self.selectedMasters()
		print('Harmonize: ', masters )
		try:

			for layer, glyph, segments in self.get_selected_glyphs():
				print( glyph.name )
				#copy to background
				for glayer in glyph.layers:
					if glayer.name in masters:
						glayer.setBackground_(glayer.copyDecomposedLayer())

				for segment in segments:
					i, P, C, N = segment

					is_smooth, K, _, _ = self.measure_segment_ratio(segment)

					if not is_smooth:
						print('segment not smooth')
						continue

					# This approach solves for the value of
					# the parameter directly, by observing that
					# the length ratios we compute on the  X-Y plane
					# must also hold in T-space, since the line
					# defined self, by the [prev, curr, next] is arc-length
					# parametrized. This makes the problem SO MUCH EASIER.
					# we can just do some simple algebra to get the parameter
					# values, and then lerp the requested point.

					# print('[%s] is the controlling master.\n' % layer.name)

					if self.is_line_curve_transition(P, C, N):
						for master_name in masters:
							target_layer = glyph.layers[master_name]							
							self.solve_line_curve_transition(segment, target_layer, K)

					elif self.is_curve_knot(P, C, N):
						for master_name in masters:
							target_layer = glyph.layers[master_name]
							self.solve_knot_point_transition(segment, target_layer, K)
		except Exception as e:
			print(("Error harmonizing", e))
		
		return True


	def length_squared(self, p1, p2):
		"""Given two NSPoints, compute their squared length.
		(skipped that square root, baby.)
		"""
		return (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2


	def length(self, p1, p2):
		"""Given two NSPoints, compute their length"""
		return sqrt(self.length_squared(p1, p2))


	def get_selected_glyphs(self):
		"""Helper method to get the currently selected layers
		in the current edit view.
		"""
		return list(map(lambda l: (l, l.parent, self.get_relevant_selected_segments(l)), self.font.selectedLayers))


	def get_relevant_selected_segments(self, layer):
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



	def measure_segment_ratio(self, segment):
		"""Given a segment consisting of (prev, curr, next), this
		method returns the segment ratio of the triple. The segment ratio
		is the ratio of squared lengths of prev to curr and curr to next:

		r = |prev - curr| / |curr - next|

		We use the squared length rather than the length to skip the
		extra computation of the squared root. The ratio is the same, regardless
		of whether you use distance or squared distance, up to O(n^2) numerical error.

		If you need extra precision, use the length instead.

		NOTE: Throws an assertion error if the selected point is not smooth: ie, a corner.
		"""
		# not sure if this is the correct
		# numerical tolerance for the smoothness check.
		smoothness_tolerance = 0.01

		_, prev, curr, next = segment

		prev_curr_length = self.length(prev, curr)
		curr_next_length = self.length(curr, next)
		prev_next_length = self.length(prev, next)

		# prev_curr_length2 = self.length_squared(prev, curr)
		# curr_next_length2 = self.length_squared(curr, next)
		# prev_next_length2 = self.length_squared(prev, next)

	 		# assuming that prev, curr, and next lie on a line
		total_length = prev_curr_length + curr_next_length
		is_smooth = abs(prev_next_length - total_length) < smoothness_tolerance

		# Using the ratio PC:CN as a proxy for the length
		# percentages displayed in Cyrus' UI. This gives us
		# a single scalar to use as a target to solve for
		# in the other masters.
		ratio = prev_curr_length / curr_next_length

		return is_smooth, ratio, prev_curr_length, curr_next_length


	# NOTE: This is not used anymore. In a previous version of this script,
	# I computed the ratios in the XY unit plane, and harmonized there. In the
	# current version of the script, I solve for the ratios directly on the
	# t-parameter line for the parametric line through the three points.
	# I'm just leaving this here for posterity.
	def get_t_for_fixed_curr_next(self, C, N, K):
		"""
		C, first fixed NSPoint
		N, second fixed NSPoint
		K = target ratio

		NOTE: Solved it by coordinates, and then realized it
		could easily be solved directly in parameter space,
		rather than ever bothering with coordinates at all.
		Leaving this routine here as a warning. It works,
		but it's not the most elegant solution.
		"""
		KL = K * self.length_squared(C, N)

		D = C.x**2 - 2*C.x*N.x + N.x**2 + C.y**2 - 2*C.y*N.y + N.y**2
		t = (sqrt(KL * D) + D) / D

		return t


	def get_P_float(self, A, B, t):
		"""Given two NSPoints, compute a linear interpolation
		between them, given by the parameter t.
		"""
		return (1-t)*A.x + t*B.x, (1-t)*A.y + t*B.y

	def get_P_int(self, A, B, t):
		"""Given two NSPoints, compute a linear interpolation between
		them, and return the resulting point given at parameter t. The
		coordinates are rounded to the nearest integer for use in the
		unit grid.
		"""
		P_x, P_y = self.get_P_float(A, B, t)
		return int(P_x), int(P_y)



	def is_line_curve_transition(self, P, C, N):
		"""Returns true if the seleted triple consists of a straight segment
		transitioning to a curve, with a smooth connection.
		"""
		o_c_l = P.type == 'offcurve' and C.type == 'curve' and N.type == 'line'
		o_l_l = P.type == 'offcurve' and C.type == 'line' and N.type == 'line'

		l_c_o = P.type == 'line' and C.type == 'curve' and N.type == 'offcurve'
		l_l_o = P.type == 'line' and C.type == 'line' and N.type == 'offcurve'


		return o_c_l or l_c_o or l_l_o or o_l_l


	def is_curve_knot(self, P, C, N):
		"""Return true if C is an oncurve point between two offcurves, and the
		two curves have a smooth connection.
		"""
		o_c_o = P.type == 'offcurve' and C.type == 'curve' and N.type == 'offcurve'

		return o_c_o


	def get_target_segment_from_layer(self, path_index, P, C, N, layer):
		"""Given an index into the path list of a target layer, as well as
		the nodes to extract, this method will extract the corresponding segment
		from the supplied layer.

		NOTE: This method assumes the target_layer is compatible with the layer
		that P, C, and N were selected from.
		"""

		other_path = layer.paths[path_index]

		P_other = other_path.nodes[P.index]
		C_other = other_path.nodes[C.index]
		N_other = other_path.nodes[N.index]

		return P_other, C_other, N_other


	def solve_line_curve_transition(self, segment, target_layer, K):
		"""Given a source segment and a target layer to adjust,
		solve the line to curve (or curve to line) transition,
		and update the center point (the point whose index in
		the target layer correspondes to the index of the selected layer).
		"""

		# print('[%s] solving curve/line transition' % target_layer.name)
		# print('[%s] adjusting point at selected index' % target_layer.name)
		i, P, C, N = segment

		P_other, C_other, N_other = self.get_target_segment_from_layer(i, P, C, N, target_layer)
		C_other_x_pre = C_other.x
		C_other_y_pre = C_other.y

		t = K / (1 + K)
		point_int = self.get_P_int(P_other, N_other, t)

		C_other.x = point_int[0]
		C_other.y = point_int[1]

		# print('[%s] moved center point (%i, %i) ==> (%i, %i)\n' % (target_layer.name, C_other_x_pre, C_other_y_pre, point_int[0], point_int[1]))


	def solve_knot_point_transition(self, segment, target_layer, K):
		"""Given a source segment and target layer to adjust,
		solve for a knot-point update in a curve. Determine which
		handle on the target layer is shorter, and adjust that handle
		so that the ratio between the two handle lengths is equal.
		"""

		# print('[%s] solving knot point transition' % target_layer.name)
		# print('[%s] adjusting point at selected index' % target_layer.name)
		i, P, C, N = segment
		P_other, C_other, N_other = self.get_target_segment_from_layer(i, P, C, N, target_layer)

		# print('[%s] determining shorter handle' % target_layer.name)
		_, ratio_pre, prev_curr_length_pre, curr_next_length_pre = self.measure_segment_ratio((i, P_other, C_other, N_other))

		if prev_curr_length_pre > curr_next_length_pre:
			#print('[%s] previous offcurve to selected point is the anchor.' % target_layer.name)
			N_other_x_pre = N_other.x
			N_other_y_pre = N_other.y

			t = (1 / K) + 1
			point_int = self.get_P_int(P_other, C_other, t)
			N_other.x = point_int[0]
			N_other.y = point_int[1]

			#print('[%s] moved next offcurve (%i, %i) ==> (%i, %i)\n' % (target_layer.name, N_other_x_pre, N_other_y_pre, point_int[0], point_int[1]))

		else:
			# print('selected point to next offcurve')
			#print('[%s] selected point to next offcurve is the anchor.' % target_layer.name)
			P_other_x_pre = P_other.x
			P_other_y_pre = P_other.y

			t = -K
			point_int = self.get_P_int(C_other, N_other, t)
			P_other.x = point_int[0]
			P_other.y = point_int[1]

			#print('[%s] moved previous offcurve (%i, %i) ==> (%i, %i)\n' % (target_layer.name, P_other_x_pre, P_other_y_pre, point_int[0], point_int[1]))

HarmonizeRatios()