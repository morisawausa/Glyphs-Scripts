from __future__ import print_function
#MenuTitle: Delete Annotations on Current Layer
# -*- coding: utf-8 -*-
__doc__="""
Clears all notes on the currently selected layer. Useful with a shortcut for the QA Test Suite.
"""

layer = Glyphs.font.selectedLayers[0]
layer.annotations = None
print(u"Notes on %s[%s] removed ✨" % (layer.parent.name, layer.name))

