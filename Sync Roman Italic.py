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
		self.w.buttonSync = vanilla.Button((10, 100, -10, 30), "Copy", callback=self.copyLayer )
		#Open window and focus on it:		
		Glyphs.showMacroWindow()
		
		self.loadPreferences()
		self.w.open()
		self.w.makeKey()

	def loadPreferences( self ):
		try:
			Glyphs.registerDefault("com.motsuka.syncRomanItalic.baseLayer", 0)
			#Glyphs.registerDefault("com.motsuka.syncRomanItalic.decomposeLayer", False)
			self.w.baseLayer.set( Glyphs.defaults["com.motsuka.syncRomanItalic.baseLayer"] )
			#self.w.decomposeLayer.set( Glyphs.defaults["com.motsuka.syncRomanItalic.decomposeLayer"] )
		except:
			return False
		return True

	def savePreferences( self, sender ):
		Glyphs.defaults["com.motsuka.syncRomanItalic.baseLayer"] = self.w.baseLayer.get()
		#Glyphs.defaults["com.motsuka.syncRomanItalic.decomposeLayer"] = self.w.decomposeLayer.get()
		return True

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
				source = layer.parent.layers[source_layer_name]
				target = layer.parent.layers[target_layer_name]
				target.clear()
				target.shapes = source.shapes.copy()
				target.anchors = source.anchors.copy()
				target.width = source.width
		except Exception as e:
			print(("Error copying layers", e))

syncRomanItalic()