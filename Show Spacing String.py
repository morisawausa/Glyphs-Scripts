#MenuTitle: Show Spacing String
# -*- coding: utf-8 -*-
__doc__="""
Inserts the selected glyph within its spacing string in a new line.
"""

import GlyphsApp
Font = Glyphs.font

def case(glyph, case):
	return glyph.case == case

def cat(glyph, category):
	return glyph.category == category

def subCat(glyph, subCat):
	return glyph.subCategory == subCat

def script(glyph, script):
	return glyph.script == script

def getContext(glyph):

	# print glyph
	glyphName = "/"+glyph.name
	
	print(glyphName, glyph.case, glyph.subCategory)

	# xheight
	if "xhght" in glyph.name:
		if script(glyph, "cyrillic"):
			return u"""/en-cy.xhght/en-cy.xhght {0} /en-cy.xhght/o-cy.xhght/en-cy.xhght/o-cy.xhght {0} /o-cy.xhght/o-cy.xhght""".format(glyphName)
		elif script(glyph, "greek"):
			return u"""/eta.xhght/eta.xhght {0} /eta.xhght/omicron.xhght/eta.xhght/omicron.xhght {0} /omicron.xhght/omicron.xhght""".format(glyphName)
		else:
			return u"""/n.xhght/n.xhght {0} /n.xhght/o.xhght/n.xhght/o.xhght {0} /o.xhght/o.xhght""".format(glyphName)

	# tabular numbers and symbols
	elif (glyph.name.endswith(".tf")):
		return u"""/zero.tf/zero.tf{0} /zero.tf/one.tf/zero.tf/one.tf{0} /one.tf/one.tf""".format(glyphName)

	# old style numbers and symbols
	elif (glyph.name.endswith(".osf")):
		return u"""/zero.osf/zero.osf{0} /zero.osf/one.osf/zero.osf/one.osf{0} /one.osf/one.osf""".format(glyphName)

	# small numbers
	elif (subCat(glyph, "Fraction") and "dnom" in glyph.name):
		return u"""/zero.dnom/zero.dnom{0} /zero.dnom/one.dnom/zero.dnom/one.dnom{0} /one.dnom/one.dnom""".format(glyphName)

	# small numbers
	elif (subCat(glyph, "Fraction") and "numr" in glyph.name):
		return u"""/zero.numr/zero.numr{0} /zero.numr/one.numr/zero.numr/one.numr{0} /one.numr/one.numr""".format(glyphName)

	# numbers
	elif subCat(glyph, "Decimal Digit"):
		return u"""00{0} 00{0} 11{0} 1101""".format(glyphName)

	# currency
	elif subCat(glyph, "Currency") :
		return u"""00{0} 00{0} 11{0} 1101""".format(glyphName)

	# Greek
	elif script(glyph, "greek") and (subCat(glyph, "Smallcaps") or case(glyph, 3)) :
		return u"""/eta.sc/eta.sc {0} /eta.sc/omicron.sc/eta.sc/omicron.sc {0} /omicron.sc/omicron.sc""".format(glyphName)

	elif script(glyph, "greek") and ( ( subCat(glyph, "Uppercase") or case(glyph, 1) ) or case(glyph, "upper") ):
		return u"""/Eta/Eta{0} /Eta/Omicron/Eta/Omicron{0} /Omicron/Omicron""".format(glyphName)

	elif script(glyph, "greek") and ( ( subCat(glyph, "Lowercase") or case(glyph, 2) ) or case(glyph, "lower") ):
		return u"""ηη{0} ηοηο{0} οο""".format(glyphName)

	# Cyrllic
	elif script(glyph, "cyrillic") and (subCat(glyph, "Smallcaps") or case(glyph, 3)) :
		return u"""/en-cy.sc/en-cy.sc {0} /en-cy.sc/o-cy.sc/en-cy.sc/o-cy.sc {0} /o-cy.sc/o-cy.sc""".format(glyphName)

	elif script(glyph, "cyrillic") and ( subCat(glyph, "Lowercase") or case(glyph, 2) ) :
		if "loclBGR" in glyph.name and 'en-cy.loclBGR' in Font.glyphs:
			return u"""/en-cy.loclBGR/en-cy.loclBGR{0} /en-cy.loclBGR/o-cy/en-cy.loclBGR/o-cy{0} /o-cy/o-cy""".format(glyphName)
		else:
			return u"""/en-cy/en-cy{0} /en-cy/o-cy/en-cy/o-cy{0} /o-cy/o-cy""".format(glyphName)

	elif script(glyph, "cyrillic") and ( subCat(glyph, "Uppercase") or case(glyph, 1) ) :
		return u"""/En-cy/En-cy{0} /En-cy/O-cy/En-cy/O-cy{0} /O-cy/O-cy""".format(glyphName)

	# UC
	elif (( subCat(glyph, "Uppercase") or case(glyph, 1) ) and "tiny" in glyph.name):
		return u"""/H.tiny/H.tiny {0} /H.tiny/o/H.tiny/o {0} /o/o""".format(glyphName)

	elif ( subCat(glyph, "Uppercase") or case(glyph, 1) ):
		return u"""HH{0} HOHO{0} OO""".format(glyphName) 
	
	# smallcaps
	elif (subCat(glyph, "Smallcaps") or case(glyph, 3)):
		return u"""/h.sc/h.sc {0} /h.sc/o.sc/h.sc/o.sc {0} /o.sc/o.sc""".format(glyphName)

	# lowercase
	elif ( subCat(glyph, "Lowercase") or case(glyph, 2) ):
		return u"""nn{0} nono{0} oo""".format(glyphName)


	# punctuation
	elif cat(glyph, "Punctuation"):

		strings = []
		single = True
		name = glyph.name

		# if you have alternates for German quotation styles, process separately
		if name == "quotedblleft.salt_german":
			strings.append(u"""HH{0} H{1} HOHO{0} O{1} OO\nnn{0} n{1} nono{0} o{1} oo""".format("/quotedblleft.salt_german", "/quotedblright"))
		
		elif name == "quoteleft.salt_german":
			strings.append(u"""HH{0} H{1} HOHO{0} O{1} OO\nnn{0} n{1} nono{0} o{1} oo""".format("/quoteleft.salt_german", "/quoteright"))
		
		else:
			#process paired punctuation
			pairPunctuation = [('questiondown', 'question'), ('exclamdown', 'exclam'), ('parenleft', 'parenright'), ('bracketleft', 'bracketright'), ('braceleft', 'braceright'), ('guilsinglleft', 'guilsinglright'), ('guilsinglright', 'guilsinglleft'), ('guillemetleft', 'guillemetright'), ('guillemetright', 'guillemetleft'),('quoteleft', 'quoteright'), ('quoteright', 'quoteright'), ('quotesinglbase', 'quoteleft'), ('quotedblleft', 'quotedblright'), ('quotedblright', 'quotedblright'), ('quotedblbase', 'quotedblleft')]

			for pair in pairPunctuation:
				if name in pair:
					single = False
					# match in pairPuctuation
					strings.append(u"""HH{0} H{1} HOHO{0} O{1} OO\nnn{0} n{1} nono{0} o{1} oo""".format("/"+pair[0], "/"+pair[1]))
			
			#defult punctuation string
			if(single):
				strings = [u"""HH{0} H{0} HOHO{0} O{0} OO\nnn{0} n{0} nono{0} o{0} oo""".format(glyphName)]

		return "\n".join(strings)

	elif cat(glyph, "Symbol"):
		numberSymbols = ["/degree", "/minute", "/second", "/literSign"]
		if glyphName in numberSymbols:
			return u"""00{0} 00{0} 11{0} 1101""".format(glyphName)
		else:
			return u"""HH{0} H{0} HOHO{0} O{0} OO\nnn{0} n{0} nono{0} o{0} oo""".format(glyphName)

	# fallback
	else:
		return u"""HOH{0} non HOH{0} HOH non{0} npn\nHHH{0} nnn HHH{0} HHH nnn{0} nnn\nOOO{0} ooo OOO{0} OOO ooo{0} ooo""".format(glyphName)


def main():

	# get active glyph
	layer = Font.selectedLayers[0]
	glyph = layer.parent

	currentString = Font.currentText
	newString =  currentString + "\n" + getContext(glyph)
	Font.currentText = newString

main()