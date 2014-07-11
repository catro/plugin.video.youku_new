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
dyCat={"data":[{"param":"cat","name":"类型","options":[{"name":"全部","value":"all"},{"name":"喜剧","value":"103"},{"name":"爱情","value":"100"},{"name":"动作","value":"106"},{"name":"恐怖","value":"102"},{"name":"科幻","value":"104"},{"name":"剧情","value":"112"},{"name":"犯罪","value":"105"},{"name":"奇幻","value":"113"},{"name":"战争","value":"108"},{"name":"悬疑","value":"115"},{"name":"动画","value":"107"},{"name":"文艺","value":"117"},{"name":"伦理","value":"101"},{"name":"纪录","value":"118"},{"name":"传记","value":"119"},{"name":"歌舞","value":"120"},{"name":"古装","value":"121"},{"name":"历史","value":"122"},{"name":"惊悚","value":"123"},{"name":"其他","value":"other"}]},{"param":"area","name":"地区","options":[{"name":"全部","value":"all"},{"name":"美国","value":"11"},{"name":"大陆","value":"10"},{"name":"香港","value":"15"},{"name":"韩国","value":"13"},{"name":"日本","value":"14"},{"name":"法国","value":"12"},{"name":"英国","value":"16"},{"name":"德国","value":"17"},{"name":"台湾","value":"18"},{"name":"泰国","value":"21"},{"name":"印度","value":"22"},{"name":"其他","value":"other"}]},{"param":"year","name":"年代","options":[{"name":"全部","value":"all"},{"name":"2014","value":"2014"},{"name":"2013","value":"2013"},{"name":"2012","value":"2012"},{"name":"2011","value":"2011"},{"name":"2010","value":"2010"},{"name":"2009","value":"2009"},{"name":"2008","value":"2008"},{"name":"2007","value":"2007"},{"name":"2006","value":"2006"},{"name":"更早","value":"other"}]}]}
dsjCat={"data":[{"param":"cat","name":"类型","options":[{"name":"全部","value":"all"},{"name":"言情","value":"101"},{"name":"伦理","value":"105"},{"name":"喜剧","value":"109"},{"name":"悬疑","value":"108"},{"name":"都市","value":"111"},{"name":"偶像","value":"100"},{"name":"古装","value":"104"},{"name":"军事","value":"107"},{"name":"警匪","value":"103"},{"name":"历史","value":"112"},{"name":"武侠","value":"106"},{"name":"科幻","value":"113"},{"name":"宫廷","value":"102"},{"name":"情景","value":"114"},{"name":"动作","value":"115"},{"name":"励志","value":"116"},{"name":"神话","value":"117"},{"name":"谍战","value":"118"},{"name":"粤语","value":"110"},{"name":"其他","value":"other"}]},{"param":"area","name":"地区","options":[{"name":"全部","value":"all"},{"name":"内地","value":"10"},{"name":"香港","value":"11"},{"name":"台湾","value":"16"},{"name":"韩国","value":"12"},{"name":"泰国","value":"14"},{"name":"日本","value":"15"},{"name":"美国","value":"13"},{"name":"英国","value":"17"},{"name":"新加坡","value":"18"}]},{"param":"year","name":"年代","options":[{"name":"全部","value":"all"},{"name":"2014","value":"2014"},{"name":"2013","value":"2013"},{"name":"2012","value":"2012"},{"name":"2011","value":"2011"},{"name":"2010","value":"2010"},{"name":"2009","value":"2009"},{"name":"2008","value":"2008"},{"name":"2007","value":"2007"},{"name":"2006","value":"2006"},{"name":"更早","value":"other"}]}]}
dmCat={"data":[{"param":"cat","name":"类型","options":[{"name":"全部","value":"all"},{"name":"热血","value":"100"},{"name":"恋爱","value":"101"},{"name":"运动","value":"103"},{"name":"美少女","value":"102"},{"name":"校园","value":"104"},{"name":"搞笑","value":"105"},{"name":"幻想","value":"106"},{"name":"冒险","value":"107"},{"name":"男性向","value":"124"},{"name":"悬疑","value":"108"},{"name":"魔幻","value":"109"},{"name":"动物","value":"110"},{"name":"少儿","value":"111"},{"name":"女性向","value":"125"},{"name":"机战","value":"112"},{"name":"怪物","value":"113"},{"name":"益智","value":"114"},{"name":"战争","value":"115"},{"name":"社会","value":"116"},{"name":"友情","value":"117"},{"name":"成人","value":"118"},{"name":"竞技","value":"119"},{"name":"耽美","value":"120"},{"name":"童话","value":"121"},{"name":"LOLI","value":"122"},{"name":"青春","value":"123"},{"name":"动作","value":"126"}]},{"param":"area","name":"地区","options":[{"name":"全部","value":"all"},{"name":"日本","value":"11"},{"name":"美国","value":"12"},{"name":"大陆","value":"10"}]}]}

