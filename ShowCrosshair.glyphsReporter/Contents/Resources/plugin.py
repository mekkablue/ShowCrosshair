# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

from GlyphsApp import *
from GlyphsApp.plugins import *
from GlyphsApp.plugins import setUpMenuHelper
import math

class ShowCrosshair(ReporterPlugin):

	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Crosshair', 
			'de': u'Fadenkreuz',
			'es': u'cruz',
			'fr': u'réticule',
		})
		NSUserDefaults.standardUserDefaults().registerDefaults_({
				"com.mekkablue.ShowCrosshair.universalCrosshair": 1,
				"com.mekkablue.ShowCrosshair.showCoordinates": 0,
				"com.mekkablue.ShowCrosshair.fontSize": 10.0
			})
		# self.universalCrosshair = bool( Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"] )
		self.controller = None
		
	def background(self, layer):
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsDragging = toolEventHandler.dragging()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"
		crossHairCenter = self.mousePosition()
		shouldDisplay = (bool(Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"]) and not toolIsTextTool) or toolIsDragging
		if crossHairCenter.x < NSNotFound and shouldDisplay:
			italicAngle = 0.0
			try:
				thisMaster = layer.associatedFontMaster()
				italicAngle = math.radians( thisMaster.italicAngle )
			except:
				pass
		
			# draw crosshair:
			offset = 1000000
			tangens = math.tan( italicAngle )
			xOffset = tangens * offset
			cursorOffset = tangens * crossHairCenter.y
			currentScale = self.getScale()
			crosshairPath = NSBezierPath.bezierPath()
			crosshairPath.setLineWidth_( 0.5 / currentScale )
			crosshairPath.moveToPoint_( NSPoint( crossHairCenter.x - xOffset - cursorOffset, -offset ) )
			crosshairPath.lineToPoint_( NSPoint( crossHairCenter.x + xOffset - cursorOffset,  offset ) )
			crosshairPath.moveToPoint_( NSPoint( -offset, crossHairCenter.y ) )
			crosshairPath.lineToPoint_( NSPoint(  offset, crossHairCenter.y ) )
			NSColor.darkGrayColor().set()
			crosshairPath.stroke()
	
	def mousePosition(self):
		view = self.controller.graphicView()
		mousePosition = view.getActiveLocation_(Glyphs.currentEvent())
		return mousePosition
	
	def foregroundInViewCoords(self, layer):
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
				NSForegroundColorAttributeName: NSColor.blackColor()
			}
			displayText = NSAttributedString.alloc().initWithString_attributes_(
				unicode(coordinateText), 
				fontAttributes
			)
			textAlignment = 0 # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
			#font = layer.parent.parent
			lowerLeftCorner = self.controller.viewPort.origin
			displayText.drawAtPoint_alignment_(lowerLeftCorner, textAlignment)

	def mouseDidMove(self, notification):
		if self.controller:
			self.controller.redraw()
		else:
			Glyphs.redraw()
	
	def willActivate(self):
		Glyphs.addCallback(self.mouseDidMove, MOUSEMOVED)
		
	def willDeactivate(self):
		try:
			Glyphs.removeCallback(self.mouseDidMove, MOUSEMOVED)
		except:
			import traceback
			NSLog(traceback.format_exc())
	
	def toggleUniversalCrosshair(self):
		self.toggleSetting("universalCrosshair")
		
	def toggleShowCoordinates(self):
		self.toggleSetting("showCoordinates")
	
	def conditionalContextMenus(self):
		return [
		{
			'name': Glyphs.localize({
				'en': u"Crosshair Options:", 
				'de': u"Fadenkreuz-Einstellungen:", 
				'es': u"Opciones de la cruz:", 
				'fr': u"Options pour le réticule:",
				}), 
			'action': None,
		},
		{
			'name': Glyphs.localize({
				'en': u"Always Show Crosshair", 
				'de': u"Fadenkreuz immer anzeigen", 
				'es': u"Siempre mostrar la cruz", 
				'fr': u"Toujours montrer le réticule",
				}), 
			'action': self.toggleUniversalCrosshair,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.universalCrosshair" ],
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Coordinates", 
				'de': u"Koordinaten anzeigen", 
				'es': u"Mostrar coordinados", 
				'fr': u"Montrer coordonnées",
				}), 
			'action': self.toggleShowCoordinates,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.showCoordinates" ],
		},
		]
		
	
	def toggleSetting(self, prefName):
		pref = "com.mekkablue.ShowCrosshair.%s" % prefName
		oldSetting = bool(Glyphs.defaults[pref])
		Glyphs.defaults[pref] = int(not oldSetting)
	
	def addMenuItemsForEvent_toMenu_(self, event, contextMenu):
		'''
		The event can tell you where the user had clicked.
		'''
		try:
			
			if self.generalContextMenus:
				setUpMenuHelper(contextMenu, self.generalContextMenus, self)
			
			newSeparator = NSMenuItem.separatorItem()
			contextMenu.addItem_(newSeparator)
			
			contextMenus = self.conditionalContextMenus()
			if contextMenus:
				setUpMenuHelper(contextMenu, contextMenus, self)
		
		except:
			import traceback
			NSLog(traceback.format_exc())
	