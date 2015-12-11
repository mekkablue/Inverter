#!/usr/bin/env python
# encoding: utf-8

import GlyphsApp
import objc
from Foundation import *
from FilterCodeBase import FilterBase

class Inverter( FilterBase ):

	def title( self ):
		"""
		This is the name as it appears in the menu
		and in the title of the dialog window.
		"""
		try:
			return "Inverter"
		except Exception as e:
			self.logToConsole( "title: %s" % str(e) )
	
	def actionName( self ):
		"""
		This is the title of the button in the settings dialog.
		Use something descriptive like 'Move', 'Rotate', or at least 'Apply'.
		"""
		try:
			return "Invert"
		except Exception as e:
			self.logToConsole( "actionName: %s" % str(e) )
	
	"""
	All 'myValue' and 'myValueField' references are an example.
	They correspond to the 'My Value' field in the .xib file.
	Replace and add your own class variables.
	"""
	
	topEdgeField = objc.IBOutlet()
	bottomEdgeField = objc.IBOutlet()
	overlapField = objc.IBOutlet()
	
	def setup( self ):
		try:
			"""
			Prepares and pre-fills the dialog fields.
			"""
			super( FilterBase, self ).setup()
			FontMaster = self.valueForKey_( "fontMaster" )
			
			# These 2 lines look for saved values (the last ones entered),
			self.topEdge = self.setDefaultFloatValue( "topEdge", 800.0, FontMaster )
			self.topEdgeField.setFloatValue_( self.topEdge )
			self.bottomEdge = self.setDefaultFloatValue( "bottomEdge", -200.0, FontMaster )
			self.bottomEdgeField.setFloatValue_( self.bottomEdge )
			self.overlap = self.setDefaultFloatValue( "overlap", 5.0, FontMaster )
			self.overlapField.setFloatValue_( self.overlap )
			
			self.process_( None )
			return None
		except Exception as e:
			self.logToConsole( "setup: %s" % str(e) )
			# if something goes wrong, you can return an NSError object with details
	
	
	@objc.IBAction
	def setBottomEdge_( self, sender ):
		"""
		Called whenever the corresponding dialog field is changed.
		Gets the contents of the field and puts it into a class variable.
		Add methods like this for each option in the dialog.
		Important: the method name must end with an underscore, e.g., setValue_(),
		otherwise the dialog action will not be able to connect to it.
		"""
		try:
			bottomEdge = sender.floatValue()
			if bottomEdge != self.bottomEdge:
				self.bottomEdge = bottomEdge
				self.process_( None )
		except Exception as e:
			self.logToConsole( "setBottomEdge_: %s" % str(e) )
			
	@objc.IBAction
	def setTopEdge_( self, sender ):
		"""
		Called whenever the corresponding dialog field is changed.
		Gets the contents of the field and puts it into a class variable.
		Add methods like this for each option in the dialog.
		Important: the method name must end with an underscore, e.g., setValue_(),
		otherwise the dialog action will not be able to connect to it.
		"""
		try:
			topEdge = sender.floatValue()
			if topEdge != self.topEdge:
				self.topEdge = topEdge
				self.process_( None )
		except Exception as e:
			self.logToConsole( "setTopEdge_: %s" % str(e) )

	@objc.IBAction
	def setOverlap_( self, sender ):
		"""
		Called whenever the corresponding dialog field is changed.
		Gets the contents of the field and puts it into a class variable.
		Add methods like this for each option in the dialog.
		Important: the method name must end with an underscore, e.g., setValue_(),
		otherwise the dialog action will not be able to connect to it.
		"""
		try:
			overlap = sender.floatValue()
			if overlap != self.overlap:
				self.overlap = overlap
				self.process_( None )
		except Exception as e:
			self.logToConsole( "setOverlap_: %s" % str(e) )
	
	def pathRect( self, bottomLeft, topRight, italicAngle=0.0, downShift=0.0 ):
		try:
			# coordinates of rectangle:
			myCoordinates = [
				[ bottomLeft[0], bottomLeft[1] ],
				[ topRight[0], bottomLeft[1] ],
				[ topRight[0], topRight[1] ],
				[ bottomLeft[0], topRight[1] ]
			]
			
			# build the path:
			rectangle = GSPath()
			for thisPoint in myCoordinates:
				newNode = GSNode()
				newNode.type = 1 # GSLINE
				newNode.position = ( thisPoint[0], thisPoint[1] )
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
			self.logToConsole( "pathRect: %s" % str(e) )
			return None
			
	def processLayerWithValues( self, Layer, topEdge, bottomEdge, overlap ):
		"""
		This is where your code for processing each layer goes.
		This method is the one eventually called by either the Custom Parameter or Dialog UI.
		Don't call your class variables here, just add a method argument for each Dialog option.
		"""
		try:
			# upper and lower edges of rectangle:
			bottomLeft = NSPoint( -overlap, bottomEdge )
			topRight = NSPoint( Layer.width+overlap, topEdge )
			
			# check italic angle and skew origin:
			thisMaster = self.valueForKey_( "fontMaster" )
			skewAngle = thisMaster.italicAngle
			halfXHeight = thisMaster.xHeight / 2.0
			
			# build the rectangle path:
			rectangle = self.pathRect( bottomLeft, topRight, skewAngle, halfXHeight )
			
			# add it to the decomposed glyph:
			if rectangle:
				Layer.decomposeComponents()
				Layer.removeOverlap()
				Layer.addPath_( rectangle )
				Layer.correctPathDirection()
		except Exception as e:
			self.logToConsole( "processLayerWithValues: %s" % str(e) )

	def processFont_withArguments_( self, Font, Arguments ):
		"""
		Invoked when called as Custom Parameter in an instance at export.
		The Arguments come from the custom parameter in the instance settings. 
		Item 0 in Arguments is the class-name. The consecutive items should be your filter options.
		"""
		try:
			# Set default values for potential arguments (values), just in case:
			topEdge = 800.0
			bottomEdge = -200.0
			overlap = 5.0
			
			# set glyphList (list of glyphs to be processed) to all glyphs in the font
			glyphList = Font.glyphs
			
			if len( Arguments ) > 1:
				
				# change glyphList to include or exclude glyphs
				if "exclude:" in Arguments[-1]:
					excludeList = [ n.strip() for n in Arguments.pop(-1).replace("exclude:","").strip().split(",") ]
					glyphList = [ g for g in glyphList if not g.name in excludeList ]
				elif "include:" in Arguments[-1]:
					includeList = [ n.strip() for n in Arguments.pop(-1).replace("include:","").strip().split(",") ]
					glyphList = [ Font.glyphs[n] for n in includeList ]
			
				# Override defaults with actual values from custom parameter:
				if not "clude:" in Arguments[1]:
					topEdge = Arguments[1].floatValue()
				if not "clude:" in Arguments[2]:
					bottomEdge = Arguments[2].floatValue()
				if not "clude:" in Arguments[3]:
					overlap = Arguments[3].floatValue()
				
			# With these values, call your code on every glyph:
			FontMasterId = Font.fontMasterAtIndex_(0).id
			for Glyph in glyphList:
				Layer = Glyph.layerForKey_( FontMasterId )
				self.processLayerWithValues( Layer, topEdge, bottomEdge, overlap ) # add your class variables here
		except Exception as e:
			self.logToConsole( "processFont_withArguments_: %s" % str(e) )
	
	def selectionOfLayer( self, Layer ):
		"""Compatibility method for old and new versions of Glyphs."""
		try:
			return Layer.selection()
		except:
			return Layer.selection
			
	
	def process_( self, sender ):
		"""
		This method gets called when the user invokes the Dialog.
		"""
		try:
			# Create Preview in Edit View, and save & show original in ShadowLayers:
			ShadowLayers = self.valueForKey_( "shadowLayers" )
			Layers = self.valueForKey_( "layers" )
			checkSelection = True
			for k in range(len( ShadowLayers )):
				ShadowLayer = ShadowLayers[k]
				Layer = Layers[k]
				Layer.setPaths_( NSMutableArray.alloc().initWithArray_copyItems_( ShadowLayer.pyobjc_instanceMethods.paths(), True ) )
				Layer.setSelection_( NSMutableArray.array() )
				shadowLayerSelection = self.selectionOfLayer(ShadowLayer)
				if len(shadowLayerSelection) > 0 and checkSelection:
					for i in range(len( ShadowLayer.paths )):
						currShadowPath = ShadowLayer.paths[i]
						currLayerPath = Layer.paths[i]
						for j in range(len(currShadowPath.nodes)):
							currShadowNode = currShadowPath.nodes[j]
							if shadowLayerSelection.containsObject_( currShadowNode ):
								Layer.addSelection_( currLayerPath.nodes[j] )
								
				self.processLayerWithValues( Layer, self.topEdge, self.bottomEdge, self.overlap )
			Layer.clearSelection()
		
			# Save the values in the FontMaster. But could be saved in UserDefaults, too.
			FontMaster = self.valueForKey_( "fontMaster" )
			FontMaster.userData[ "topEdge"    ] = NSNumber.numberWithFloat_( self.topEdge    )
			FontMaster.userData[ "bottomEdge" ] = NSNumber.numberWithFloat_( self.bottomEdge )
			FontMaster.userData[ "overlap"    ] = NSNumber.numberWithFloat_( self.overlap    )
			
			# call the superclass to trigger the immediate redraw:
			super( FilterBase, self ).process_( sender )
		except Exception as e:
			self.logToConsole( "process_: %s" % str(e) )
