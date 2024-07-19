from __future__ import print_function
from functools import reduce
#MenuTitle: Import Designspace Substitutions (GUI)
# -*- coding: utf-8 -*-
#
# This script opens a GUI which allows you to specify a filepath
# to a .designspace file. The script will attempt to read the substitution
# structure out of the .designspace file's <rules> table, and scan across
# static instances in this font, assigning corresponding substitution rules to
# them, so that their behavior matches the variable font.
#
# This script does some rudimentary correctness checking, and will ensure that
# The designspace file you load has the same number of axes, with the same names,
# in the same order as in the Glyphs open font.
__doc__="""(GUI) Allows you to update instance substitution rules
in the open font with the substitutions in a chosen .designspace file. 
"""

import os.path
from vanilla import *
from vanilla.dialogs import getFile
import xml.etree.ElementTree as ET

DEFAULT_OUTPUT_HEADER = 'Output'
DEFAULT_OUTPUT_TEXT = 'Details will appear here during import.'


class SubstititionImportWindow():
	def __init__(self):
		self.filepath = ""

		self.window = FloatingWindow(
			(250, 325),
			"Import Substitutions",
			textured=False);

		self.window.header = TextBox(
			(10, 10, -10, 20),
			"Import Designspace File",
			alignment="left",
			sizeStyle="regular")

		self.window.instructions = TextBox(
			(10, 35, -10, 100),
			"This tool will help you import a designspace file generated from the Variable Font Visualizer into the static instances of this font. Click below and choose a designspace file to import.",
			alignment="left",
			sizeStyle="mini")

		self.window.button = Button(
			(10, 120, -10, 30),
			"Import Substitutions",
			callback=self.getDesignspaceFilepath)

		self.window.line = HorizontalLine((0, 155, -0, 1))

		self.window.output_header = TextBox(
			(10, 165, -10, 20),
			DEFAULT_OUTPUT_HEADER,
			alignment="left",
			sizeStyle="regular")

		self.window.output_text = TextBox(
			(10, 190, -10, 100),
			DEFAULT_OUTPUT_TEXT,
			alignment="left",
			sizeStyle="mini")

		self.window.open()


	def getDesignspaceFilepath(self, sender):
		self.resetResponse()
		files = getFile(title=".designspace", messageText="Select a Designspace File")
		if len(files) > 0:
			self.filepath = files[0]
			self.processDesignspace(None)


	def resetResponse(self):
		self.setResponse(DEFAULT_OUTPUT_HEADER, DEFAULT_OUTPUT_TEXT)


	def setResponse(self, header, text):
		self.window.output_header.set(header)
		self.window.output_text.set(text)


	def processDesignspace(self, sender):

		if not os.path.exists(self.filepath):
			self.setResponse("No Such File", "Couldn't find a file at that path.")
			return False

		if '.designspace' not in self.filepath:
			self.setResponse(
				"Not A Designspace File",
				"Please specify a .designspace file.\n\nFind the .designspace file you'd like to import in your Finder, option-right-click on it, and hit 'Copy as pathname'.")
			return False


		try:
			ds_root = ET.parse(self.filepath).getroot()
		except e:
			self.setResponse("Malformed XML")
			self.setResponse("We couldn't parse the XML in your .designspace file. Please check the file for syntax errors.")
			return False

		# Step One: Validate that the axis values
		# set in this designspace file correspond to
		# the current Glyphs file, otherwise abort.
		g_axes = Glyphs.font.axes
		ds_axes = ds_root.findall('axes/axis');
		ds_maxima = map(lambda r: int(r.get('maximum')), ds_axes)

		# Step Two: Traverse the rules, and for
		# each rule condition, check to see if any of the isntances
		# fall in side the condition.
		ds_rules = ds_root.findall('rules/rule')
		g_instances = Glyphs.font.instances

		if len(g_axes) != len(ds_axes):
			self.setResponse("Wrong Axis Count", "The font has %s registered axes, but the .designspace has %s. Are you sure this is the right file?" % (len(g_axes), len(ds_axes)))
			return False

		paired_axes = zip(g_axes, map(lambda axis: {"Name": axis.get('name'), "Tag": axis.get("tag")}, ds_axes))
		valid = reduce(lambda p, a: a[0]['Name'] == a[1]['Name'] and a[0]['Tag'] == a[1]['Tag'] and p, paired_axes, True)

		if (not valid):
			self.setResponse("Mismatched Axes", "The open font and .designspace files have mismatching axes. Are you sure this is the right file?")
			return False

		if len(g_instances) == 0:
			self.setResponse("No Instances", "It looks like there aren't any static instances defined for this font. Add some instances and try again.")
			return False

		if len(ds_rules) == 0:
			self.setResponse("No Designspace Rules", "It looks like there aren't any designspace rules for this .designspace file. Add some substitution rules and try again.")
			return False

		renaming_map = dict()

		def instance_is_in_rect(instance, rect):
			def valid_check(points):
				(index, (p, i)) = points
				return (i[0] <= p and p < i[1]) or (p == ds_maxima[index] and i[1] == ds_maxima[index])

			points_in_intervals = enumerate(zip(instance.axes, rect))
			valid_per_axis = map(valid_check, points_in_intervals)
			return reduce(lambda a, b: a and b, valid_per_axis, True);


		for ds_rule in ds_rules:

			ds_cond_sets = ds_rule.findall('conditionset')
			print(ds_cond_sets)
			ds_subs = map(lambda s: (s.get('name'), s.get('with')), ds_rule.findall('sub'))
			print(ds_subs)


			for g_index, g_instance in enumerate(Glyphs.font.instances):

				for ds_cond_set in ds_cond_sets:
					ds_conds = ds_cond_set.findall('condition')
					ds_conds = map(lambda c: (float(c.get('minimum')), float(c.get('maximum'))), ds_conds)

					if instance_is_in_rect(g_instance, ds_conds):

						rename_string = map(lambda gs: "%s=%s" % gs, ds_subs)
						if g_instance.name not in renaming_map:
							renaming_map[g_instance.name] = {
								"index": g_index,
								"substitutions": rename_string
							}
						else:
							renaming_map[g_instance.name]['substitutions'] += rename_string

						break


		print("Substitutions Generated from .designspace:\n")
		instance_count = 0

		# TODO: find a better way to delete custom parameters.
		for g_index, instance in enumerate(Glyphs.font.instances):
			while Glyphs.font.instances[g_index].customParameters['Rename Glyphs'] != "":
				Glyphs.font.instances[g_index].customParameters['Rename Glyphs'] = ""

		sorted_keys = sorted(renaming_map.keys())

		print(renaming_map);

		for g_name in sorted_keys:
			g_index = renaming_map[g_name]['index']
			renaming_string = ', '.join(renaming_map[g_name]['substitutions'])
			substitutions_list = '\n'.join(renaming_map[g_name]['substitutions'])

			print(g_name)
			print('---')
			print(substitutions_list)
			print('\n')

			del(Glyphs.font.instances[g_index].customParameters['Rename Glyphs'])
			Glyphs.font.instances[g_index].customParameters['Rename Glyphs'] = renaming_string

			instance_count += 1

		self.setResponse("Success!", "Processed %d rulesets across %d instances. More information is available in the macro window." % (len(ds_rules), instance_count))
		return True



SubstititionImportWindow()
