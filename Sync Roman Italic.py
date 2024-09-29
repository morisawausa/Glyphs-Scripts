#MenuTitle: Sync Roman Italic
# -*- coding: utf-8 -*-
__doc__="""
(GUI) Duplicates selected glyphs into corresponding roman/italic layers when re-using shapes across slant
"""

import vanilla

class syncRomanItalic( object ):
	"""Copies the selected layers to the roman/italic counterpart, based on layer names
	"""
	def __init__(self):
		windowWidth  = 200
		windowHeight = 150

		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default self, window size
			"Sync Roman and Italic", # window title
			autosaveName = "com.motsuka.syncRomanItalic.mainwindow" # stores last window position and size
		)

		self.font = Glyphs.font

		self.w.text = vanilla.TextBox((10, 10, -10, 20), "Choose the source layer")
		self.w.baseLayer = vanilla.RadioGroup((10, 30, -10, 30), ["Roman", "Italic"], callback=self.savePreferences)
		#self.w.decomposeLayer = vanilla.CheckBox((10, 60, -10, 30), "Decompose target?", callback=self.savePreferences)
		self.w.offset = vanilla.CheckBox((10, 70, 90, 20), "Offset", callback=self.savePreferences)
		self.w.offsetValue = vanilla.EditText((100, 70, -10, 20), text='', callback=self.savePreferences)

		self.w.buttonSync = vanilla.Button((10, 100, -10, 30), "Copy", callback=self.copyLayer )
		#Open window and focus on it:		
		Glyphs.showMacroWindow()
		
		self.loadPreferences()

		self.w.open()
		self.w.makeKey()

	def loadPreferences( self ):
		try:
			Glyphs.registerDefault("com.motsuka.syncRomanItalic.baseLayer", 0)
			Glyphs.registerDefault("com.motsuka.syncRomanItalic.offset", 0)
			Glyphs.registerDefault("com.motsuka.syncRomanItalic.offsetValue", '')
			#Glyphs.registerDefault("com.motsuka.syncRomanItalic.decomposeLayer", False)
			self.w.baseLayer.set( Glyphs.defaults["com.motsuka.syncRomanItalic.baseLayer"] )
			self.w.offset.set( Glyphs.defaults["com.motsuka.syncRomanItalic.offset"] )
			self.w.offsetValue.set( Glyphs.defaults["com.motsuka.syncRomanItalic.offsetValue"] )
			#self.w.decomposeLayer.set( Glyphs.defaults["com.motsuka.syncRomanItalic.decomposeLayer"] )
		except:
			return False
		return True

	def savePreferences( self, sender ):
		Glyphs.defaults["com.motsuka.syncRomanItalic.baseLayer"] = self.w.baseLayer.get()
		Glyphs.defaults["com.motsuka.syncRomanItalic.offset"] = self.w.offset.get()
		Glyphs.defaults["com.motsuka.syncRomanItalic.offsetValue"] = self.w.offsetValue.get()
		#Glyphs.defaults["com.motsuka.syncRomanItalic.decomposeLayer"] = self.w.decomposeLayer.get()
		return True

	def copyPathsFromLayerToLayer( self, sourceLayer, targetLayer, keepOriginal=False ):
		"""Copies all paths from sourceLayer to targetLayer"""
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


	# def calcItalicOffset(self, yoffset, italicAngle):
	# 	"""
	# 	Given a y offset and an italic angle, calculate the x offset.
	# 	"""
	# 	from math import radians, tan
	# 	ritalicAngle = radians(italicAngle)
	# 	xoffset = int(round(tan(ritalicAngle) * yoffset/2))
	# 	return xoffset

	# def setOffset(self, sender):
	# 	if sender.get() == 1:
	# 		print('recalc offset')
	# 		master = self.font.selectedFontMaster
	# 		originValue = master.xHeight
	# 		italicAngle = master.italicAngle
	# 		self.offset = self.calcItalicOffset(yoffset=originValue, italicAngle=italicAngle)
	# 		self.w.offsetValue.set(str(self.offset))

	def copyLayer(self, sender):
		base = self.w.baseLayer.get()
		try:
			for layer in Font.selectedLayers:
				if base == 1:
					if 'Italic' in layer.name:
						target_layer_name = layer.name.replace(' Italic', '')
						source_layer_name = layer.name
					else:
						target_layer_name = layer.name
						source_layer_name = layer.name + ' Italic'
				if base == 0:
					if 'Italic' not in layer.name:
						target_layer_name = layer.name + ' Italic'
						source_layer_name = layer.name
					else:
						target_layer_name = layer.name
						source_layer_name = layer.name.replace(' Italic', '')

				print(f'{layer.parent.name}: copying {source_layer_name} to {target_layer_name}')
				sourcelayer = layer.parent.layers[source_layer_name]
				targetlayer = layer.parent.layers[target_layer_name]
					
				self.font.disableUpdateInterface()

				try:
					# Copy paths, components, anchors, and metrics:
					self.copyPathsFromLayerToLayer( sourcelayer, targetlayer, False )
					self.copyComponentsFromLayerToLayer( sourcelayer, targetlayer, False )
					self.copyAnchorsFromLayerToLayer( sourcelayer, targetlayer, False )
					self.copyMetricsFromLayerToLayer( sourcelayer, targetlayer )
					if self.w.offset.get() == 1:
						offsetvalue =  self.w.offsetValue.get()
						print( '- Offseting by ' + offsetvalue )
						transformation = NSAffineTransform()
						transformation.shift( (float(offsetvalue), 0) )
						targetlayer.transform(transformation)
						
				except Exception as e:
					raise e
					
				finally:
					self.font.enableUpdateInterface()

		except Exception as e:
			print(("Error copying layers", e))

syncRomanItalic()