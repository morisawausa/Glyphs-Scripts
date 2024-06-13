#MenuTitle: Italic Bowtie...
# -*- coding: utf-8 -*-
__doc__="""
(GUI) Italicizes the selected glyph(s), while setting up "bowtie" guides in the edit view to show the relationship of a font’s vertical and slanted sidebearings.
"""

import vanilla
import math
import GlyphsApp
import copy
from AppKit import NSColor, NSAffineTransform, NSAffineTransformStruct, NSPoint

f = Glyphs.font

class ItalicBowtie( object ):

	def __init__( self ):

		windowWidth  = 350
		windowHeight = 480

		windowWidthResize  = 3000          # user can resize width by this value
		windowHeightResize = 3000          # user can resize height by this value

		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Italic Bowtie",         # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName="com.motsuka.ItalicBowtie.mainwindow"
		)
		self.populateView()

		if not self.loadPreferences( ):
			print("Error: Could not load preferences. Will resort to defaults.")

		self.getView().open()


	def savePreferences( self, sender ):

		self.updateValues()

		view = self.getView()
		Glyphs.defaults["com.motsuka.ItalicBowtie.selectOrigin"] = view.selectOrigin.get()

		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxPaths"] = view.checkboxPaths.get()
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxAnchors"] = view.checkboxAnchors.get()
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxComponents"] = view.checkboxComponents.get()

		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxDrawBowtie"] = view.checkboxDrawBowtie.get()
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxMakeRef"] = view.checkboxMakeRef.get()
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxCommitAngle"] = view.checkboxCommitAngle.get()
		return True


	def loadPreferences( self ):
		view = self.getView()
		#register defaults
		Glyphs.defaults["com.motsuka.ItalicBowtie.selectOrigin"] = 0
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxPaths"] = True
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxAnchors"] = True
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxComponents"] = False

		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxDrawBowtie"] = False
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxMakeRef"] = False
		Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxCommitAngle"] = False

		try:
			view.selectOrigin.set( Glyphs.defaults["com.motsuka.ItalicBowtie.selectOrigin"] )

			view.checkboxPaths.set( Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxPaths"] )
			view.checkboxAnchors.set( Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxAnchors"] )
			view.checkboxComponents.set( Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxComponents"] )

			view.checkboxDrawBowtie.set( Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxDrawBowtie"] )
			view.checkboxMakeRef.set( Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxMakeRef"] )
			view.checkboxCommitAngle.set( Glyphs.defaults["com.motsuka.ItalicBowtie.checkboxCommitAngle"] )

			self.updateValues()

		except:
			return False

		return True



	def populateView(self):

		# define layer scope
		self.setupLayers()

		itemWidth = 110
		itemHeight = 25

		linePos, inset, lineHeight = 12, 15, 30

		view = self.getView()

		view.descriptionText = vanilla.TextBox( (inset, linePos, -inset, lineHeight*2), u"Italicizes the selected glyph(s), while drawing a 'bowtie' in the edit view to show the relationship of a font’s vertical and slanted sidebearings.", sizeStyle='small')
		linePos += lineHeight*2

		view.labelSelected = vanilla.TextBox( (inset, linePos, itemWidth, itemHeight), u"Selected", sizeStyle = 'regular' )
		view.listSelected = vanilla.TextBox( (inset+itemWidth, linePos, -inset-50, itemHeight), "", sizeStyle = 'regular')
		view.buttonRefresh = vanilla.Button( (-70, linePos, 50, itemHeight), u"↺", sizeStyle = 'small', callback=self.resetSelection)

		linePos += lineHeight

		view.labelAngle = vanilla.TextBox( (inset, linePos, itemWidth, itemHeight), u"Italic Angle", sizeStyle = 'regular' )
		view.inputItalicAngle = vanilla.EditText( (inset+itemWidth, linePos, itemWidth, itemHeight), self.master.italicAngle, sizeStyle = 'regular', callback=self.triggerUpdateValuesFromUI)

		linePos += lineHeight

		view.labelOrigin = vanilla.TextBox( (inset, linePos, itemWidth, itemHeight), u"Origin", sizeStyle = 'regular' )
		view.selectOrigin = vanilla.PopUpButton((inset+itemWidth, linePos, itemWidth, itemHeight), [o[0] for o in self.listOrigins], sizeStyle = 'regular', callback=self.savePreferences)
		linePos += lineHeight

		view.labelOffset = vanilla.TextBox( (inset, linePos, itemWidth, itemHeight), u"Offset", sizeStyle = 'regular', selectable = True )
		view.italicSlantOffset = vanilla.TextBox((inset+itemWidth, linePos, itemWidth, itemHeight), "calculated", sizeStyle = 'regular', selectable = True)

		linePos += lineHeight
		view.line = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 5

		view.checkboxPaths = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Paths", sizeStyle='regular', callback=self.savePreferences )
		linePos += itemHeight

		view.checkboxAnchors = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Anchors", sizeStyle='regular', callback=self.savePreferences)
		linePos += itemHeight

		view.checkboxComponents = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Components", sizeStyle='regular', callback=self.savePreferences )

		# linePos += itemHeight
		# view.checkboxGuides = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Guides", sizeStyle='regular', callback=self.savePreferences )

		linePos += lineHeight
		view.line1 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 5

		view.checkboxDrawBowtie = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Draw Bowtie", sizeStyle='regular', callback=self.savePreferences )
		linePos += itemHeight

		view.checkboxMakeRef = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Reference Layer in Background", sizeStyle='regular', callback=self.savePreferences )

		linePos += lineHeight
		view.line2 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 5

		view.checkboxCommitAngle = vanilla.CheckBox( (inset, linePos, -inset, itemHeight), "Update Master with this Italic Angle", sizeStyle='regular', callback=self.savePreferences )
		linePos += itemHeight

		linePos += 15

		view.buttonTransform = vanilla.Button((inset, linePos, -inset, itemHeight), "Italicize", sizeStyle='regular', callback=self.commitItalicCallback )
		view.setDefaultButton( view.buttonTransform )
		linePos += lineHeight

		view.buttonClose = vanilla.Button((inset, linePos, 160, itemHeight), "Close", sizeStyle='regular', callback=self.exit )
		view.buttonReset = vanilla.Button((190, linePos, -inset, itemHeight), "Reset", sizeStyle='regular', callback=self.cancel )

		self.setSelected()

		view.open()
		view.makeKey()

		view.bind("became key", self.resetSelection)

	def setupLayers(self):
		"""sets selected scope and duplicates layers for resets"""
		try:
			self.master = f.selectedFontMaster
			self.italicAngle = self.master.italicAngle
			self.originalAngle = self.master.italicAngle
			self.layers = f.selectedLayers
			self.originalLayers = []

			# make copy of original layers to revert to
			for l in self.layers:
				originalLayer = GSLayer()
				originalLayer = l.copy()
				self.originalLayers.append(originalLayer)

			self.listOrigins = [
				[u"½ x-height", self.master.xHeight],
				[u"½ cap height", self.master.capHeight]
			]
		except:
			Message("Please select a glyph with paths", "Nothing selected", OKButton=None)
			return False

	def resetSelection(self, sender=None):
		"""refreshes Bowtie with new scope"""
		self.disableUpdate()
		self.setupLayers() #reset scope
		self.setSelected() #update window
		self.enableUpdate()

	def getView(self):
		return self.w

	def disableUpdate(self, sender=None):
		f.disableUpdateInterface()

	def enableUpdate(self, sender=None):
		f.enableUpdateInterface()
		self.refreshView()

	def refreshView(self):
		"""The refresh view function forces a repaint of the EditView,
		even the user has not interacted. useful for updating views based on
		settings changes or external events.
		"""
		try:
			current_tab_view = Glyphs.font.currentTab
			if current_tab_view:
				current_tab_view.graphicView().setNeedsDisplay_(True)
		except:
			pass


	# Math stuff to calc values
	##################################

	def calcItalicSkew(self, italicAngle):
		return math.radians(italicAngle)

	def calcItalicOffset(self, yoffset, italicAngle):
		"""
		Given a y offset and an italic angle, calculate the x offset.
		"""
		from math import radians, tan
		ritalicAngle = radians(italicAngle)
		xoffset = int(round(tan(ritalicAngle) * yoffset/2))
		return xoffset*-1

	def NStransform(self, shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
		"""
		Returns an NSAffineTransform object for transforming layers.
		Apply an NSAffineTransform t object like this:
			Layer.transform_checkForSelection_doComponents_(t,False,True)
		Access its transformation matrix like this:
			tMatrix = t.transformStruct() # returns the 6-float tuple
		Apply the matrix tuple like this:
			Layer.applyTransform(tMatrix)
			Component.applyTransform(tMatrix)
			Path.applyTransform(tMatrix)
		Chain multiple NSAffineTransform objects t1, t2 like this:
			t1.appendTransform_(t2)
		"""
		myTransform = NSAffineTransform.transform()
		if rotate:
			myTransform.rotateByDegrees_(rotate)
		if scale != 1.0:
			myTransform.scaleBy_(scale)
		if not (shiftX == 0.0 and shiftY == 0.0):
			myTransform.translateXBy_yBy_(shiftX,shiftY)
		if skew:
			skewStruct = NSAffineTransformStruct()
			skewStruct.m11 = 1.0
			skewStruct.m22 = 1.0
			skewStruct.m21 = math.tan(math.radians(skew))
			skewTransform = NSAffineTransform.transform()
			skewTransform.setTransformStruct_(skewStruct)
			myTransform.appendTransform_(skewTransform)
		return myTransform

	# Get values from vanilla window
	##################################

	def triggerUpdateValuesFromUI(self, sender):
		self.updateValues()

	def updateValues(self):
		view = self.getView()

		italicAngleStr = view.inputItalicAngle.get()

		try:
			if (italicAngleStr != ""):
				self.italicAngle = float(italicAngleStr)
			else:
				self.italicAngle = 0

			self.origin = self.listOrigins[view.selectOrigin.get()]

			self.setOffset(self.origin[1])

			self.paths = bool(view.checkboxPaths.get())
			self.anchors = bool(view.checkboxAnchors.get())
			self.components = bool(view.checkboxComponents.get())

			self.drawBowtie = bool(view.checkboxDrawBowtie.get())
			self.makeRef = bool(view.checkboxMakeRef.get())

			self.angleUpdate = bool(view.checkboxCommitAngle.get())

		except Exception as e:
			print(("Error updating values", e))
			return False

	def setOffset(self, originValue):
		self.offset = self.calcItalicOffset(yoffset=originValue, italicAngle=self.italicAngle)
		self.getView().italicSlantOffset.set(str(self.offset))

	# Sets values into vanilla textboxes
	##################################
	def setSelected(self):
		view = self.getView()

		selectedNames = []
		for l in self.layers:
			selectedNames.append(l.parent.name)
		selectedList = (",").join(selectedNames)

		view.listSelected.set(selectedList)
		view.inputItalicAngle.set(self.master.italicAngle)

	# Main
	##################################

	def commitItalicCallback(self, sender):
		"""Commits italicization changes to all layers and tags with color"""

		try:
			self.disableUpdate()

			skewRadians = self.calcItalicSkew(self.italicAngle)
			offset = float(self.offset)

			for layerIndex, layer in enumerate(self.layers):
				try:
					layer.colorObject = NSColor.colorWithDeviceRed_green_blue_alpha_(197.0 / 255.0, 166.0 / 255.0, 255.0 / 255.0, 1)
				except Exception as e:
					print(e)

				if(self.angleUpdate):
					self.master.italicAngle = self.italicAngle #update italic angle for master

				# apply italicizing

				# layer.applyTransform([
				# 					1, # x scale factor
				# 					0, # x skew factor
				# 					skewRadians, # y skew factor
				# 					1, # y scale factor
				# 					offset, # x position #offset
				# 					0  # y position
				# 					])

				
				t = self.NStransform(offset, 0.0, 0.0, self.italicAngle, 1.0)
				layer.transform_checkForSelection_doComponents_(t,False,True)

				# reset layer according to params
				self.resetLayer(layerIndex, paths=(not self.paths), anchors=(not self.anchors), components=(not self.components), guides=False, metrics=False)

				# draw references
				if(self.drawBowtie):
					self.drawItalicBowtie(layer, italicAngle=self.italicAngle, offset=0, origin=self.origin[1])

				if(self.makeRef):
					self.makeReferenceLayer(layer, italicAngle=self.italicAngle, offset=self.offset)

			self.enableUpdate()
		except Exception as e:
			print(("italicize", e))
			pass


	def exit(self, sender):
		"""Close dialog box"""
		self.getView().close()

	def cancel(self, sender):
		"""Resets all original form before transformation"""
		self.disableUpdate()
		for layerIndex, layer in enumerate(self.layers):
			self.resetLayer(layerIndex)
			layer.color = 9223372036854775807
		self.enableUpdate()


	def resetLayer(self, layerIndex, paths=True, anchors=True, components=True, guides=True, metrics=True):
		"""Resets layer path to original form before transformation"""
		
		thisLayer = self.layers[layerIndex]
		backupLayer = self.originalLayers[layerIndex]

		if(metrics):
			print("reset italic angle to ", self.originalAngle)
			self.italicAngle = self.originalAngle
			# self.master.customParameters['italicAngle'] = 0
			# del(self.master.customParameters['italicAngle'])

		if(paths and len(thisLayer.paths)>0 ):
			print("reset paths")
			self.copyPathsFromLayerToLayer(backupLayer, thisLayer)

		if(anchors):
			print("reset anchors")
			self.copyAnchorsFromLayerToLayer(backupLayer, thisLayer)
		# 	thisLayer.anchors = copy.copy(backupLayer.anchors)

		if(components and len(thisLayer.components)>0):
			print("reset components")
			self.copyComponentsFromLayerToLayer(backupLayer, thisLayer)

		if(guides):
			# clear guides
			print("clear guides")
			thisLayer.guides = None
			thisLayer.background.guides = None


	def copyPathsFromLayerToLayer( self, sourceLayer, targetLayer, keepOriginal=False ):
		"""Copies all paths from sourceLayer to targetLayer from Copy Layer to Layer.py"""
		numberOfPathsInSource  = len( sourceLayer.paths )
		numberOfPathsInTarget  = len( targetLayer.paths )
		
		if numberOfPathsInTarget != 0 and not keepOriginal:
			print("- Deleting %i paths in target layer" % numberOfPathsInTarget)
			try:
				# GLYPHS 3
				for i in reversed(range(len(targetLayer.shapes))):
					if type(targetLayer.shapes[i]) == GSPath:
						del targetLayer.shapes[i]
			except:
				# GLYPHS 2
				targetLayer.paths = None

		if numberOfPathsInSource > 0:
			print("- Copying paths")
			for thisPath in sourceLayer.paths:
				newPath = thisPath.copy()
				try:
					# GLYPHS 3
					targetLayer.shapes.append( newPath )
				except:
					# GLYPHS 2
					targetLayer.paths.append( newPath )

	def copyComponentsFromLayerToLayer( self, sourceLayer, targetLayer, keepOriginal=False ):
		"""Copies all components from sourceLayer to targetLayer."""
		numberOfComponentsInSource = len( sourceLayer.components )
		numberOfComponentsInTarget = len( targetLayer.components )

		if numberOfComponentsInTarget != 0 and not keepOriginal:
			print("- Deleting %i components in target layer" % numberOfComponentsInTarget)
			try:
				# GLYPHS 3
				for i in reversed(range(len(targetLayer.shapes))):
					if type(targetLayer.shapes[i]) == GSComponent:
						del targetLayer.shapes[i]
			except:
				# GLYPHS 2
				targetLayer.components = []

		if numberOfComponentsInSource > 0:
			print("- Copying components:")
			for thisComp in sourceLayer.components:
				newComp = thisComp.copy()
				print("   Component: %s" % ( thisComp.componentName ))
				targetLayer.components.append( newComp )

	def copyAnchorsFromLayerToLayer( self, sourceLayer, targetLayer, keepOriginal=False ):
		"""Copies all anchors from sourceLayer to targetLayer."""
		numberOfAnchorsInSource = len( sourceLayer.anchors )
		numberOfAnchorsInTarget = len( targetLayer.anchors )

		if numberOfAnchorsInTarget != 0 and not keepOriginal:
			print("- Deleting %i anchors in target layer" % numberOfAnchorsInTarget)
			targetLayer.setAnchors_(None)

		if numberOfAnchorsInSource > 0:
			print("- Copying anchors from source layer:")
			for thisAnchor in sourceLayer.anchors:
				newAnchor = thisAnchor.copy()
				targetLayer.anchors.append( newAnchor )
				print("   %s (%i, %i)" % ( thisAnchor.name, thisAnchor.position.x, thisAnchor.position.y ))

	def copyMetricsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies width of sourceLayer to targetLayer."""
		sourceWidth = sourceLayer.width
		if targetLayer.width != sourceWidth:
			targetLayer.width = sourceWidth
			print("- Copying width (%.1f)" % sourceWidth)
		else:
			print("- Width not changed (already was %.1f)" % sourceWidth)

	# Options
	##################################

	def drawItalicBowtie(self, layer, italicAngle=0, offset=0, origin=0):
		"""
		Draw an italic Bowtie as guides
		"""

		leftGuide = GSGuide()
		leftGuide.position = NSPoint(offset, origin/2)
		leftGuide.angle = 90-italicAngle

		leftStraightGuide = GSGuide()
		leftStraightGuide.position = NSPoint(offset, origin/2)
		leftStraightGuide.angle = 90

		rightGuide = GSGuide()
		rightGuide.position = NSPoint(offset+layer.width, origin/2)
		rightGuide.angle = 90-italicAngle

		rightStraightGuide = GSGuide()
		rightStraightGuide.position = NSPoint(offset+layer.width, origin/2)
		rightStraightGuide.angle = 90

		layer.guides.extend([leftGuide, rightGuide, leftStraightGuide, rightStraightGuide])


	def makeReferenceLayer(self, layer, italicAngle=0, offset=0):
		"""
		Store a vertically skewed copy in the background for reference
		"""

		# use for vertical offset later
		bottom1 = layer.bounds.origin.y
		height1 = abs(layer.bounds.size.height)

		layer.background = layer.copy()
		dy = abs(italicAngle)/2.0 #half the italic angle
		y = self.calcItalicSkew(dy)

		layer.background.applyTransform((
			  1.0, # x scale factor
			  -y, # x skew factor
			  0, # y skew factor
			  1.0, # y scale factor
			  0.0, # x position
			  0.0  # y position
		))

		# shift y to align better with foreground
		bottom2 = layer.background.bounds.origin.y
		height2 = abs(layer.background.bounds.size.height)
		dif = (height1-height2) / 2
		yoffset = (abs(bottom2)-abs(bottom1)) + dif

		layer.background.applyTransform((
			  1.0, # x scale factor
			  0, # x skew factor
			  0, # y skew factor
			  1.0, # y scale factor
			  0.0, # x position
			  yoffset  # y position
		))

ItalicBowtie()