plugin = Plugin()

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
        self.pageData = kwargs.get('sdata')['data']['data']
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
        self.getControl(99).setLabel('[COLOR=blue] - [/COLOR]优酷[COLOR=blue] - [/COLOR]'+self.pageData['title'].encode('UTF-8'))
        self.getControl( 749 ).setImage(self.pageData['cover'])
        self.getControl( 750 ).setLabel(self.pageData['title'])
        self.getControl( 756 ).setLabel(self.pageData['word'])
        self.getControl( 755 ).setLabel('/'.join(self.pageData['actor']).encode('UTF-8'))
        self.getControl( 754 ).setLabel('/'.join(self.pageData['director']).encode('UTF-8'))
        self.getControl( 751 ).setLabel('/'.join(self.pageData['type']).encode('UTF-8'))
        self.getControl( 752 ).setLabel('/'.join(self.pageData['area']).encode('UTF-8'))
        self.getControl( 753 ).setLabel(str(self.pageData['year']))
        self.sites=[]
        for item in self.pageData['sites']:
                self.sites.append({
                        'name':item['name'],
                        'site':item['site'],
                        'upinfo':item['upinfo']
                        })
        for x in self.sites:
            listitem = xbmcgui.ListItem( label=x['name']) 
            self.getControl( 115 ).addItem( listitem )
        self.getControl( 115 ).getListItem(self.siteid).select(True)
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
    def updateUrl(self):
        self.getControl( 116 ).reset()
        data=GetHttpData("http://api.m.v.360.cn/android/episode/v12/?id="+self.pageData['id']+"&cat=3&from=0&count=50&site="+self.sites[self.siteid]['site']+"&method=episode.multi&refm=selffull&ss=4")
        data=json.loads(data[32:])
        self.allepisode=data['data']['data']['allepisode']
        for item in self.allepisode:
            listitem = xbmcgui.ListItem( label="["+item['name']+"]"+item['desc']) 
            listitem.setProperty('name',"["+item['name']+"]"+item['desc'])
            self.getControl( 116 ).addItem( listitem )



    def onClick( self, controlId ):
        if controlId == 115:
            position = self.getControl( 115 ).getSelectedPosition()
            self.getControl( 115 ).getListItem(self.siteid).select(False)
            self.getControl( 115 ).getSelectedItem().select(True)
            self.siteid=position
            if self.pageData['cat']==3:
                self.updateUrl()
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
            self.menus
        except:
            self.updateIndex()
            
    def updateIndex(self):
        data=GetHttpData('http://www.youku.com/v/')
        
        self.menus=[]
        self.getControl( 500 ).reset()
        self.getControl( 501 ).reset()
        
        #get movie list
        maptuple = (('olist', 'showmovie'), ('showlist', 'showmovie'),
                ('show_page', 'showepisode'), ('v_show/', 'playmovie'))
        mstr = r'{0}{1}{2}'.format('[vp]-thumb">\s+<img src="(.*?)" alt="([^>]+)"',
                                   '.*?"[pv]-thumb-tag[lr]b"><.*?">([^<]+?)',
                                   '<.*?"[pv]-link">\s+<a href="(.*?)"')
        movies = re.findall(mstr, data, re.S)
        for seq, m in enumerate(movies):
            routeaddr = filter(lambda x: x[0] in m[3], maptuple)
            label = '{1}【{2}】'.format(seq, m[1], m[2]).decode( 'utf-8') if m[0] else m[1].decode('utf-8')
            path = m[3]
            thumbnail = m[0]
            self.menus.append({
                'label': label,
                'path': path,
                'thumbnail': thumbnail,
            })
            listitem = xbmcgui.ListItem( label=label,label2='index',thumbnailImage=thumbnail)
            self.getControl( 500 ).addItem( listitem )
        
        #add catalogs
        self.catlist = []
        catastr = re.search(r'yk-filter-panel">(.*?)yk-filter-handle',
                            data, re.S)
        catalogs = re.findall(r'href="(.*?)".*?>(.*?)</a>', catastr.group(1))
        
        title='全部'
        url='http://www.youku.com/v/'
        self.catlist.append({'title':title, 'url':url})
        listitem = xbmcgui.ListItem( label=title,label2='Channel')
        self.getControl( 501 ).addItem( listitem )
        for catalog in catalogs:
            title=catalog[-1].decode('utf-8')
            url='http://www.youku.com{0}'.format(catalog[0])
            self.catlist.append({'title':title, 'url':url})
            listitem = xbmcgui.ListItem( label=title,label2='Channel')
            self.getControl( 501 ).addItem( listitem )
        self.getControl( 501 ).getListItem(0).select(True)
        
        self.update_title('首页')

    def updateChannel(self,cid,page=1):
        data=GetHttpData("http://api.m.v.360.cn/android/list/v12/?p={0}&c={1}&area={2}&cat={3}&year={4}&method=list.datas&refm=selffull&ss=4".format(str(page),str(cid),str(self.opt['area']),str(self.opt['cat']),str(self.opt['year'])))
        data=json.loads(data[32:])
        if page==1:
            self.getControl( 500 ).reset()
            self.menus=[]
        else:
            self.oldpos=self.getControl( 500 ).getSelectedPosition()
        for item in data['data']['data']['data']:
            self.menus.append({
                'label': '%s' % ( item['title'].encode('UTF-8')),
                'id':  item.has_key('id') and item['id'] or '',
                'cat': item.has_key('id') and item['cat'] or '',
                'url': item.has_key('xstm') and item['xstm'] or '',
                'thumbnail': item['cover'],})
            listitem = xbmcgui.ListItem( label=item['title'].encode('UTF-8'),label2='Channel',thumbnailImage=item['cover'])
            self.getControl( 500 ).addItem( listitem )
        if page!=1:
            self.getControl(500).selectItem(self.oldpos)
    def updateSubChannel(self,cat,tid,page=0):
        data=GetHttpData("http://api.m.v.360.cn/android/channel/v12/?cid={0}&tid={1}&start={2}&count=20&method=channel.datas&refm=selffull&ss=4".format(str(cat),str(tid),str(page)))
        data=json.loads(data[32:])
        if page==0:
            self.getControl( 500 ).reset()
            self.menus=[]
        else:
            self.oldpos=self.getControl( 500 ).getSelectedPosition()
        for item in data['data']['data']['datas']:
            self.menus.append({
                'label': '%s' % ( item['title'].encode('UTF-8')),
                'id':  item.has_key('id') and item['id'] or '',
                'cat': item.has_key('id') and item['cat'] or '',
                'url': item.has_key('xstm') and item['xstm'] or '',
                'thumbnail': item['cover'],})
            listitem = xbmcgui.ListItem( label=item['title'].encode('UTF-8'),label2='subChannel',thumbnailImage=item['cover'])
            self.getControl( 500 ).addItem( listitem )
        if page!=0:
            self.getControl(500).selectItem(self.oldpos)
    def updateTab(self,cat,filters=0):
        if cat=="ranking":
            self.getControl( 502 ).reset()
            self.Tabmenus=[]
            self.Tabmenus.append({'label': '电影','tid':  1,'cat': cat,})
            self.Tabmenus.append({'label': '电视剧','tid':  2,'cat': cat,})
            self.Tabmenus.append({'label': '综艺','tid':  3,'cat': cat,})
            self.Tabmenus.append({'label': '动漫','tid':  4,'cat': cat,})
            for item in self.Tabmenus:
                listitem = xbmcgui.ListItem( label=item['label'],label2='Tab')
                self.getControl( 502 ).addItem( listitem )
        else:
            data=GetHttpData("http://api.m.v.360.cn/android/channel/v12/?cid={0}&method=channel.tabs&refm=selffull&ss=4".format(str(cat)))
            data=json.loads(data[32:])
            self.getControl( 502 ).reset()
            self.Tabmenus=[]
            if int(filters)>0:
                plugin.log.error(filters)
                self.Tabmenus.append({'label': '筛选','tid': -1,'cat': cat,})
            for item in data['data']['data']:
                self.Tabmenus.append({'label': '%s' % ( item['title'].encode('UTF-8')),'tid':  item['tid'],'cat': cat,})
            for item in self.Tabmenus:
                listitem = xbmcgui.ListItem( label=item['label'],label2='Tab')
                self.getControl( 502 ).addItem( listitem )


    def onClick( self, controlId ):
        if controlId == 500:
            position = self.getControl( 500 ).getSelectedPosition()
            catid=self.getControl( 500).getListItem(position).getLabel2()
            if catid in "index,ranking,subChannel,Channel":
                if self.menus[position]['id']=='':
                    url=self.menus[position]['url']
                    play(url,number=0)
                else:
                    data=GetHttpData("http://api.m.v.360.cn/android/coverpage/v12/?id="+self.menus[position]['id']+"&cat="+str(self.menus[position]['cat'])+"&method=coverpage.data&refm=selffull&zhushouParams=null&ss=4&token=fe8ebfe52cb27c10ad621271fca8ac67&ver=23&ch=360ysgw")
                    data=json.loads(data[32:])
                    openWindow( "info" ,session=self,sdata=data)

        if controlId == 501:
            position = self.getControl( 501 ).getSelectedPosition()
            self.getControl( 501 ).getListItem(self.selectcat).select(False)
            self.getControl( 501 ).getSelectedItem().select(True)
            self.selectcat=position
            self.update_title(self.catlist[position]['title'])
            if self.catlist[position]['cid']=='index':
                self.updateIndex()
            else:
                pass
        if controlId == 502:
            position = self.getControl( 502 ).getSelectedPosition()
            if self.Tabmenus[position]['tid']==-1:
                if self.catlist[self.getControl( 501 ).getSelectedPosition()]['cid']=='3':
                    sel = xbmcgui.Dialog().select(dsjCat['data'][0]['name'], [i['name'] for i in dsjCat['data'][0]['options']])
                    sel1 = xbmcgui.Dialog().select(dsjCat['data'][1]['name'], [i['name'] for i in dsjCat['data'][1]['options']])
                    sel2 = xbmcgui.Dialog().select(dsjCat['data'][2]['name'], [i['name'] for i in dsjCat['data'][2]['options']])
                    self.opt['cat']=dsjCat['data'][0]['options'][sel]['value']
                    self.opt['catname']=dsjCat['data'][0]['options'][sel]['name']
                    self.opt['area']=dsjCat['data'][1]['options'][sel]['value']
                    self.opt['areaname']=dsjCat['data'][1]['options'][sel]['name']
                    self.opt['year']=dsjCat['data'][2]['options'][sel]['value']
                    self.opt['yearname']=dsjCat['data'][2]['options'][sel]['name']
                    self.opt['cid']='2'
                    self.updateChannel('2')
                elif self.catlist[self.getControl( 501 ).getSelectedPosition()]['cid']=='4':
                    sel = xbmcgui.Dialog().select(dyCat['data'][0]['name'], [i['name'] for i in dyCat['data'][0]['options']])
                    sel1 = xbmcgui.Dialog().select(dyCat['data'][1]['name'], [i['name'] for i in dyCat['data'][1]['options']])
                    sel2 = xbmcgui.Dialog().select(dyCat['data'][2]['name'], [i['name'] for i in dyCat['data'][2]['options']])
                    self.opt['cat']=dyCat['data'][0]['options'][sel]['value']
                    self.opt['catname']=dyCat['data'][0]['options'][sel]['name']
                    self.opt['area']=dyCat['data'][1]['options'][sel]['value']
                    self.opt['areaname']=dyCat['data'][1]['options'][sel]['name']
                    self.opt['year']=dyCat['data'][2]['options'][sel]['value']
                    self.opt['yearname']=dyCat['data'][2]['options'][sel]['name']
                    self.opt['cid']='1'
                    self.updateChannel('1')
                elif self.catlist[self.getControl( 501 ).getSelectedPosition()]['cid']=='6':
                    sel = xbmcgui.Dialog().select(dmCat['data'][0]['name'], [i['name'] for i in dmCat['data'][0]['options']])
                    sel1 = xbmcgui.Dialog().select(dmCat['data'][1]['name'], [i['name'] for i in dmCat['data'][1]['options']])
                    self.opt['cat']=dmCat['data'][0]['options'][sel]['value']
                    self.opt['catname']=dmCat['data'][0]['options'][sel]['name']
                    self.opt['area']=dmCat['data'][1]['options'][sel]['value']
                    self.opt['areaname']=dmCat['data'][1]['options'][sel]['name']
                    self.opt['cid']='4'
                    self.updateChannel('4')
                self.update_title(self.catlist[self.getControl( 501 ).getSelectedPosition()]['title']+'[COLOR=blue] - [/COLOR]'+self.Tabmenus[position]['label']+'[COLOR=blue] - [/COLOR]'+'类型:{0}|地区:{1}|年份:{2}'.format(self.opt['catname'],self.opt['areaname'],self.opt['yearname']))

            else:
                self.update_title(self.catlist[self.getControl( 501 ).getSelectedPosition()]['title']+'[COLOR=blue] - [/COLOR]'+self.Tabmenus[position]['label'])
                self.updateSubChannel(self.Tabmenus[position]['cat'],self.Tabmenus[position]['tid'])


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
        if action.getId()in (3,4) and self.getFocusId()== 501:
            if     self.getControl( 501 ).getSelectedPosition() >= 2:
                self.updateTab(str(self.catlist[self.getControl( 501 ).getSelectedPosition()]['cid']),self.catlist[self.getControl( 501 ).getSelectedPosition()]['filter'])
                self.Tab=True
                self.getControl(498).setPosition(150,0)
            else:
                self.Tab=False
                self.getControl(498).setPosition(-150,0)
        elif action.getId() ==2 and self.getFocusId()== 501:
            if self.Tab:
                self.setFocusId(502)
            else:
                self.setFocusId(500)
        elif action.getId()==4 and self.getFocusId()== 500:
            posid=self.getControl( 500 ).getSelectedPosition()
            label2=self.getControl( 500 ).getListItem(posid).getLabel2()
            tot=self.getControl( 500 ).size()
            self.oldpos=self.getControl( 500 ).getSelectedPosition()
            if tot-posid<=5:
                if label2=='subChannel':
                    self.updateSubChannel(self.Tabmenus[self.getControl( 502 ).getSelectedPosition()]['cat'],self.Tabmenus[self.getControl( 502 ).getSelectedPosition()]['tid'],tot)
                elif label2=='Channel':
                    self.updateChannel(self.opt['cid'],tot/20+1)
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
        
