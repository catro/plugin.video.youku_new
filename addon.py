# -*- coding: utf-8 -*-
# default.py
import urllib,urllib2,re,xbmcplugin,xbmcgui,subprocess,sys,os,os.path
import json,time,hashlib,gzip,StringIO
from xbmcswift2 import Plugin,xbmcaddon,ListItem
from collections_backport import OrderedDict
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    from ChineseKeyboard import Keyboard
except:
    from xbmc import Keyboard  
    pass
# Plugin constants 
__addonid__ = "plugin.video.youku_new"
__addon__ = xbmcaddon.Addon(id=__addonid__)
__cwd__ = __addon__.getAddonInfo('path')
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
THEME = 'Default'
sys.path.append (__resource__)
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448 )
ACTION_MOVE_LEFT      = 1
ACTION_MOVE_RIGHT     = 2
ACTION_MOVE_UP        = 3
ACTION_MOVE_DOWN      = 4
ACTION_PAGE_UP        = 5
ACTION_PAGE_DOWN      = 6
ACTION_SELECT_ITEM    = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR_OLD = 9
ACTION_PARENT_DIR     = 92
ACTION_PREVIOUS_MENU  = 10
ACTION_SHOW_INFO      = 11
ACTION_PAUSE          = 12
ACTION_STOP           = 13
ACTION_NEXT_ITEM      = 14
ACTION_PREV_ITEM      = 15
ACTION_SHOW_GUI       = 18
ACTION_PLAYER_PLAY    = 79
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_CONTEXT_MENU   = 117

plugin = Plugin()
root_url = 'http://www.youku.com/v_showlist/c0.html'

epcache = plugin.get_storage('epcache', TTL=1440)
class WindowState:
    def __init__(self):
        self.items = None
        self.listIndex = 0
        self.settings = {}

class BaseWindow(xbmcgui.WindowXML):
    def __init__( self, *args, **kwargs):
        self.oldWindow = None
        xbmcgui.WindowXML.__init__( self )
        
    def doClose(self):
        self.session.window = self.oldWindow
        self.close()
        
    def onInit(self):
        self.setSessionWindow()
        
    def onFocus( self, controlId ):
        self.controlId = controlId
        
    def setSessionWindow(self):
        try:
            self.oldWindow = self.session.window
        except:
            self.oldWindow=self
        self.session.window = self
        
    def onAction(self,action):
        if action.getId() == ACTION_PARENT_DIR or action.getId() == ACTION_PREVIOUS_MENU:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
            self.doClose()
        else:
            return False
            

