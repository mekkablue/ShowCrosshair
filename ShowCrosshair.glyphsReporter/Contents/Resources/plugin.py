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
from GlyphsApp import Glyphs, MOUSEMOVED, MOUSEDOWN, MOUSEUP
from GlyphsApp.plugins import ReporterPlugin
from math import radians, tan, hypot
from Foundation import NSZeroPoint
from Cocoa import NSBezierPath, NSColor, NSImage, NSMenu, NSMenuItem, NSPoint, NSFont, NSFontAttributeName, NSForegroundColorAttributeName, NSAttributedString, NSSize, NSRect, NSMakeRect, NSLog, NSNotFound, NSOnState
# to set context menu set state
# from AppKit import NSBundle
# path = __file__
# Bundle = NSBundle.bundleWithPath_(path[:path.rfind("Contents/Resources/")])


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

		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.alwaysCrosshair", 1)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.showCoordinates", 0)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.showThickness", 0)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.fontSize", 10.0)
		Glyphs.registerDefault("com.mekkablue.ShowCrosshair.ignoreItalicAngle", 0)

		# attempt deleting older default name
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"]:
			del Glyphs.defaults["com.mekkablue.ShowCrosshair.universalCrosshair"]

		self.generalContextMenus = self.buildContextMenus()
		self.dragStart = None  # drag origin point

	@objc.python_method
	def buildContextMenus(self):

		# Dot Icon
		dot = None
		try:
			# dot = NSImage.imageWithSystemSymbolName_accessibilityDescription_("checkmark.circle", None)
			dot = NSImage.imageWithSystemSymbolName_accessibilityDescription_("circlebadge.fill", None)
			dot.setTemplate_(True)  # Makes the icon blend in with the toolbar.
		except:
			pass

		# Empty list of context menu items
		contextMenus = []

		onlyWhileDraggingOption = {
			'en': "Only While Dragging",
			'de': "Nur beim Ziehen",
			'es': "Solo al arrastrar",
			'fr': "Uniquement pendant le glissement",
			'jp': "ドラッグ中のみ表示",
			'zh': "仅在拖动时显示",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(onlyWhileDraggingOption), self.toggleUniversalCrosshair, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.alwaysCrosshair"] is False:
			menu.setState_(NSOnState)
		contextMenus.append({"menu": menu})

		thicknessOption = {
			'en': "Show Thicknesses",
			'de': "Dicken anzeigen",
			'es': "Mostrar grosores",
			'fr': "Afficher les épaisseurs",
			'jp': "縦横の太さを表示",
			'zh': "显示纵横坐标差",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(thicknessOption), self.toggleShowThickness, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.showThickness"]:
			menu.setState_(NSOnState)
		contextMenus.append({"menu": menu})

		# ---------- Separator
		contextMenus.append({"menu": NSMenuItem.separatorItem()})

		coordinatePlacesTitle = {
			'en': "Show Coordinates At",
			'de': "Koordinaten anzeigen bei",
			'es': "Mostrar coordinados",
			'fr': "Afficher les coordonnées",
			'jp': "カーソル座標の表示位置",
			'zh': "在左下角显示坐标值",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(coordinatePlacesTitle), None, "")
		menu.setEnabled_(False)
		contextMenus.append({"menu": menu})

		bottomleftTitle = {
			'en': "Bottom Left",
			'de': "Unten links",
			'es': "Abajo a la izquierda",
			'fr': "En bas à gauche",
			'jp': "左下",
			'zh': "左下角",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(bottomleftTitle), self.toggleShowCoordinates0, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.showCoordinates"] == 0:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		topleftTitle = {
			'en': "Top Left",
			'de': "Oben links",
			'es': "Arriba a la izquierda",
			'fr': "En haut à gauche",
			'jp': "左上",
			'zh': "左上角",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(topleftTitle), self.toggleShowCoordinates1, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.showCoordinates"] == 1:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		alongAxisTitle = {
			'en': "Along Axis Lines",
			'de': "Entlang der Achsenlinien",
			'es': "A lo largo de las líneas del eje",
			'fr': "Le long des lignes d'axe",
			'jp': "軸線の脇",
			'zh': "沿轴线",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(alongAxisTitle), self.toggleShowCoordinates2, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.showCoordinates"] == 2:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		nextToCursorTitle = {
			'en': "Next To Cursor",
			'de': "Neben dem Mauszeiger",
			'es': "Junto al cursor",
			'fr': "À côté du curseur",
			'jp': "カーソルの脇",
			'zh': "光标旁边",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(nextToCursorTitle), self.toggleShowCoordinates3, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.showCoordinates"] == 3:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		# ---------- Separator
		contextMenus.append({"menu": NSMenuItem.separatorItem()})

		textSizesTitle = {
			'en': "Numbers Size",
			'de': "Zahlengröße",
			'es': "Tamaño de números",
			'fr': "Taille des chiffres",
			'jp': "数字サイズ",
			'zh': "数字大小",
		}
		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(Glyphs.localize(textSizesTitle), None, "")
		menu.setEnabled_(False)
		contextMenus.append({"menu": menu})


		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('8', self.toggleFontSize8, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"] == 8:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('9', self.toggleFontSize9, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"] == 9:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('10', self.toggleFontSize10, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"] == 10:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('12', self.toggleFontSize12, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"] == 12:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('14', self.toggleFontSize14, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"] == 14:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		menu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('18', self.toggleFontSize18, "")
		if Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"] == 18:
			menu.setState_(NSOnState)
			if dot:
				menu.setOnStateImage_(dot)
		contextMenus.append({"menu": menu})

		# Put them into a sub menu
		menu = NSMenuItem.alloc().init()
		# menu.setTitle_('Show Crosshair')
		menu.setTitle_(Glyphs.localize({
			'en': u'Crosshair Settings',
			'de': u'Fadenkreuzeinstellungen',
			'es': u'Ajustes de la cruz',
			'fr': u'Paramètres du réticule',
			'jp': u'カーソル照準設定',
			'zh': u'✨准星线设置',
		}))
		subMenu = NSMenu.alloc().init()

		for item in contextMenus:

			item['menu'].setTarget_(self)
			subMenu.addItem_(item['menu'])
		menu.setSubmenu_(subMenu)

		return [{'menu': menu}]

	@objc.python_method
	def drawCircle(self, center, size):
		radius = size * 0.5
		circle = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
			NSMakeRect(center.x - radius, center.y - radius, size, size),
			radius,
			radius,
		)
		circle.fill()

	@objc.python_method
	def foreground(self, layer):
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsDragging = toolEventHandler.dragging()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"
		shouldDisplay = (Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.alwaysCrosshair"] and not toolIsTextTool) or toolIsDragging

		if Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.showThickness"] and shouldDisplay:
			font = Glyphs.font
			master = layer.associatedFontMaster()
			scale = self.getScale()
			mousePosition = self.mousePosition()

			# intersection markers:
			handleSize = self.getHandleSize() * scale**-0.7
			try:
				NSColor.separatorColor().set()
			except:
				NSColor.systemGrayColor().set()  # pre 10.14

			# stem thickness horizontal slice
			sliceY = mousePosition.y
			minX = -1000 * (font.upm / 1000.0)
			maxX = layer.width + 1000 * (font.upm / 1000.0)
			prev = minX
			xs = {}
			intersections = layer.calculateIntersectionsStartPoint_endPoint_decompose_(
				(minX, sliceY),
				(maxX, sliceY),
				True,
			)
			for inter in intersections[1:-1]:
				self.drawCircle(inter, handleSize)
				if prev != minX:
					xs[(inter.x - prev) / 2 + prev] = inter.x - prev
				prev = inter.x

			# stem thickness vertical slice
			sliceX = mousePosition.x
			minY = master.descender - 1000 * (font.upm / 1000.0)
			maxY = master.ascender + 1000 * (font.upm / 1000.0)
			prev = minY
			ys = {}

			italicAngle = master.italicAngle

			verticalIntersections = layer.calculateIntersectionsStartPoint_endPoint_decompose_(
				self.italicize(NSPoint(sliceX, minY), italicAngle=italicAngle, pivotalY=sliceY),
				self.italicize(NSPoint(sliceX, maxY), italicAngle=italicAngle, pivotalY=sliceY),
				True,
			)
			for inter in verticalIntersections[1:-1]:
				self.drawCircle(inter, handleSize)
				if prev != minY:
					ys[(inter.y - prev) / 2 + prev] = inter.y - prev
				prev = inter.y

			# set font attributes
			fontSize = Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"]
			thicknessFontAttributes = {
				NSFontAttributeName: NSFont.monospacedDigitSystemFontOfSize_weight_(fontSize / scale, 0.0),
				NSForegroundColorAttributeName: NSColor.textColor()
			}

			# dragging width and height
			if font.tool == 'SelectTool' and toolIsDragging:
				origin = self.dragStart
				width = round(mousePosition.x - origin.x)
				height = round(mousePosition.y - origin.y)

				widthText = NSAttributedString.alloc().initWithString_attributes_(
					"%s × %s" % (str(abs(width)), str(abs(height))),
					thicknessFontAttributes
				)

				textAlignment = 2  # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
				sizePos = (max(origin.x, mousePosition.x) - 4 / scale, min(origin.y, mousePosition.y) - fontSize - 4)
				widthText.drawAtPoint_alignment_(sizePos, textAlignment)

			# number badges on vertical slice:
			for key in ys:
				item = ys[key]
				item = round(item, 1)
				if item != 0:
					x, y = sliceX, key
					# adjust x for italic angle if necessary:
					if italicAngle:
						x = self.italicize(NSPoint(x, y), italicAngle=italicAngle, pivotalY=sliceY).x
					self.drawThicknessBadge(scale, fontSize, x, y, item)
					self.drawThicknessText(scale, thicknessFontAttributes, x, y, item)

			# number badges on horizontal slice:
			for key in xs:
				item = xs[key]
				item = round(item, 1)
				if item != 0:
					x, y = key, sliceY
					self.drawThicknessBadge(scale, fontSize, x, y, item)
					self.drawThicknessText(scale, thicknessFontAttributes, x, y, item)

	@objc.python_method
	def italicize(self, thisPoint, italicAngle=0.0, pivotalY=0.0):
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
			yOffset = thisPoint.y - pivotalY  # calculate vertical offset
			italicAngle = radians(italicAngle)  # convert to radians
			tangens = tan(italicAngle)  # math.tan needs radians
			horizontalDeviance = tangens * yOffset  # vertical distance from pivotal point
			x += horizontalDeviance  # x of point that is yOffset from pivotal point
			return NSPoint(x, thisPoint.y)

	@objc.python_method
	def background(self, layer):
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsDragging = toolEventHandler.dragging()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"
		crossHairCenter = self.mousePosition()
		shouldDisplay = (Glyphs.boolDefaults["com.mekkablue.ShowCrosshair.alwaysCrosshair"] and not toolIsTextTool) or toolIsDragging

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
			crosshairColor = NSColor.disabledControlTextColor()  # subtle grey
			crosshairColor = crosshairColor.colorWithAlphaComponent_(0.25)
			crosshairColor.set()
			crosshairPath = NSBezierPath.bezierPath()
			crosshairPath.setLineWidth_(0.75 / self.getScale())

			# vertical line:
			crosshairPath.moveToPoint_(self.italicize(NSPoint(crossHairCenter.x, -offset), italicAngle=italicAngle, pivotalY=crossHairCenter.y))
			crosshairPath.lineToPoint_(self.italicize(NSPoint(crossHairCenter.x, +offset), italicAngle=italicAngle, pivotalY=crossHairCenter.y))

			# horizontal line:
			crosshairPath.moveToPoint_(NSPoint(-offset, crossHairCenter.y))
			crosshairPath.lineToPoint_(NSPoint(+offset, crossHairCenter.y))

			# execute stroke:
			crosshairPath.stroke()

	def mousePosition(self):
		if not self.controller:
			return NSZeroPoint
		view = self.controller.graphicView()
		mousePosition = view.getActiveLocation_(Glyphs.currentEvent())
		return mousePosition

	@objc.python_method
	def foregroundInViewCoords(self, layer=None):
		if not self.controller:
			return
		toolEventHandler = self.controller.view().window().windowController().toolEventHandler()
		toolIsTextTool = toolEventHandler.className() == "GlyphsToolText"

		# display at bottom left or top left
		coordinatesOption = Glyphs.defaults["com.mekkablue.ShowCrosshair.showCoordinates"]
		if not toolIsTextTool:

			fontSize = Glyphs.defaults["com.mekkablue.ShowCrosshair.fontSize"]
			fontAttributes = {
				# NSFontAttributeName: NSFont.labelFontOfSize_(10.0),
				NSFontAttributeName: NSFont.monospacedDigitSystemFontOfSize_weight_(fontSize, 0.0),
				NSForegroundColorAttributeName: NSColor.textColor()
			}

			mousePosition = self.mousePosition()
			coordinatesText = "%4d, %4d" % (round(mousePosition.x), round(mousePosition.y))
			displayText = NSAttributedString.alloc().initWithString_attributes_(
				coordinatesText,
				fontAttributes
			)
			origin = self.controller.viewPort.origin

			if coordinatesOption == 0:  # show at bottom left
				textAlignment = 0  # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
			#font = layer.parent.parent
				displayLocation = origin.x + 10, origin.y + 10
				displayText.drawAtPoint_alignment_(displayLocation, textAlignment)

			elif coordinatesOption == 1:  # show at top left
				displayLocation = origin.x + 10, origin.y + self.controller.viewPort.size.height - fontSize
				textAlignment = 6
				displayText.drawAtPoint_alignment_(displayLocation, textAlignment)

			else:
				event = Glyphs.currentEvent()
				if not event:
					return
				mousePosInWindow = event.locationInWindow()
				absMousePosition = NSPoint(origin.x + mousePosInWindow.x, origin.y + mousePosInWindow.y)

				if coordinatesOption == 2:  # show along axis
					mouseXText = NSAttributedString.alloc().initWithString_attributes_(
						str(round(mousePosition.x)),
						fontAttributes
					)
					mouseYText = NSAttributedString.alloc().initWithString_attributes_(
						str(round(mousePosition.y)),
						fontAttributes
					)
					textAlignment = 0
					displayXLocation = absMousePosition.x + 10, origin.y + self.controller.viewPort.size.height - fontSize - 10
					mouseXText.drawAtPoint_alignment_(displayXLocation, textAlignment)
					displayYLocation = origin.x + 10, absMousePosition.y - 35 + 10  # 35 window bottom height?
					mouseYText.drawAtPoint_alignment_(displayYLocation, textAlignment)
				else:  # shor next to mouse cursor
					mousePosText = NSAttributedString.alloc().initWithString_attributes_(
						coordinatesText,
						fontAttributes
					)
					textAlignment = 0
					mousePosText.drawAtPoint_alignment_((absMousePosition.x + 10, absMousePosition.y - fontSize - 35 - 20), textAlignment)

	@objc.python_method
	def drawThicknessBadge(self, scale, fontSize, x, y, value):
		mousePosition = self.mousePosition()
		# set opacity if badge is too close to mouse cursor
		distFromCursor = hypot(mousePosition.x - x, mousePosition.y - y)
		fadeMin = 30 / scale  # distance from mouse curser under which the badge starts to fade.
		fadeMax = 20 / scale  # distance from mouse curser under which the badge disappears completely.
		if distFromCursor >= fadeMin:
			opacity = 1
		elif distFromCursor <= fadeMax:
			opacity = 0
		else:
			opacity = (distFromCursor - fadeMax) / (fadeMin - fadeMax)

		width = len(str(value)) * fontSize * 0.7 / scale
		rim = fontSize * 0.3 / scale
		badge = NSRect()
		badge.origin = NSPoint(x - width / 2, y - fontSize / 2 - rim)
		badge.size = NSSize(width, fontSize + rim * 2)
		if opacity > 0:
			if opacity == 1:
				NSColor.textBackgroundColor().set()
			else:
				textBackgroundColor = NSColor.textBackgroundColor().colorWithAlphaComponent_(opacity)
				textBackgroundColor.set()
			NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(badge, fontSize * 0.5, fontSize * 0.5).fill()

	@objc.python_method
	def drawThicknessText(self, scale, thicknessFontAttributes, x, y, item):
		mousePosition = self.mousePosition()
		# set opacity if badge is too close to mouse cursor
		distFromCursor = hypot(mousePosition.x - x, mousePosition.y - y)
		fadeMin = 30 / scale  # distance from mouse curser under which the badge starts to fade.
		fadeMax = 20 / scale  # distance from mouse curser under which the badge disappears completely.
		if distFromCursor >= fadeMin:
			opacity = 1
		elif distFromCursor <= fadeMax:
			opacity = 0
		else:
			opacity = (distFromCursor - fadeMax) / (fadeMin - fadeMax)

		if opacity > 0:
			if opacity < 1:
				newTextColor = NSColor.textColor().colorWithAlphaComponent_(opacity)
				thicknessFontAttributes[NSForegroundColorAttributeName] = newTextColor
			displayText = NSAttributedString.alloc().initWithString_attributes_(
				str(item),
				thicknessFontAttributes
			)
			displayText.drawAtPoint_alignment_((x, y), 4)

	def mouseDown_(self, notification):
		self.dragStart = self.mousePosition()

	def mouseUp_(self, notification):
		self.dragStart = None
		self.dragging = False

	def mouseDidMove_(self, notification):
		if hasattr(self, 'controller') and self.controller:
			self.controller.redraw()
		else:
			Glyphs.redraw()

	def willActivate(self):
		Glyphs.addCallback(self.mouseDidMove_, MOUSEMOVED)
		Glyphs.addCallback(self.mouseDown_, MOUSEDOWN)
		Glyphs.addCallback(self.mouseUp_, MOUSEUP)

	def willDeactivate(self):
		try:
			Glyphs.removeCallback(self.mouseDidMove_, MOUSEMOVED)
			Glyphs.removeCallback(self.mouseDown_, MOUSEDOWN)
			Glyphs.removeCallback(self.mouseUp_, MOUSEUP)
		except:
			import traceback
			NSLog(traceback.format_exc())

	def toggleUniversalCrosshair(self):
		self.toggleSetting("alwaysCrosshair")

	def toggleShowThickness(self):
		self.toggleSetting("showThickness")

	def toggleShowCoordinates0(self):  # bottom left
		self.toggleSetting("showCoordinates", 0)

	def toggleShowCoordinates1(self):  # top left
		self.toggleSetting("showCoordinates", 1)

	def toggleShowCoordinates2(self):  # along axis
		self.toggleSetting("showCoordinates", 2)

	def toggleShowCoordinates3(self):  # next to cursor
		self.toggleSetting("showCoordinates", 3)

	def toggleFontSize8(self):  # next to cursor
		self.toggleSetting("fontSize", 8)

	def toggleFontSize9(self):  # next to cursor
		self.toggleSetting("fontSize", 9)

	def toggleFontSize10(self):  # next to cursor
		self.toggleSetting("fontSize", 10)

	def toggleFontSize12(self):  # next to cursor
		self.toggleSetting("fontSize", 12)

	def toggleFontSize14(self):  # next to cursor
		self.toggleSetting("fontSize", 14)

	def toggleFontSize18(self):  # next to cursor
		self.toggleSetting("fontSize", 18)

	@objc.python_method
	def toggleSetting(self, prefName, extraParameter=None):
		if extraParameter is not None:
			Glyphs.defaults["com.mekkablue.ShowCrosshair.%s" % prefName] = extraParameter
		else:
			pref = "com.mekkablue.ShowCrosshair.%s" % prefName
			oldSetting = Glyphs.boolDefaults[pref]
			Glyphs.defaults[pref] = int(not oldSetting)
		self.generalContextMenus = self.buildContextMenus()

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
