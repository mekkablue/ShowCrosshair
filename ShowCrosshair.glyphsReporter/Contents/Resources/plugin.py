# encoding: utf-8
from __future__ import division, print_function, unicode_literals

#######################################################################################
#
# Reporter Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#######################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from math import radians, tan

class ShowCrosshair(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Crosshair', 
			'de': u'Fadenkreuz',
			'es': u'cruz',
			'fr': u'réticule',
			'jp': u'カーソル照準',
			'zh': u'✨准星线',
		})
		
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.universalCrosshair", 1)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.showCoordinates", 0)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.showThickness", 0)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.fontSize", 10.0)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.ignoreItalicAngle", 0)
		
		self.generalContextMenus = [
		{
			'name': Glyphs.localize({
				'en': u"Crosshair Options:", 
				'de': u"Fadenkreuz-Einstellungen:", 
				'es': u"Opciones de la cruz:", 
				'fr': u"Options pour le réticule:",
				'jp': u"照準プラグインオプション",
				'zh': u"准星线选项",
				}), 
			'action': None,
		},
		{
			'name': Glyphs.localize({
				'en': u"Always Show Crosshair", 
				'de': u"Fadenkreuz immer anzeigen", 
				'es': u"Siempre mostrar la cruz", 
				'fr': u"Toujours afficher le réticule",
				'jp': u"照準を常に表示",
				'zh': u"始终显示准星线",
				}), 
			'action': self.toggleUniversalCrosshair,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.universalCrosshair" ],
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Coordinates", 
				'de': u"Koordinaten anzeigen", 
				'es': u"Mostrar coordinados", 
				'fr': u"Afficher les coordonnées",
				'jp': u"マウスの座標を左下に表示",
				'zh': u"在左下角显示坐标值",
				}), 
			'action': self.toggleShowCoordinates,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.showCoordinates" ],
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Thicknesses", 
				'de': u"Dicken anzeigen", 
				'es': u"Mostrar grosores", 
				'fr': u"Afficher les épaisseurs",
				'jp': u"縦横の太さを表示",
				'zh': u"显示纵横坐标差",
				}), 
			'action': self.toggleShowThickness,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.showThickness" ],
		},
		]
	
	@objc.python_method
	def drawCircle(self, center, size):
		radius = size*0.5
		circle = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
			NSMakeRect(center.x-radius, center.y-radius, size, size),
			radius,
			radius,
			)
		circle.fill()
	
	@objc.python_method
	def foreground(self, layer):
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsDragging = toolEventHandler.dragging()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"
		shouldDisplay = (Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.universalCrosshair"] and not toolIsTextTool) or toolIsDragging
		
		if Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.showThickness"] and shouldDisplay:
			font = Glyphs.font
			master = layer.associatedFontMaster()
			scale = self.getScale()
			mousePosition = self.mousePosition()
			
			# intersection markers:
			handleSize = self.getHandleSize() * scale**-0.7
			NSColor.separatorColor().set()

			# stem thickness horizontal slice
			sliceY = mousePosition.y
			minX = -1000*(font.upm/1000.0)
			maxX = layer.width + 1000*(font.upm/1000.0)
			prev = minX
			xs = {}
			intersections = layer.calculateIntersectionsStartPoint_endPoint_decompose_(
				(minX,sliceY),
				(maxX,sliceY),
				True,
			)
			for inter in intersections:
				if inter.x != maxX:
					self.drawCircle(inter, handleSize)
					if prev != minX:
						xs[(inter.x-prev)/2+prev] = inter.x-prev
				prev = inter.x
			
			# stem thickness vertical slice
			sliceX = mousePosition.x
			minY = master.descender - 1000*(font.upm/1000.0)
			maxY = master.ascender  + 1000*(font.upm/1000.0)
			prev = minY
			ys = {}
			verticalIntersections = layer.calculateIntersectionsStartPoint_endPoint_decompose_(
				self.italicize( NSPoint(sliceX,minY), italicAngle=master.italicAngle, pivotalY=sliceY ),
				self.italicize( NSPoint(sliceX,maxY), italicAngle=master.italicAngle, pivotalY=sliceY ),
				True,
				)
			for inter in verticalIntersections:
				if inter.y != maxY:
					self.drawCircle(inter, handleSize)
					if prev != minY:
						ys[(inter.y-prev)/2+prev] = inter.y-prev
				prev = inter.y

			# set font attributes
			fontSize = Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"]
			thicknessFontAttributes = { 
				NSFontAttributeName: NSFont.monospacedDigitSystemFontOfSize_weight_(fontSize/scale,0.0),
				NSForegroundColorAttributeName: NSColor.textColor()
			}
			
			# number badges on vertical slice:
			for key in ys:
				item = ys[key]
				item = round(item, 1)
				if item != 0:
					x, y = sliceX, key
					# adjust x for italic angle if necessary:
					if master.italicAngle:
						x = self.italicize( NSPoint(x,y), italicAngle=master.italicAngle, pivotalY=sliceY ).x
					self.drawThicknessBadge(scale, fontSize, x, y, item)
					self.drawThicknessText(thicknessFontAttributes, x, y, item)
					
			# number badges on horizontal slice:
			for key in xs:
				item = xs[key]
				item = round(item, 1)
				if item != 0:
					x, y = key, sliceY
					self.drawThicknessBadge(scale, fontSize, x, y, item)
					self.drawThicknessText(thicknessFontAttributes, x, y, item)
	
	@objc.python_method
	def italicize( self, thisPoint, italicAngle=0.0, pivotalY=0.0 ):
		"""
		Returns the italicized position of an NSPoint 'thisPoint'
		for a given angle 'italicAngle' and the pivotal height 'pivotalY',
		around which the italic slanting is executed, usually half x-height.
		Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
		"""
		if Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.ignoreItalicAngle"]:
			return thisPoint
		else:
			x = thisPoint.x
			yOffset = thisPoint.y - pivotalY # calculate vertical offset
			italicAngle = radians( italicAngle ) # convert to radians
			tangens = tan( italicAngle ) # math.tan needs radians
			horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
			x += horizontalDeviance # x of point that is yOffset from pivotal point
			return NSPoint( x, thisPoint.y )
	
	@objc.python_method
	def background(self, layer):
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsDragging = toolEventHandler.dragging()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"
		crossHairCenter = self.mousePosition()
		shouldDisplay = (Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.universalCrosshair"] and not toolIsTextTool) or toolIsDragging
		
		if crossHairCenter.x < NSNotFound and shouldDisplay:
			# determine italic angle:
			italicAngle = 0.0
			try:
				thisMaster = layer.associatedFontMaster()
				italicAngle = thisMaster.italicAngle
			except:
				pass
			
			# set up bezierpath:
			offset = 1000000
			NSColor.disabledControlTextColor().set() # subtle grey
			crosshairPath = NSBezierPath.bezierPath()
			crosshairPath.setLineWidth_( 0.75 / self.getScale() )

			# vertical line:
			crosshairPath.moveToPoint_( self.italicize( NSPoint(crossHairCenter.x,-offset), italicAngle=italicAngle, pivotalY=crossHairCenter.y) )
			crosshairPath.lineToPoint_( self.italicize( NSPoint(crossHairCenter.x,+offset), italicAngle=italicAngle, pivotalY=crossHairCenter.y) )
			
			# horizontal line:
			crosshairPath.moveToPoint_( NSPoint(-offset,crossHairCenter.y) )
			crosshairPath.lineToPoint_( NSPoint(+offset,crossHairCenter.y) )

			# execute stroke:
			crosshairPath.stroke()
	
	def mousePosition(self):
		view = self.controller.graphicView()
		mousePosition = view.getActiveLocation_(Glyphs.currentEvent())
		return mousePosition
	
	@objc.python_method
	def foregroundInViewCoords(self):
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"

		if Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.showCoordinates"] and not toolIsTextTool:
			mousePosition = self.mousePosition()
			coordinateText = "%4d, %4d" % (
				round(mousePosition.x), 
				round(mousePosition.y)
			)
			
			fontSize = Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"]
			fontAttributes = { 
				#NSFontAttributeName: NSFont.labelFontOfSize_(10.0),
				NSFontAttributeName: NSFont.monospacedDigitSystemFontOfSize_weight_(fontSize,0.0),
				NSForegroundColorAttributeName: NSColor.textColor()
			}
			displayText = NSAttributedString.alloc().initWithString_attributes_(
				coordinateText, 
				fontAttributes
			)
			textAlignment = 0 # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
			#font = layer.parent.parent
			lowerLeftCorner = self.controller.viewPort.origin
			displayText.drawAtPoint_alignment_(lowerLeftCorner, textAlignment)

	@objc.python_method
	def drawThicknessBadge(self, scale, fontSize, x, y, value):
		width = len(str(value)) * fontSize * 0.7 / scale
		rim = fontSize * 0.3 / scale
		badge = NSRect()
		badge.origin = NSPoint( x-width/2, y-fontSize/2-rim )
		badge.size = NSSize( width, fontSize + rim*2 )
		NSColor.textBackgroundColor().set()
		NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_( badge, fontSize*0.5, fontSize*0.5 ).fill()

	@objc.python_method
	def drawThicknessText(self, thicknessFontAttributes, x, y, item):
		displayText = NSAttributedString.alloc().initWithString_attributes_(
			str(item), 
			thicknessFontAttributes
		)
		displayText.drawAtPoint_alignment_((x, y), 4)

	def mouseDidMove_(self, notification):
		if self.controller:
			self.controller.redraw()
		else:
			Glyphs.redraw()

	def willActivate(self):
		Glyphs.addCallback(self.mouseDidMove_, MOUSEMOVED)
	
	def willDeactivate(self):
		try:
			Glyphs.removeCallback(self.mouseDidMove_, MOUSEMOVED)
		except:
			import traceback
			NSLog(traceback.format_exc())
	
	def toggleUniversalCrosshair(self):
		self.toggleSetting("universalCrosshair")
	
	def toggleShowCoordinates(self):
		self.toggleSetting("showCoordinates")

	def toggleShowThickness(self):
		self.toggleSetting("showThickness")
	
	@objc.python_method
	def toggleSetting(self, prefName):
		pref = "com.mekkablue.ShowCrosshair.%s" % prefName
		oldSetting = Glyphs.boolDefaults[pref]
		Glyphs.defaults[pref] = int(not oldSetting)
	
	# def addMenuItemsForEvent_toMenu_(self, event, contextMenu):
	# 	'''
	# 	The event can tell you where the user had clicked.
	# 	'''
	# 	try:
	#
	# 		if self.generalContextMenus:
	# 			setUpMenuHelper(contextMenu, self.generalContextMenus, self)
	#
	# 		newSeparator = NSMenuItem.separatorItem()
	# 		contextMenu.addItem_(newSeparator)
	#
	# 		contextMenus = self.conditionalContextMenus()
	# 		if contextMenus:
	# 			setUpMenuHelper(contextMenu, contextMenus, self)
	#
	# 	except:
	# 		import traceback
	# 		NSLog(traceback.format_exc())

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