class infoWindows(BaseWindow):
    def __init__( self, *args, **kwargs ):
        """Init main Application"""
        self.session = kwargs.get('session')
        self.pageData = kwargs.get('sdata')
        self.siteid=0
        self.upd=True
        BaseWindow.__init__( self, *args, **kwargs )

    def onInit( self ):
        if self.session:
            self.session.window = self
        else:
            try:
                self.session = VstSession(self)
            except:
                print 'Unhandled Error'
                self.close()
        if self.upd:
            self.updates()

    def updates(self):
        data = GetHttpData(self.pageData['url'])
    
        try:
            name = re.search(r'class="name".*?>(.*?)</span>', data, re.S).group(1)
            self.getControl(99).setLabel('[COLOR=blue] - [/COLOR]优酷[COLOR=blue] - [/COLOR]'+name)
            self.getControl( 750 ).setLabel(name)
        except:
            pass
        try:
            cover = re.search(r'class="thumb"><img src.*?\'(.*?)\'.*?alt', data, re.S).group(1)
            self.getControl( 749 ).setImage(cover)
        except:
            pass
        try:
            desp = re.search(r'class="detail"(.*?)</div>', data, re.S).group(1)
            desp = re.search(r'.*style.*?>\s*(.*?)\s*</span>', desp, re.S).group(1)
            self.getControl( 756 ).setLabel(desp)
        except:
            pass
        try:
            actors = re.search(r'class="actor">(.*?)</span>', data, re.S).group(1)
            actors = re.compile(r'<a.*?">(.*?)</a>').findall(actors)
            self.getControl( 755 ).setLabel('/'.join(actors))
        except:
            pass
        try:
            directors = re.search(r'class="director">(.*?)</span>', data, re.S).group(1)
            directors = re.compile(r'<a.*?">(.*?)</a>').findall(directors)
            self.getControl( 754 ).setLabel('/'.join(directors))
        except:
            pass
        try:
            types = re.search(r'showInfo_wrap.*?class="type">(.*?)</span>', data, re.S).group(1)
            types = re.compile(r'<a.*?">(.*?)</a>').findall(types)
            self.getControl( 751 ).setLabel('/'.join(types))
        except:
            pass
        try:
            areas = re.search(r'class="area">(.*?)</span>', data, re.S).group(1)
            areas = re.compile(r'<a.*?">(.*?)</a>').findall(areas)
            self.getControl( 752 ).setLabel('/'.join(areas))
        except:
            pass
        try:
            year = re.search(r'class="pub">(.*?)</span>', data, re.S).group(1)
            self.getControl( 753 ).setLabel(year)
        except:
            pass
    
        self.sites=[]
        
        if self.pageData['cat']==1:
            listitem = xbmcgui.ListItem( label="播放") 
            listitem.setProperty('name',"播放")
            self.getControl( 116 ).addItem( listitem )
        elif self.pageData['cat']in (2,4):
            for i in range(int(self.sites[0]['upinfo'])):
                listitem = xbmcgui.ListItem( label="第"+str(i+1)+"集") 
                listitem.setProperty('name',"第"+str(i+1)+"集")
                self.getControl( 116 ).addItem( listitem )
        elif self.pageData['cat']==3:
                data=GetHttpData("http://api.m.v.360.cn/android/episode/v12/?id="+self.pageData['id']+"&cat=3&from=0&count=50&site="+self.sites[self.siteid]['site']+"&method=episode.multi&refm=selffull&ss=4")
                data=json.loads(data[32:])
                self.allepisode=data['data']['data']['allepisode']
                for item in self.allepisode:
                    listitem = xbmcgui.ListItem( label="["+item['name']+"]"+item['desc']) 
                    listitem.setProperty('name',"["+item['name']+"]"+item['desc'])
                    self.getControl( 116 ).addItem( listitem )

        self.upd=False



    def onClick( self, controlId ):
        if controlId == 116:
            position = self.getControl( 116 ).getSelectedPosition()
            if self.pageData['cat']==1:
                url=self.pageData['sites'][self.siteid]['xstm']
                play(url,number=position)
            if self.pageData['cat']in (2,4):
                data=GetHttpData("http://api.m.v.360.cn/android/episode/v12/?id="+self.pageData['id']+"&cat="+str(self.pageData['cat'])+"&index="+str(position)+"&site="+self.pageData['sites'][self.siteid]['site']+"&quality=&method=episode.single&refm=selffull&ss=4")
                data=json.loads(data[32:])
                play(data['data']['data']['xstm'],number=position)
            if self.pageData['cat']==3:
                url=self.allepisode[position]['xstm']
                play(url,number=position)
        
