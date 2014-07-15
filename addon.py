# -*- coding: utf-8 -*-
# default.py
import urllib,urllib2,re,xbmcplugin,xbmcgui,subprocess,sys,os,os.path
import json,time,hashlib,gzip,StringIO,HTMLParser,httplib
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
html_parser = HTMLParser.HTMLParser()

epcache = plugin.get_storage('epcache', TTL=1440)

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
        self.updates()

    def updates(self):
        data = GetHttpData(self.pageData['url'])
    
        try:
            rating = html_parser.unescape(re.search(r'class="ratingstar".*?class="num">(.*?)</em>', data, re.S).group(1))
            self.getControl(750).setLabel(rating)
        except:
            pass
        try:
            name = html_parser.unescape(re.search(r'class="name".*?>(.*?)</span>', data, re.S).group(1))
            self.getControl(99).setLabel('[COLOR=blue] - [/COLOR]'+name)
        except:
            pass
        try:
            cover = html_parser.unescape(re.search(r'class="thumb"><img src.*?\'(.*?)\'.*?alt', data, re.S).group(1))
            self.getControl( 749 ).setImage(cover)
        except:
            pass
        try:
            desp = re.search(r'class="detail"(.*?)</div>', data, re.S).group(1)
            desp = html_parser.unescape(re.search(r'.*style.*?>\s*(.*?)\s*</span>', desp, re.S).group(1)).replace('<br />', '\r\n')
            self.getControl( 756 ).setLabel(desp)
        except:
            pass
        try:
            actors = re.search(r'class="actor">(.*?)</span>', data, re.S).group(1)
            actors = re.compile(r'<a.*?">(.*?)</a>').findall(actors)
            self.getControl( 755 ).setLabel(html_parser.unescape('/'.join(actors)))
        except:
            pass
        try:
            directors = re.search(r'class="director">(.*?)</span>', data, re.S).group(1)
            directors = re.compile(r'<a.*?">(.*?)</a>').findall(directors)
            self.getControl( 754 ).setLabel(html_parser.unescape('/'.join(directors)))
        except:
            pass
        try:
            types = re.search(r'showInfo_wrap.*?class="type">(.*?)</span>', data, re.S).group(1)
            types = re.compile(r'<a.*?">(.*?)</a>').findall(types)
            self.getControl( 751 ).setLabel(html_parser.unescape('/'.join(types)))
        except:
            pass
        try:
            areas = re.search(r'class="area">(.*?)</span>', data, re.S).group(1)
            areas = re.compile(r'<a.*?">(.*?)</a>').findall(areas)
            self.getControl( 752 ).setLabel(html_parser.unescape('/'.join(areas)))
        except:
            pass
        try:
            year = re.search(r'class="pub">(.*?)</span>', data, re.S).group(1)
            self.getControl( 753 ).setLabel(year)
        except:
            pass
            
            
        episodestr = re.search(r'id="episode_wrap">(.*?)<div id="point_wrap',
                               data, re.S)
        patt = re.compile(r'(http://v.youku.com/v_show/.*?.html)".*?>([^<]+?)</a')
        episodes = patt.findall(episodestr.group(1))

        #some catalog not episode, e.g. most movie
        if not episodes:
            playurl = re.search(r'class="btnplay" href="(.*?)"', data)
            if not playurl:
                playurl = re.search(r'btnplayposi".*?"(http:.*?)"', data)
            if not playurl:
                playurl = re.search(r'btnplaytrailer.*?(http:.*?)"', data)
            self.playlist = [{'title': '播放', 'url': playurl.group(1)}]
        else:
            elists = re.findall(r'<li data="(reload_\d+)" >', data)
            epiurlpart = self.pageData['url'].replace('page', 'episode')

            #httplib can keepalive
            conn = httplib.HTTPConnection(epiurlpart.split('/')[2])
            for elist in elists:
                epiurl = epiurlpart + '?divid={0}'.format(elist)
                conn.request('GET', '/%s' % '/'.join(epiurl.split('/')[3:]))
                data = conn.getresponse().read()
                epimore = patt.findall(data)
                episodes.extend(epimore)
            conn.close()
            
            self.playlist = [{
                'title': html_parser.unescape(episode[1].decode('utf-8')),
                'url': episode[0],
                } for episode in episodes]
                
        self.getControl( 116 ).reset()
        for item in self.playlist:
            listitem = xbmcgui.ListItem( label=item['title']) 
            self.getControl( 116 ).addItem( listitem )
            
        self.setFocusId( 116 )
        

    def onClick( self, controlId ):
        if controlId == 116:
            position = self.getControl( 116 ).getSelectedPosition()
            url = self.playlist[position]['url']
            play(url)
        
