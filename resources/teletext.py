# coding=utf-8

#
#    copyright (C) 2017 Steffen Rolapp (github@rolapp.de)
#
#    based on ZattooBoxExtended by Daniel Griner (griner.ch@gmail.com) license under GPl
#
#    This file is part of ZattooBox
#
#    ZattooBox is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ZattooBox is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with ZattooBox.  If not, see <http://www.gnu.org/licenses/>.
#


import xbmc, xbmcgui, xbmcaddon, time, threading
from resources.zattooDB import ZattooDB
import os 
import urllib2


__addon__ = xbmcaddon.Addon()
_dataFolder_ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
localString = __addon__.getLocalizedString


ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10

KEY_NAV_BACK = 92
KEY_HOME = 159

ACTION_MOUSE_DOUBLE_CLICK = 103
ACTION_MOUSE_DRAG = 106
ACTION_MOUSE_END = 109
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_LONG_CLICK = 108
ACTION_MOUSE_MIDDLE_CLICK = 102
ACTION_MOUSE_MOVE = 107
ACTION_MOUSE_RIGHT_CLICK = 101
ACTION_MOUSE_START = 100
ACTION_MOUSE_WHEEL_DOWN = 105
ACTION_MOUSE_WHEEL_UP = 104

ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_GESTURE_SWIPE_RIGHT = 521
ACTION_GESTURE_SWIPE_UP = 531
ACTION_GESTURE_SWIPE_DOWN = 541


class Teletext(xbmcgui.WindowDialog):
	def __init__(self):
		super(Teletext, self).__init__()

		self.channelID = ZattooDB().get_playing()['channel']

		self.imagePath=''
		self.pageInput=''

		self.bgImage = xbmcgui.ControlImage(0,0,1280,720,'')
		self.addControl(self.bgImage)
		self.bgImage.setImage(__addon__.getAddonInfo('path') + '/resources/teletextBG.png')

		self.pageInputCtrl = xbmcgui.ControlLabel(0, 0, 265, 100, '100', font='font30', alignment=2)
		self.addControl(self.pageInputCtrl)
		self.pageInputCtrl.setVisible(False)

		self.pageImage = xbmcgui.ControlImage(260, 0, 800, 720, "")
		self.addControl(self.pageImage)
		
		self.button0 = xbmcgui.ControlButton(50, 640, 170, 40, localString(31912), font='font20', alignment=6)
		self.addControl(self.button0)
		
		self.button1 = xbmcgui.ControlButton(1090, 640, 50, 40, "<", font='font30', alignment=6)
		self.addControl(self.button1)
		
		self.button2 = xbmcgui.ControlButton(1190, 640, 50, 40, ">", font='font30', alignment=6)
		self.addControl(self.button2)

		self.currentPage=100
		self.subPage=1
		self.showPage(str(self.currentPage), str(self.subPage))

	def onAction(self, action):
		if hasattr(self, 'supPageTimer'): self.supPageTimer.cancel()
		action = action.getId()
		#print('action:'+str(action))
		if action in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU]:
			if self.imagePath: os.remove(self.imagePath)
			self.close()
			
		elif (action>57 and action<68): #numbers 0-9
			self.pageInput+=str(action-58)
			self.pageInputCtrl.setLabel(self.pageInput+('*'*(3-len(self.pageInput))))
			self.pageInputCtrl.setVisible(True)
			if len(self.pageInput)>2:
				self.currentPage = int(self.pageInput)
				self.showPage(str(self.currentPage), str(self.subPage))
				self.pageInput=''

		elif action in [ACTION_MOVE_DOWN, ACTION_GESTURE_SWIPE_DOWN]:
			self.currentPage=(int((self.currentPage-1)/100))*100
			if self.currentPage<100: self.currentPage=100
			self.showPage(str(self.currentPage), str(self.subPage))
		elif action in [ACTION_MOVE_UP, ACTION_GESTURE_SWIPE_UP]:
			self.currentPage=(int(self.currentPage/100)+1)*100
			self.showPage(str(self.currentPage), str(self.subPage))
		elif action in [ACTION_MOVE_RIGHT, ACTION_GESTURE_SWIPE_RIGHT]:
			self.currentPage +=1
			self.showPage(str(self.currentPage), str(self.subPage))
		elif action in [ACTION_MOVE_LEFT, ACTION_GESTURE_SWIPE_LEFT]:
			self.currentPage -=1
			self.showPage(str(self.currentPage), str(self.subPage))
		elif action == ACTION_PAGE_DOWN:
			self.subPage = self.subPage-1
			self.showPage(str(self.currentPage),self.subPage)
		elif action == ACTION_PAGE_UP:
			self.subPage = self.subPage+1
			self.showPage(str(self.currentPage),self.subPage)
			
	def onControl(self, control):
		if control == self.button0:
			print "Open Keypad"
			dialog = xbmcgui.Dialog()
			self.pageInput = dialog.numeric(0, 'Enter Site')
			if len(self.pageInput)>2:
				self.currentPage = int(self.pageInput)
				self.showPage(str(self.currentPage), str(self.subPage))
				self.pageInput=''
				
		elif control == self.button1:
			self.subPage = self.subPage-1
			self.showPage(str(self.currentPage),self.subPage)
				
		elif control == self.button2:
			self.subPage = self.subPage+1
			self.showPage(str(self.currentPage),self.subPage)
			
				
	def showPage(self, page, subpage=1):
		if (subpage==1):
			self.pageInputCtrl.setLabel(str(self.currentPage))
			self.pageInputCtrl.setVisible(True)
		url='https://zapi.zattoo.com/teletext/'+self.channelID+'/hd/'+page+'/'+str(subpage)+'.html'
		#url="https://zapi.zattoo.com/teletext/sf-1/hd/100/1.html"
		#print('teletext image:'+url)

		req=urllib2.Request(headers={'User-Agent':'Mozilla/5.0','Cache-Control':'max-age=0'}, url=url)
		try:
			f = urllib2.urlopen(req)
			html=f.read()
			start = html.index('base64,') + 7
			end = html.index('"', start)
			image= html[start:end]

			if self.imagePath: os.remove(self.imagePath)
			self.imagePath = os.path.join(_dataFolder_, 'teletextImage'+str(time.clock())+'.png')

			fh = open(self.imagePath, "wb")
			fh.write(image.decode('base64'))
			fh.close()

			self.pageImage.setImage(self.imagePath, useCache=False)

			self.pageInputCtrl.setLabel('')
			self.pageInputCtrl.setVisible(False)
			self.supPageTimer=threading.Timer(8, self.showPage,[page,subpage+1])
			self.supPageTimer.start()
		except:
			self.subPage = 1
			if (subpage==1):self.pageInputCtrl.setLabel('page '+page+' not found')
			elif (subpage>2):self.showPage(page,1)
			elif (subpage<1):self.showPage(page,1)