#controlID(500): Main window
#controlID(501): Navigation window        
class mainWindows(BaseWindow):
    def __init__( self, *args, **kwargs ):
        """Init main Application"""
        self.session = None
        self.selectcat=0
        self.oldpos=0
        self.Tab=False
        self.opt={'cid':'','cat':'all','catname':'全部','year':'all','yearname':'全部','area':'all','areaname':'全部'}
        BaseWindow.__init__( self, *args, **kwargs )

    def onInit( self ):
        if self.session:
            self.session.window = self
        else:
            try:
                self.session = VstSession(self)
            except:
                print 'Unhandled Error'
                self.close()
        try:
            self.catlist
            self.menus
        except:
            self.initCategory()
            self.showCategory()
            pass
            
    def initCategory(self):
        data=GetHttpData(root_url)
        self.getControl( 501 ).reset()
        
        #add catalogs
        self.catlist = []
        catastr = re.search(r'yk-filter-panel">(.*?)yk-filter-handle', data, re.S)
        catalogs = re.findall(r'href="(.*?)".*?>(.*?)</a>', catastr.group(1))
        
        title='全部'
        url=root_url
        self.catlist.append({'title':title, 'url':url, 'nextpage': url})
        listitem = xbmcgui.ListItem(label=title)
        self.getControl( 501 ).addItem( listitem )
        for catalog in catalogs:
            title=catalog[-1].decode('utf-8')
            url='http://www.youku.com{0}'.format(catalog[0])
            self.catlist.append({'title':title, 'url':url})
            listitem = xbmcgui.ListItem( label=title)
            self.getControl( 501 ).addItem( listitem )
        self.getControl( 501 ).getListItem(0).select(True)
    
    def showCategory(self):
        
        self.menus=[]
        self.getControl( 500 ).reset()
        
        url = self.catlist[self.selectcat]['url']
        self.appendCategory(url)
        
        self.update_title(self.catlist[self.selectcat]['title'])
        
    def appendCategory(self, url):
        data=GetHttpData(url)
        
        mstr = r'{0}{1}{2}'.format('[vp]-thumb">\s+<img src="(.*?)" alt="([^>]+)"',
                                   '.*?"[pv]-thumb-tag[lr]b"><.*?">([^<]+?)',
                                   '<.*?"[pv]-link">\s+<a href="(.*?)"')
        movies = re.findall(mstr, data, re.S)
        for seq, m in enumerate(movies):
            label = '{1}【{2}】'.format(seq, m[1], m[2]).decode( 'utf-8') if m[0] else m[1].decode('utf-8')
            url = m[3]
            thumbnail = m[0]
            self.menus.append({
                'label': label,
                'url': url,
                'thumbnail': thumbnail,
            })
            listitem = xbmcgui.ListItem( label=label,thumbnailImage=thumbnail)
            self.getControl( 500 ).addItem( listitem )
        
        nextpage = re.search(r'class="next".*?href="(.*?)"', data, re.S).group(1)
        self.catlist[self.selectcat]['nextpage'] = 'http://www.youku.com' + nextpage
    
    
    def onClick( self, controlId ):
        if controlId == 500:
            position = self.getControl( 500 ).getSelectedPosition()
            url = self.menus[position]['url']
            if 'show_page' in url:
                openWindow( "info" ,session=self ,sdata=self.menus[position])
            else:
                play(url)

        if controlId == 501:
            position = self.getControl( 501 ).getSelectedPosition()
            self.getControl( 501 ).getListItem(self.selectcat).select(False)
            self.getControl( 501 ).getSelectedItem().select(True)
            self.selectcat = position
            self.showCategory()
            

    def onFocus( self, controlId ):
        if controlId==501:
            self.getControl( 499 ).setPosition(0,0)
            if     self.getControl( 501 ).getSelectedPosition() >=2:
                self.Tab=True
                self.getControl(498).setPosition(150,0)

        elif controlId==500:
            self.getControl( 499 ).setPosition(-130,0)
            self.getControl(498).setPosition(-150,0)

    def onAction(self,action):
        if action.getId() ==2 and self.getFocusId()== 501:
            self.setFocusId(500)
        elif action.getId()==4 and self.getFocusId()== 500:
            posid=self.getControl( 500 ).getSelectedPosition()
            tot=self.getControl( 500 ).size()
            self.oldpos=self.getControl( 500 ).getSelectedPosition()
            if tot-posid<=10:
                self.oldpos=self.getControl( 500 ).getSelectedPosition()
                self.appendCategory(self.catlist[self.selectcat]['nextpage'])
                self.getControl(500).selectItem(self.oldpos)
        if action.getId() == ACTION_PARENT_DIR or action.getId() == ACTION_PREVIOUS_MENU:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('优酷', '确定要退出吗?')
            if ret:
                if xbmc.Player().isPlaying():
                    xbmc.Player().stop()
                self.doClose()
                return True
            else:
                return False


    def update_title(self,name):
        self.getControl(99).setLabel('[COLOR=blue] - [/COLOR]优酷[COLOR=blue] - [/COLOR]'+name)

        
