# Glyphs-Scripts

Public repository of Glyphs scripts for the Glyphs font editor by Occupant Fonts.


## Align Selected Nodes with Background

Align selected nodes with the nearest background node unless it is already taken by a previously moved node.

## Delete Annotations

Clears all notes on the currently selected layer. Useful with a shortcut when using the [QA Tool](https://github.com/morisawausa/QATool)


## Harmonize Ratios Across Masters

This script responds to a selected oncurve point by measuring the length ratio of the surrounding offcurves and solving for the same ratio in all other masters, up to numerical precision. Having consistent offcurve ratios is useful for ensuring controlled interpolation across a design space in a variable font.


## Import Designspace Substitutions

This script opens a GUI which allows you to specify a filepath to a `.designspace` file. The script will attempt to read the substitution structure out of the `.designspace` file’s `<rules>` table, and scan across static instances in this font, assigning corresponding substitution rules to them, so that their behavior matches the variable font.

This script does some rudimentary correctness checking, and will ensure that The designspace file you load has the same number of axes, with the same names, in the same order as in the Glyphs open font.

## Italic Bowtie

A Glyphs port of [Italic Bowtie](https://github.com/FontBureau/fbOpenTools/tree/master/ItalicBowtie) originally developed for Robofont by Cyrus Highsmith and DJR.


## Make Angle 90 Degrees

Makes the angle at the selected corner point 90 degrees. Moves the selected point along the longer of the two neighboring segments to find the 90 degree point.

## Rotate Glyph 180

Rotate the current glyph 180°. Created to assign a shortcut.

