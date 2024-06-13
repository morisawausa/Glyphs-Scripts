#MenuTitle: Rotate Glyph 180
# -*- coding: utf-8 -*-
__doc__="""
Rotate the current glyph 180°
"""

from AppKit import NSAffineTransform

Font = Glyphs.font
selectedLayers = Font.selectedLayers


Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	bounds = thisLayer.bounds
	midx = bounds[0].x + bounds[1].width / 2
	midy = bounds[0].y + bounds[1].height / 2
	
	transformation = NSAffineTransform()
	transformation.rotate(180, (midx, midy))
	thisLayer.transform(transformation)


Font.enableUpdateInterface()