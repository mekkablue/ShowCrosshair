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
			'jp': u'カーソル照準',
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
			NSColor.disabledControlTextColor().set()
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
				NSForegroundColorAttributeName: NSColor.textColor()
			}
			displayText = NSAttributedString.alloc().initWithString_attributes_(
				unicode(coordinateText), 
				fontAttributes
			)
			textAlignment = 0 # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
			#font = layer.parent.parent
			lowerLeftCorner = self.controller.viewPort.origin
			displayText.drawAtPoint_alignment_(lowerLeftCorner, textAlignment)

		if Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.showThickness"] and not toolIsTextTool:
			mousePosition = self.mousePosition()
			# stem thickness x slice
			f = Glyphs.font
			m = f.selectedFontMaster
			sliceX = mousePosition.x
			miniY = m.descender - 1000*(f.upm/1000.0)
			maxiY = m.ascender + 1000*(f.upm/1000.0)
			prev = miniY
			ys = {}
			for inter in layer.calculateIntersectionsStartPoint_endPoint_decompose_((sliceX,miniY),(sliceX,maxiY),True):
				if prev != miniY and inter.y != maxiY:
					ys[(inter.y-prev)/2+prev] = inter.y-prev
				prev = inter.y

			scale = self.getScale()
			# stem thickness y slice
			sliceY = mousePosition.y
			miniX = -1000*(f.upm/1000.0)
			maxiX = layer.width + 1000*(f.upm/1000.0)
			prev = miniX
			xs = {}
			for inter in layer.calculateIntersectionsStartPoint_endPoint_decompose_((miniX,sliceY),(maxiX,sliceY),True):
				if prev != miniX and inter.x != maxiX:
					xs[(inter.x-prev)/2+prev] = inter.x-prev
				prev = inter.x

			# set font attributes
			fontSize = Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"]
			thicknessFontAttributes = { 
				NSFontAttributeName: NSFont.monospacedDigitSystemFontOfSize_weight_(fontSize,0.0),
				NSForegroundColorAttributeName: NSColor.textColor()
			}

			for key, item in ys.iteritems():
				item = round(item, 1)
				if item != 0:
					x, y = sliceX*scale, (key-m.ascender)*scale
					self.drawThicknessBadge(scale, fontSize, x, y, item)
					self.drawThicknessText(thicknessFontAttributes, x, y, item)

			for key, item in xs.iteritems():
				item = round(item, 1)
				if item != 0:
					x, y = key*scale, (sliceY-m.ascender)*scale
					self.drawThicknessBadge(scale, fontSize, x, y, item)
					self.drawThicknessText(thicknessFontAttributes, x, y, item)

	def drawThicknessBadge(self, scale, fontSize, x, y, value):
		width = len(str(value)) * fontSize * 0.7
		rim = fontSize * 0.3
		badge = NSRect()
		badge.origin = NSPoint( x-width/2, y-fontSize/2-rim )
		badge.size = NSSize( width, fontSize + rim*2 )
		NSColor.colorWithCalibratedRed_green_blue_alpha_( 1,1,1,1 ).set()
		NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_( badge, fontSize*0.5, fontSize*0.5 ).fill()

	def drawThicknessText(self, thicknessFontAttributes, x, y, item):
		displayText = NSAttributedString.alloc().initWithString_attributes_(
			unicode(item), 
			thicknessFontAttributes
		)
		displayText.drawAtPoint_alignment_((x, y), 4)


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

	def toggleShowThickness(self):
		self.toggleSetting("showThickness")
	
	def conditionalContextMenus(self):
		return [
		{
			'name': Glyphs.localize({
				'en': u"Crosshair Options:", 
				'de': u"Fadenkreuz-Einstellungen:", 
				'es': u"Opciones de la cruz:", 
				'fr': u"Options pour le réticule:",
				'jp': u"照準プラグインオプション",
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
				}), 
			'action': self.toggleShowCoordinates,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.showCoordinates" ],
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Thickness", 
				'de': u"Dicke anzeigen", 
				'es': u"Espesor coordinados", 
				'fr': u"Afficher l'épaisseur",
				'jp': u"縦横の太さを表示",
				}), 
			'action': self.toggleShowThickness,
			'state': Glyphs.defaults[ "com.mekkablue.ShowCrosshair.showThickness" ],
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
	