class PlayUtil(object):
    def __init__(self, url, source='youku',number=0):
        self.url = url
        self.source = source
        self.number=number
        self.dialog = xbmcgui.Dialog()
        plugin.log.error( url)

    def notsup(self):
        return 'not support'
    def imgotv(self):
        paths=urllib.unquote_plus( self.url[self.url.find("url=")+4:])
        html=GetHttpData(paths)
        codes=re.search(r'code: "(.*?)"', html).group(1)
        files=re.search(r'file: "(.*?)"', html).group(1)
        limit_rate=re.search(r'limit_rate: (.*?),', html).group(1)
        moviesurl="http://pcvcr.cdn.imgo.tv/ncrs/vod.do?fid="+str(codes)+'&limitrate='+str(int(int(limit_rate) * 1.2))+'&file='+files+'&fmt=6&pno=3&m3u8=1'
        html=GetHttpData(moviesurl)
        vcodes=re.search(r'"info": "(.*?)"', html).group(1)
        return vcodes
        
    def fengxing(self):
        stypes = OrderedDict((('1080P', 'superdvd'), ('超清', 'highdvd'),
                              ('高清', 'dvd'), ('标清', 'tv')))
        vid = re.search(r'm-(.*?)\.e', self.url).group(1)
        moviesurl="http://jsonfe.funshion.com/media/?cli=apad&ver=1.2.3.3&sid=1018&mid={0}".format(vid)
        result = GetHttpData(moviesurl)
        movinfo = json.loads(result.replace('\r\n',''))
        if movinfo['data']['pinfos'].has_key('mid'):
           streamfids = movinfo['data']['pinfos']['mpurls']
        else:
           if movinfo['data']['pinfos'].has_key('sort'):
              streamfids = movinfo['data']['pinfos']['content'][movinfo['data']['pinfos']['sort'][0]]['fsps'][self.number]['mpurls']
           else:
              streamfids = movinfo['data']['pinfos']['fsps'][self.number]['mpurls']
        if len(streamfids) > 1:
            selstypes = [k for k,v in stypes.iteritems() if v in streamfids]
            selitem = self.dialog.select('清晰度', selstypes)
            if selitem is -1: return 'cancle'
            stype = stypes[selstypes[selitem]]
        movurl = streamfids[stype]['url']
        result = json.loads(GetHttpData(movurl))
        return result['playlist'][0]['urls'][0]

    def youku(self):
        stypes = OrderedDict((('1080P', 'hd3'), ('超清', 'hd2'),('高清', 'mp4'), ('标清', 'flv')))
        #get movie metadata (json format)
        vid = re.search(r'id_(.*?)\.html', self.url).group(1)
        print vid
        moviesurl="http://v.youku.com/player/getPlayList/VideoIDS/{0}".format(
            vid)
        result = GetHttpData(moviesurl)
        movinfo = json.loads(result.replace('\r\n',''))
        movdat = movinfo['data'][0]
        streamfids = movdat['streamfileids']
        stype = 'flv'
        # user select streamtype
        if len(streamfids) > 1:
            selstypes = [k for k,v in stypes.iteritems() if v in streamfids]
            selitem = self.dialog.select('清晰度', selstypes)
            if selitem is -1: return 'cancle'
            stype = stypes[selstypes[selitem]]
        movurl = 'http://pl.youku.com/playlist/m3u8?ts='+str(time.time())+'&keyframe=0&vid='+vid+'&type='+stype
        return movurl

    def sohu(self):
        paths=urllib.unquote_plus( self.url[self.url.find("url=")+4:])
        html = GetHttpData(paths)
        vid = re.search(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?', html).group(1)
        data = json.loads(GetHttpData(
            'http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % vid))
        qtyps = [('超清', 'superVid'), ('高清', 'highVid'), ('流畅', 'norVid')]
        sel = self.dialog.select('清晰度', [q[0] for q in qtyps])
        if sel is -1: return 'cancel'
        qtyp = data['data'][qtyps[sel][1]]
        if qtyp and qtyp != vid:
            movurl = 'http://hot.vrs.sohu.com/ipad'+str(qtyp)+'.m3u8'
        else:
            movurl = 'http://hot.vrs.sohu.com/ipad'+str(vid)+'.m3u8'
        return movurl

    def iqiyi(self):
        html = GetHttpData(self.url)
        videoId = re.search(r'data-player-videoid="([^"]+)"', html).group(1)

        info_url = 'http://cache.video.qiyi.com/v/%s' % videoId
        info_xml = GetHttpData(info_url)

        from xml.dom.minidom import parseString
        doc = parseString(info_xml)
        title = doc.getElementsByTagName('title')[0].firstChild.nodeValue
        size = int(doc.getElementsByTagName('totalBytes')[0].
                   firstChild.nodeValue)
        urls = [n.firstChild.nodeValue
                for n in doc.getElementsByTagName('file')]
        assert urls[0].endswith('.f4v'), urls[0]

        for i in range(len(urls)):
            temp_url = "http://data.video.qiyi.com/%s" % urls[i].split(
                "/")[-1].split(".")[0] + ".ts"
            try:
                req = urllib2.Request(temp_url)
                urllib2.urlopen(req, timeout=30)
            except urllib2.HTTPError as e:
                key = re.search(r'key=(.*)', e.geturl()).group(1)
            assert key
            urls[i] += "?key=%s" % key
        movurl = 'stack://{0}'.format(' , '.join(urls))
        return movurl

    def pps(self):
        vid = self.url[:-5].split('_')[1]
        html = GetHttpData(
            'http://dp.ppstream.com/get_play_url_cdn.php?sid={0}{1}'.format(
                vid,'&flash_type=1'))
        movstr = re.compile(r'(http://.*?)\?hd=').search(html).group(1)
        return movstr

    def tudou(self):
        html = GetHttpData(self.url)
        vcode = re.search(r'vcode\s*[:=]\s*\'([^\']+)\'', html).group(1)
        self.url = 'http://v.youku.com/v_show/id_{0}.html'.format(vcode)
        self.youku()


    def letv(self):
        paths=urllib.unquote_plus( self.url[self.url.find("=")+1:])
        vid = paths.split('/')[-1][:-5]
        infojson = GetHttpData('http://static.app.m.letv.com/android/mod/mob/ctl/getalbumbyid/act/detail/id/{0}/pcode/010110407/version/5.1.mindex.html'.format(vid))
        infojson = json.loads(infojson)
        aid=infojson['body']['id']
        infojson = GetHttpData('http://static.app.m.letv.com/android/mod/mob/ctl/videolist/act/detail/id/{1}/vid/{0}/b/1/s/60/o/-1/m/1/pcode/010110407/version/5.1.mindex.html'.format(vid,aid))
        infojson = json.loads(infojson)
        for item in infojson['body']['videoInfo']:
            if item['id']==vid:
               mid=item['mid']
        tid=time.time()
        key='{0},{1},360_dC50f2A05C3F2d5,p3bGWLVl0Ac8zDh'.format(str(mid),str(tid))
        key=hashlib.md5(str(key)).hexdigest()
        infojson = GetHttpData('http://dynamic.app.m.letv.com/android/dynamic.php?tm={0}&playid=0&splatid=360_dC50f2A05C3F2d5&tss=no&ctl=videofileapi&mod=minfo&pcode=010110407&from=SDK360&act=index&key={1}&mmsid={2}&version=5.1'.format(str(tid),str(key),str(mid)))
        infojson = json.loads(infojson)
        #sinfo = infojson['body']['videofile']['infos']['mp4_1300']['mainUrl']
        qtyps = [('高清', 'mp4_1300'),
                 ('标清', 'mp4_1000'), ('流畅', 'mp4_350')]
        sel = self.dialog.select('清晰度', [q[0] for q in qtyps])
        if sel is -1: return 'cancel'
        sinfo = infojson['body']['videofile']['infos'][qtyps[sel][1]]['mainUrl']
        infojson = GetHttpData(sinfo)
        infojson = json.loads(infojson)
        movurl = infojson['location']
        return movurl

    def qq(self):
        html = GetHttpData(self.url)
        vid = re.compile(r'vid:"([^"]+)"').search(html).group(1)
        murl = 'http://vv.video.qq.com/'
        vinfo = GetHttpData('%sgetinfo?otype=json&vids=%s' % (murl, vid))
        infoj = json.loads(vinfo.split('=')[1][:-1])
        qtyps = OrderedDict((
            ('1080P', 'fhd'), ('超清', 'shd'), ('高清', 'hd'), ('标清', 'sd')))
        #python 2.7 syntax
        #vtyps = {v['name']:v['id'] for v in infoj['fl']['fi']}
        vtyps = dict((v['name'],v['id']) for v in infoj['fl']['fi'])
        qtypid = vtyps['sd']
        sels = [k for k,v in qtyps.iteritems() if v in vtyps]
        sel = dialog.select('清晰度', sels)
        surls = []
        urlpre = infoj['vl']['vi'][0]['ul']['ui'][-1]['url']
        if sel is -1: return 'cancel'
        qtypid = vtyps[qtyps[sels[sel]]]
        for i in range(1, int(infoj['vl']['vi'][0]['cl']['fc'])):
            fn = '%s.p%s.%s.mp4' % (vid, qtypid%10000, str(i))
            sinfo = GetHttpData(
                '{0}getkey?format={1}&filename={2}&vid={3}&otype=json'.format(
                    murl, qtypid, fn, vid))
            skey = json.loads(sinfo.split('=')[1][:-1])['key']
            surl = urllib2.urlopen(
                '%s%s?vkey=%s' % (urlpre, fn, skey), timeout=30).geturl()
            if not surl: break
            surls.append(surl)
        movurl = 'stack://{0}'.format(' , '.join(surls))
        return movurl
        #movurl = 'http://vsrc.store.qq.com/%s.flv' % vid

    def _getfileid(self, streamid, seed):
        """
        get dynamic stream file id
        Arguments:
        - `streamid`: e.g. '48*60*21*...*13*'
        - `seed`: mix str seed
        """
        source = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'\
                 '/\\:._-1234567890'
        index = 0
        mixed = []
        for i in range(len(source)):
            seed = (seed * 211 + 30031) % 65536
            index =  seed * len(source) / 65536
            mixed.append(source[index])
            source = source.replace(source[index],"")
        mixstr = ''.join(mixed)
        attr = streamid[:-1].split('*')
        res = ""
        for item in attr:
            res +=  mixstr[int(item)]
        return res

    def real_url(self, host, prot, file, new):
        url = 'http://%s/?prot=%s&file=%s&new=%s' % (host, prot, file, new)
        start, _, host, key = GetHttpData(url).split('|')[:4]
        return '%s%s?key=%s' % (start[:-1], new, key)
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
        plugin.log.error("缓存输出:"+url)
        return epcache[url]
    else:
        plugin.log.error("数据更新:"+url)
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


#def play(url, source='youku'):
#    playutil = PlayUtil(url, source)
def play(url,number=0):
    source=re.compile('movie\/(.+?)\?').findall(url)[0]
    if source=="":
        print "未知视频源"
    else:
        playutil = PlayUtil(url, source,number)
    movurl = getattr(playutil, source, playutil.notsup)()
    if not movurl:
        xbmcgui.Dialog().ok(
            '提示框', '解析地址异常，无法播放')
        return
    if 'not support' in movurl:
        xbmcgui.Dialog().ok(
            '提示框', '不支持的播放源,目前支持youku/sohu/qq/iqiyi/pps/letv/tudou')
        return
    if 'cancel' in movurl: return
    listitem=xbmcgui.ListItem()
    listitem.setInfo(type="Video", infoLabels={'Title': 'c'})
    xbmc.Player().play(movurl, listitem)


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