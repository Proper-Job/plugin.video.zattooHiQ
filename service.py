# coding=utf-8
#
#    copyright (C) 2017 Steffen Rolapp (github@rolapp.de)
#
#    This file is part of zattooHiQ
#
#    zattooHiQ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    zattooHiQ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with zattooHiQ.  If not, see <http://www.gnu.org/licenses/>.
#


import xbmc, xbmcgui, xbmcaddon, datetime, time
import os, urlparse
from resources.library import library
from resources.zattooDB import ZattooDB
_zattooDB_ = ZattooDB()
__addon__ = xbmcaddon.Addon()
__addondir__  = xbmc.translatePath( __addon__.getAddonInfo('profile') ) 

_library_=library()
localString = __addon__.getLocalizedString
SWISS = __addon__.getSetting('swiss')
DEBUG = __addon__.getSetting('debug')

def refreshProg():
    import urllib
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(600): break
        #from resources.zattooDB import ZattooDB
        #_zattooDB_ = ZattooDB()
        #update programInfo
        startTime=datetime.datetime.now()
        endTime=datetime.datetime.now()+datetime.timedelta(minutes = 120)
        #print 'StartRefresh  ' + str(datetime.datetime.now())

        try:
            getProgNextDay()
            #print "Next Day"
            _zattooDB_.getProgInfo(False, startTime, endTime)
        except:
            #print 'ERROR on REFRESH'
            pass
        #print "REFRESH Prog  " + str(datetime.datetime.now())

def recInfo():
    import urllib
    from resources.zattooDB import ZattooDB
    _zattooDB_ = ZattooDB()

    resultData = _zattooDB_.zapi.exec_zapiCall('/zapi/playlist', None)
    if resultData is None: return
    for record in resultData['recordings']:
        _zattooDB_.getShowInfo(record['program_id'])

def start():
    import urllib

    #re-import ZattooDB to prevent "convert_timestamp" error
    from resources.zattooDB import ZattooDB
    _zattooDB_ = ZattooDB()
    _zattooDB_.cleanProg(True)
    
    #re-import ZattooDB to prevent "convert_timestamp" error
    from resources.zattooDB import ZattooDB
    _zattooDB_ = ZattooDB()
    _zattooDB_.updateChannels()
    
    #re-import ZattooDB to prevent "convert_timestamp" error
    from resources.zattooDB import ZattooDB
    _zattooDB_ = ZattooDB()
    _zattooDB_.updateProgram()

    startTime=datetime.datetime.now()#-datetime.timedelta(minutes = 60)
    endTime=datetime.datetime.now()+datetime.timedelta(minutes = 20)
    
    #re-import ZattooDB to prevent "convert_timestamp" error
    from resources.zattooDB import ZattooDB
    _zattooDB_ = ZattooDB()
    #xbmcgui.Dialog().notification(localString(31916), localString(30110),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False)
    _zattooDB_.getProgInfo(True, startTime, endTime)

    if SWISS == 'true':
        #xbmcgui.Dialog().notification(localString(31106), localString(31915),  __addon__.getAddonInfo('path') + '/icon.png', 3000, False)
        #xbmc.executebuiltin("ActivateWindow(busydialog)")
        recInfo()
        _library_.delete_library() # add by samoth
        _library_.make_library()
        #xbmc.executebuiltin("Dialog.Close(busydialog)")



def getProgNextDay():
    from resources.zattooDB import ZattooDB
    _zattooDB_ = ZattooDB()

    start = datetime.time(18, 0, 0)
    now = datetime.datetime.now().time()
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

    if now > start:
        #print 'NextDay ' + str(start) + ' - ' + str(now) + ' - ' + str(tomorrow)
        _zattooDB_.updateProgram(tomorrow)


# start
class myPlayer(xbmc.Player):
    
    def __init__(self, skip=0):
      self.skip=skip
      self.startTime=0
      self.playing=True
      
      
    def onPlayBackStarted(self):
      #self.loadKeymap()
      if (self.skip>0):
        self.seekTime(self.skip)
        self.startTime=self.startTime-datetime.timedelta(seconds=self.skip)
      xbmc.sleep(200)
      playingFile=xbmc.getInfoLabel('Player.Filenameandpath')
      print "playingfile: " + str(playingFile)
      if playingFile.find('dash-live')>-1 or playingFile.find('hls-live')>-1:
			self.loadKeymap()
     
      else: #start recall while playing -> unload keymap
        self.unloadKeymap()
        
    def onPlayBackSeek(self, time, seekOffset):
      if self.startTime+datetime.timedelta(milliseconds=time) > datetime.datetime.now():
        channel=_zattooDB_.get_playing()['channel']
        _zattooDB_.set_playing() #clear setplaying to start channel in watch_channel
        xbmc.executebuiltin('RunPlugin("plugin://'+__addonId__+'/?mode=watch_c&id='+channel+'&showOSD=1")')
        self.playing=False
        
    def onPlayBackStopped(self):
      self.unloadKeymap()        
      self.playing=False;
      
    def onPlayBackEnded(self): 
      self.unloadKeymap()          
      self.playing=False;
     
        
    def loadKeymap(self):
      #xbmcgui.Dialog().notification('zattooBoxExt', 'loadKeymap')
      
      source = __addondir__ + '/zattooKeymap.xml'
      dest = xbmc.translatePath('special://profile/keymaps/zattooKeymap.xml')
      if os.path.isfile(dest): return
      with open(source, 'r') as file: content = file.read()
      with open(dest, 'w') as file: file.write(content)
      xbmc.sleep(200)
      xbmc.executebuiltin('XBMC.Action(reloadkeymaps)')

    def unloadKeymap(self):
      #xbmcgui.Dialog().notification('zattooBoxExt', 'unloadKeymap')
      path=xbmc.translatePath('special://profile/keymaps/zattooKeymap.xml')
      if os.path.isfile(path):
        try:
          os.remove(path)
          xbmc.sleep(200)
          xbmc.executebuiltin('XBMC.Action(reloadkeymaps)')
        except:pass


player=myPlayer()

#xbmc.sleep(2000)
#delete zapi files to force new login    
#profilePath = xbmc.translatePath(__addon__.getAddonInfo('profile'))
#try:
    #os.remove(os.path.join(profilePath, 'cookie.cache'))
    #os.remove(os.path.join(profilePath, 'session.cache'))
    #os.remove(os.path.join(profilePath, 'account.cache'))
#except:
    #pass


if __addon__.getSetting('dbonstart') == 'true':
	start()

refreshProg()


