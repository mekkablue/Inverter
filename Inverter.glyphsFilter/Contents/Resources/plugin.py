# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

import objc
from GlyphsApp.plugins import *

class Inverter(FilterWithDialog):
	
	# Definitions of IBOutlets
	dialog = objc.IBOutlet()
	topEdgeField = objc.IBOutlet()
	bottomEdgeField = objc.IBOutlet()
	overlapField = objc.IBOutlet()
	
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Inverter',
			'de': 'Umkehren',
			'fr': 'Inverter'
			'es': 'Invertar',
			'it': 'Invertire',
			'pt': 'Inverter',
		})
		
		NSUserDefaults.standardUserDefaults().registerDefaults_({
			"com.mekkablue.Inverter.topEdge": 800.0,
			"com.mekkablue.Inverter.bottomEdge": -200.0,
			"com.mekkablue.Inverter.overlap": 5.0,
			})
		
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)
	
	# On dialog show
	@objc.python_method
	def start(self):
		# Set value of text field
		self.topEdgeField.setFloatValue_( Glyphs.defaults['com.mekkablue.Inverter.topEdge'] )
		self.bottomEdgeField.setFloatValue_( Glyphs.defaults['com.mekkablue.Inverter.bottomEdge'] )
		self.overlapField.setFloatValue_( Glyphs.defaults['com.mekkablue.Inverter.overlap'] )
		self.topEdgeField.becomeFirstResponder()
	
	@objc.IBAction
	def setTopEdge_( self, sender ):
		# Store value coming in from dialog
		Glyphs.defaults['com.mekkablue.Inverter.topEdge'] = sender.floatValue()
		# Trigger redraw
		self.update()

	@objc.IBAction
	def setBottomEdge_( self, sender ):
		Glyphs.defaults['com.mekkablue.Inverter.bottomEdge'] = sender.floatValue()
		self.update()
			
	@objc.IBAction
	def setOverlap_( self, sender ):
		Glyphs.defaults['com.mekkablue.Inverter.overlap'] = sender.floatValue()
		self.update()
	
	@objc.python_method
	def pathRect( self, bottomLeft, topRight, italicAngle=0.0, downShift=0.0 ):
		try:
			# coordinates of rectangle:
			myCoordinates = (
				NSPoint( bottomLeft.x, bottomLeft.y ),
				NSPoint( topRight.x, bottomLeft.y ),
				NSPoint( topRight.x, topRight.y ),
				NSPoint( bottomLeft.x, topRight.y )
			)
			
			# build the path:
			rectangle = GSPath()
			for thisPoint in myCoordinates:
				newNode = GSNode()
				newNode.type = 1 # GSLINE
				newNode.position = thisPoint
				rectangle.nodes.append( newNode )
			rectangle.closed = True
			
			# skew if there is an italic angle:
			if not italicAngle == 0.0:
				
				# calculate & build skew transformation:
				from math import tan, pi
				skewTangens = tan( italicAngle/180*pi )
				skew = NSAffineTransform.transform()
				skew.setTransformStruct_( (1.0, 0.0, skewTangens, 1.0, 0.0, downShift) )
				skew.translateXBy_yBy_( 0.0, -downShift )
				
				# apply transformation to points of rectangle:
				for thisNode in rectangle.nodes:
					thisNode.position = skew.transformPoint_( thisNode.position )
			
			return rectangle

		except Exception as e:
			import traceback
			print(traceback.format_exc())
			print("pathRect: %s" % str(e))
	
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		topEdge = float( Glyphs.defaults['com.mekkablue.Inverter.topEdge'] )
		bottomEdge = float( Glyphs.defaults['com.mekkablue.Inverter.bottomEdge'] )
		overlap = float( Glyphs.defaults['com.mekkablue.Inverter.overlap'] )
		
		# Called on font export, override with values from customParameters:
		if 'top' in customParameters:
			topEdge = customParameters['top']
		if 'bottom' in customParameters:
			bottomEdge = customParameters['bottom']
		if 'overlap' in customParameters:
			overlap = customParameters['overlap']
		
		# upper and lower edges of rectangle:
		bottomLeft = NSPoint( -overlap, bottomEdge )
		topRight = NSPoint( layer.width+overlap, topEdge )
		
		# check italic angle and skew origin:
		thisMaster = layer.associatedFontMaster()
		skewAngle = thisMaster.italicAngle
		halfXHeight = thisMaster.xHeight / 2.0
		
		# build the rectangle path:
		rectangle = self.pathRect( bottomLeft, topRight, skewAngle, halfXHeight )
		
		# add it to the decomposed glyph:
		if rectangle:
			layer.decomposeComponents()
			layer.removeOverlap()
			layer.paths.append( rectangle )
			layer.correctPathDirection()

	@objc.python_method
	def generateCustomParameter( self ):
		return "%s; top:%s; bottom:%s; overlap:%s" % (
			self.__class__.__name__,
			Glyphs.defaults['com.mekkablue.Inverter.topEdge'],
			Glyphs.defaults['com.mekkablue.Inverter.bottomEdge'],
			Glyphs.defaults['com.mekkablue.Inverter.overlap'],
			)
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