#controlID(500): Main window
#controlID(501): Navigation window        
class mainWindows(BaseWindow):
    def __init__( self, *args, **kwargs ):
        """Init main Application"""
        self.session = None
        self.selectcat=0
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
            self.setFocusId(500)
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
            if 'c_96' in url:
                url = url.replace('c_96', 'c_96_s_1_d_1_pt_1')
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
                'label': html_parser.unescape(label),
                'url': url,
                'thumbnail': thumbnail,
            })
            if url in epcache: 
                listitem = epcache[url]
            else:
                listitem = xbmcgui.ListItem( label=label,thumbnailImage=thumbnail)
                epcache[url] = listitem
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
            self.setFocusId(500)
            

    def onFocus( self, controlId ):
        if controlId==501:
            self.getControl( 499 ).setPosition(0,0)

        elif controlId==500:
            self.getControl( 499 ).setPosition(-130,0)

    def onAction(self,action):
        if action.getId() ==2 and self.getFocusId()== 501:
            self.setFocusId(500)
        elif action.getId()==4 and self.getFocusId()== 500:
            posid=self.getControl( 500 ).getSelectedPosition()
            tot=self.getControl( 500 ).size()
            oldpos=self.getControl( 500 ).getSelectedPosition()
            if tot-posid<=10:
                oldpos=self.getControl( 500 ).getSelectedPosition()
                self.appendCategory(self.catlist[self.selectcat]['nextpage'])
                self.getControl(500).selectItem(oldpos)
        if action.getId() == ACTION_PARENT_DIR or action.getId() == ACTION_PREVIOUS_MENU:
            dialog = xbmcgui.Dialog()
            #ret = dialog.yesno('优酷', '确定要退出吗?')
            #if ret:
            #    if xbmc.Player().isPlaying():
            #        xbmc.Player().stop()
            #    self.doClose()
            #    return True
            #else:
            #    return False
            self.doClose()
            return True


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
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) {0}{1}'.
                   format('AppleWebKit/537.36 (KHTML, like Gecko) ',
                          'Chrome/28.0.1500.71 Safari/537.36'))
    req.add_header('Accept-encoding', 'gzip')
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
    return httpdata


def play(url):
    try:
        stypes = ['hd2', 'mp4', 'flv']
        vid = url[-18:-5]
        moviesurl="http://v.youku.com/player/getPlayList/VideoIDS/{0}/ctype/12/ev/1".format(vid)
        result = GetHttpData(moviesurl)
        movinfo = json.loads(result.replace('\r\n',''))
        movdat = movinfo['data'][0]
        streamfids = movdat['streamfileids']
        video_id = movdat['videoid']
        stype = 'flv'

        if len(streamfids) > 1:
            selstypes = [v for v in stypes if v in streamfids]
            stype = selstypes[0]
        
        playurl = r'http://v.youku.com/player/getM3U8/vid/' + vid + r'/type/' + stype + '/video.m3u8'
        playlist = xbmc.PlayList(1)
        playlist.clear()
        title =" 第"+str(1)+"/"+str(1)+"节"
        listitem=xbmcgui.ListItem(title)
        listitem.setInfo(type="Video",infoLabels={"Title":title})
        playlist.add(playurl, listitem)
        xbmc.Player().play(playlist)
        return
        
        flvcdurl='http://www.flvcd.com/parse.php?format=super&kw='+urllib.quote_plus(url)
        result = GetHttpData(flvcdurl)
        foobars = re.compile('(http://k.youku.com/.*)"\starget', re.M).findall(result)
        if len(foobars) < 1:
            xbmcgui.Dialog().ok('提示框', '付费视频，无法播放')
            return
        playlist = xbmc.PlayList(1)
        playlist.clear()
        for i in range(0,len(foobars)):
            title =" 第"+str(i+1)+"/"+str(len(foobars))+"节"
            listitem=xbmcgui.ListItem(title)
            listitem.setInfo(type="Video",infoLabels={"Title":title})
            playlist.add(foobars[i], listitem)
        xbmc.Player().play(playlist)
    except:
        xbmcgui.Dialog().ok('提示框', '解析地址异常，无法播放')


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
