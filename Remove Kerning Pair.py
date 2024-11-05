#MenuTitle: Remove kerning for active pair
# -*- coding: utf-8 -*-
__doc__="""
Deletes kerning for the current pair, useful when assigned a shortcut. If there are exceptions, it will snap back to the group value. If the resulting kerning value is zero, it will also remove the zero value kerning.
"""

font = Glyphs.font

View = Glyphs.currentDocument.windowController().activeEditViewController().graphicView()

def get_layers():
	ActiveLayer = View.activeLayer()
	PrevLayer = View.cachedGlyphAtIndex_(View.activeIndex() - 1)
	return PrevLayer, ActiveLayer

def check_pair_type(l,r):
	r_exception = r.previousKerningExceptionForLayer_direction_(l, LTR)
	l_exception = r.previousKerningExceptionForLayer_direction_(r, LTR)

	right_key = r.parent.leftKerningKey
	left_key = l.parent.rightKerningKey
	right_glyphname = r.parent.name
	left_glyphname = l.parent.name
	# print(l, ' ', left_key, '&', r, ' ', right_key)

	if not l_exception and r_exception:
		kerning_parameters = left_key, right_glyphname
		print("group to glyph kerning")
	elif l_exception and not r_exception:
		kerning_parameters = left_glyphname, right_key
		print("glyph to group kerning")
	elif r_exception and l_exception:
		kerning_parameters = left_glyphname, right_glyphname
		print("glyph to glyph kerning")
	else:
		kerning_parameters = left_key, right_key
		print("group to group kerning")
	
	return kerning_parameters

layers = get_layers()
params = check_pair_type(*layers)
font.removeKerningForPair(font.selectedFontMaster.id, *params,)
print("Removed kerning pair %s \n" %(params,))

# check again to see if this resulted in zero kerning
layers2 = get_layers()
params2 = check_pair_type(*layers2)
if font.kerningForPair(font.selectedFontMaster.id, *params2) == 0:
	font.removeKerningForPair(font.selectedFontMaster.id, *params2,)
	print("Removed zero-value kerning pair %s \n" %(params2,))
