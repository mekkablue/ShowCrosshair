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


from GlyphsApp.plugins import *
import math

class ShowCrosshair(ReporterPlugin):

	def settings(self):
		self.menuName = Glyphs.localize({'en': u'Crosshair', 'de': u'Fadenkreuz'})
		NSUserDefaults.standardUserDefaults().registerDefaults_({
				"com.mekkablue.ShowCrosshair.universalCrosshair": 1
			})
		# self.universalCrosshair = bool( Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"] )
		
		self.generalContextMenus = [
			{
				'name': Glyphs.localize({
					'en': u'Toggle Crosshair',
					'de': u'Fadenkreuz umschalten'
				}), 
				'action': self.toggleUniversalCrosshair
			},
		]
		
	def background(self, layer):
		currentController = self.controller
		view = currentController.graphicView()
		toolIsDragging = currentController.view().window().windowController().toolEventHandler().dragging()
		crossHairCenter = view.getActiveLocation_(Glyphs.currentEvent())
		shouldDisplay = bool(Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"]) or toolIsDragging
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

	def mouseDidMove(self, notification):
		self.controller.view().setNeedsDisplay_(True)
	
	def willActivate(self):
		Glyphs.addCallback(self.mouseDidMove, MOUSEMOVED)
		
	def willDeactivate(self):
		try:
			Glyphs.removeCallback(self.mouseDidMove, MOUSEMOVED)
		except:
			NSLog(traceback.format_exc())
	
	def toggleUniversalCrosshair(self):
		Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"] = int(not bool(Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"]))
		