def openWindow(window_name,session=None,**kwargs):
        windowFile = '%s.xml' % window_name
        if window_name == 'main':
            windowFile = 'main.xml'
            windowFilePath = os.path.join(xbmc.translatePath(__addon__.getAddonInfo('path')),'resources','skins',"Default",'720p',windowFile)
            w = mainWindows(windowFile , xbmc.translatePath(__addon__.getAddonInfo('path')), "Default",**kwargs)
        elif window_name == 'info':
            w = infoWindows(windowFile , xbmc.translatePath(__addon__.getAddonInfo('path')), "Default",session=session,**kwargs)
        else:
            return #Won't happen :)
        w.doModal()            
        del w
        

def GetHttpData(url):
    xbmc.executebuiltin("ShowBusyDialog")
    if url in epcache:
        plugin.log.error("From Cache:"+url)
        return epcache[url]
    else:
        plugin.log.error("Update:"+url)
    req = urllib2.Request(url)
    req.add_header('User-Agent', "360 Video App/2.6.1 Android/4.1.1 QIHU")
    #req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) {0}{1}'.
    #               format('AppleWebKit/537.36 (KHTML, like Gecko) ',
    #                      'Chrome/28.0.1500.71 Safari/537.36'))
    #req.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(req)
    httpdata = response.read()
    if response.headers.get('content-encoding', None) == 'gzip':
        httpdata = gzip.GzipFile(fileobj=StringIO.StringIO(httpdata)).read()
    response.close()
    match = re.compile('encodingt=(.+?)"').findall(httpdata)
    if len(match)<=0:
        match = re.compile('meta charset="(.+?)"').findall(httpdata)
    if len(match)>0:
        charset = match[0].lower()
        if (charset != 'utf-8') and (charset != 'utf8'):
            httpdata = unicode(httpdata, charset).encode('utf8')
    epcache[url] = httpdata
    xbmc.executebuiltin('HideBusyDialog')
    return httpdata


def play(url):
    flvcdurl='http://www.flvcd.com/parse.php?format=super&kw='+urllib.quote_plus(url)
    result = GetHttpData(flvcdurl)
    foobars = re.compile('(http://k.youku.com/.*)"\starget', re.M).findall(result)
    if len(foobars)<=0:
        return
    playlist = xbmc.PlayList(1)
    playlist.clear()
    for i in range(0,len(foobars)):
        title =" 第"+str(i+1)+"/"+str(len(foobars))+"节"
        listitem=xbmcgui.ListItem(title)
        listitem.setInfo(type="Video",infoLabels={"Title":title})
        playlist.add(foobars[i], listitem)
    xbmc.Player().play(playlist)


class VstSession:
    def __init__(self,window=None):
        self.window = window
        
    def removeCRLF(self,text):
        return " ".join(text.split())
        
    def makeAscii(self,name):
        return name.encode('ascii','replace')
    
    
        
    def closeWindow(self):
        self.window.doClose()
            
    def clearSetting(self,key):
        __addon__.setSetting(key,'')
        
    def setSetting(self,key,value):
        __addon__.setSetting(key,value and ENCODE(value) or '')
        
    def getSetting(self,key,default=None):
        setting = __addon__.getSetting(key)
        if not setting: return default
        if type(default) == type(0):
            return int(float(setting))
        elif isinstance(default,bool):
            return setting == 'true'
        return setting
        

if __name__ == '__main__':
    openWindow('main')