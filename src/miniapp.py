# coding: utf8

"""
    Defination of Class
    - Element(name, contents, element)
    - Event(name, contents, element, trigger, handler)
    - Navigator(name, content, element, type, target, url, extradata, bindings)
    - Page(page_path)
    - MiniApp(miniapp_path)
"""

import os
import json
import re
from loguru import logger
import config as config
from bs4 import BeautifulSoup
from pdg_js.build_pdg import get_data_flow
from utils.utils import get_page_expr_node, get_page_method_nodes
from pdg_js.js_operators import get_node_computed_value


class UIElement:
    '''
        Definition of UIElement.

        -------
        Properties:
        - name: str =>
            Name of the UIElement, such as button
        - contents: str =>
            Contents of the UIElement
        - element: Tag
            The UIElement itself, which is stored as a Tag class(BeautifulSoup4)
    '''
    def __init__(self, name, contents, element):
        self.name = name  # UIElement type name, such as button
        self.contents = contents  # Element contents
        self.element = element  # The UI element itself (Class Tag in BeautifulSoup)


class Event(UIElement):
    '''
        Definition of Event(Extends from UIElement).

        -------
        Properties:
        - name: str =>
            Name of the UIElement, such as button
        - contents: str =>
            Contents of the UIElement
        - element: Tag
            The UIElement itself, which is stored as a Tag class(BeautifulSoup4)
        - trigger: str
            Trigger of the event, such as bindtap
        - handler: str
            The corresponding event handler in Logical Layer(js)
    '''
    def __init__(self, name, contents, element, trigger, handler):
        super().__init__(name, contents, element)
        self.trigger = trigger  # Event trigger action, such as bindtap
        self.handler = handler  # Event handler function


class Navigator(UIElement):
    '''
        Definition of Navigator(Extends from UIElement).

        -------
        Properties:
        - name: str =>
            Name of the UIElement(Here is navigator of course)
        - contents: str =>
            Contents of the UIElement
        - element: Tag
            The UIElement itself, which is stored as a Tag class(BeautifulSoup4)
        - type: str =>
            Type of navigator(navigate/redirect/switchTab/reLaunch/navigateBack)
        - target: str =>
            self(routing between pages) or appid(jumping between miniapps)
        - url: str =>
            Routing/Jumping destination page url
        - extradata: str =>
            Data transmitted by cross-pages/cross-miniapps communication
        - bindings: dict =>
            Bind success/fail/complete event
    '''
    def __init__(self, name, contents, element, type='', target='', url='', \
                 extradata='', bindsuccess='', bindfail='', bindcomplete=''):
        super().__init__(name, contents, element)
        self.type = type  # navigate/redirect/switchTab/reLaunch/navigateBack
        self.target = target  # target miniprogram(self/miniprogram appid)
        self.url = url  # target page url
        self.extradata = extradata  # extradata when navigateToMiniprogram
        self.bindings = {
            'success': bindsuccess,
            'fail': bindfail,
            'complete': bindcomplete
        }


class NavigateAPI:
    '''
        Definition of NavigateAPI.

        -------
        Properties:
        - type: str =>
            route(between pages) or jump(between miniapps)
        - name: str =>
            The name of API
        - target: str/dict =>
            page_url(if routing between pages) or {appid:path}(if jumping between miniapps)
        - extradata: str =>
            Data transmitted by cross-pages/cross-miniapps communication
        - bindings: dict =>
            Bind success/fail/complete event
    '''
    def __init__(self, type, name, target='', extradata='', \
                 bindsuccess=None, bindfail=None, bindcomplete=None):
        self.type = type  # route/jump
        '''
            route: wx.navigateTo/redirectTo/switchTab/reLaunch/navigateBack
            jump: wx.navigateToMiniprogram/navigateBackMiniprogram/exitMiniprogram
        '''
        self.name = name
        self.target = target  # target page_url/appid
        self.extradata = extradata  # extradata when jump
        self.bindings = {
            'success': bindsuccess,
            'fail': bindfail,
            'complete': bindcomplete
        }


class Page:
    '''
        Definition of Page

        -------
        Properties:
        - page_path: str =>
            Path of the miniapp page
        - miniapp: MiniApp =>
            The original miniapp to which the page belongs
        - pdg_node: Node =>
            Head node of the PDG of page.js
        - data: dict =>
            A dict of {key:value} to store local variable in the page (setData)
        - binding_event: dict =>
            Store Event(extends from UIElement) which triggers binding from Render Layer(wxml) to Logical Layer(js)
        - navigator: dict =>
            Store Navigator(extends from UIElement) or NavigateAPI to build UI State Transition Graph
    '''
    def __init__(self, page_path, miniapp):
        self.page_path = page_path
        self.miniapp = miniapp
        if os.path.exists(page_path+'.js'):
            self.pdg_node = get_data_flow(input_file=page_path+'.js', benchmarks={})
        elif os.path.exists(page_path+'.ts'):
            self.pdg_node = get_data_flow(input_file=page_path+'.ts', benchmarks={})
        else: self.pdg_node = None
        if self.pdg_node != None:
            self.page_expr_node = get_page_expr_node(self.pdg_node)
        if self.page_expr_node != None:
            self.page_method_nodes = get_page_method_nodes(self.page_expr_node)
        self.binding_event = {
            # Bubbling Event
            'bindtap': [],
            'bindlongtap': [],  # including longtap/longpress event

            # Non-bubbling Event in Specific Compenonts
            'bindgetuserinfo': [],  # <button open-type='getUserInfo' bindgetuserinfo=handler_fun>
            'bindgetphonenumber': [],  # <button open-type='getPhoneNumber' bindgetphonenumber=handler_fun>
            'bindchooseavatar': [],  # <button open-type='chooseAvatar' bindchooseavatar=handler_fun>
            'bindopensetting': [],  # <button open-type='openSetting' bindopensetting=handler_fun>
            'bindlaunchapp': [],  # <button open-type='launchApp' bindlaunchapp=handler_fun>

            'bindsubmit': []  # <form binsubmit=handler_fun>
        }
        self.navigator = {
            'UIElement': [],  # Navigator element trigger, such as <navigator url="/page/index/index">切换 Tab</navigator>
            'NavigateAPI': []  # API Trigger, such as wx.navigateTo()
        }

        self.init_page_data(page_path)
        self.set_binding_event(page_path)
        self.set_navigator(page_path)

    def init_page_data(self, page_path):
        pass

    def set_binding_event(self, page_path):
        try:
            soup = BeautifulSoup(open(page_path+'.wxml'), 'html.parser')
        except Exception as e:
            logger.error('WxmlNotFoundError: {}'.format(e))
        for binding in self.binding_event.keys():
            self.binding_event_handler(soup=soup, binding=binding)

    def binding_event_handler(self, soup, binding):
        # tags = soup.find_all(binding=True)  # binding是字符串, 不能直接作为tag属性名查找 
        tags = self.find_tags_by_attr(soup, attr=binding)
        for tag in tags:
            self.binding_event[binding].append(Event(name=tag.name, trigger=binding, \
                handler=tag.attrs[binding], contents=tag.contents, element=tag))
            
    def find_tags_by_attr(self, soup, attr):
        tags = []
        for tag in soup.find_all(True):
            if attr in tag.attrs.keys():
                tags.append(tag)
        return tags
            
    def set_navigator(self, page_path):
        self.set_navigator_ui(page_path)
        if self.pdg_node != None:
            self.set_navigator_api()

    def set_navigator_ui(self, page_path):
        try:
            soup = BeautifulSoup(open(page_path+'.wxml'), 'html.parser')
        except Exception as e:
            print(f"[wxml] got error: {e}")
        tags = soup.find_all('navigator')
        for tag in tags:
            target = tag['target'] if 'bindsuccess' in tag.attrs.keys() else 'self'
            type = tag['open-type'] if 'open-type' in tag.attrs.keys() else 'navigate'
            bindsuccess = tag['bindsuccess'] if 'bindsuccess' in tag.attrs.keys() else None
            bindfail = tag['bindfail'] if 'bindfail' in tag.attrs.keys() else None
            bindcomplete = tag['bindcomplete'] if 'bindcomplete' in tag.attrs.keys() else None
            if target.lower() == 'miniprogram' and type.lower() in ('navigate', 'navigateBack'):
                extradata = tag['extra-data'] if 'extra-data' in tag.attrs.keys() else None
                if type.lower() == 'navigate':
                    # <navigator open-type=navigateBack>
                    target = tag['app-id'] if 'app-id' in tag.attrs.keys() else 'miniprogram'
                    url = tag['path'] if 'path' in tag.attrs.keys() else 'index'
                    
                    self.navigator['UIElement'].append(
                        Navigator(
                            name='navigator', contents=tag.contents, element=tag, \
                            type=type, target=target, url=url, extradata=extradata, \
                            bindsuccess=bindsuccess, bindfail=bindfail, bindcomplete=bindcomplete
                        )
                    )
                else:
                    # <navigator open-type=navigateBack>
                    self.navigator['UIElement'].append(
                    Navigator(
                        name='navigator', contents=tag.contents, element=tag, \
                        type=type, extradata=extradata, \
                        bindsuccess=bindsuccess, bindfail=bindfail, bindcomplete=bindcomplete
                    )
                )
            else:
                url = tag['url'] if 'url' in tag.attrs.keys() else None
                self.navigator['UIElement'].append(
                    Navigator(
                        name='navigator', contents=tag.contents, element=tag, \
                        type=type, target=target, url=url, \
                        bindsuccess=bindsuccess, bindfail=bindfail, bindcomplete=bindcomplete
                    )
                )

    def set_navigator_api(self):
        for child in self.pdg_node.children:
            if child.name in ('CallExpression', 'TaggedTemplateExpression'):
                if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                    callee = child.children[0]
                    call_expr_value = get_node_computed_value(callee)
                    if type(call_expr_value) == 'str':
                        if call_expr_value in (
                            'wx.navigateToMiniProgram', 
                            'wx.navigateBackMiniProgram',  
                            'wx.exitMiniProgram'
                        ):
                            self.jump_api_handler(self, child, call_expr_value)
                        elif call_expr_value in (
                            'wx.switchTab',
                            'wx.reLaunch',
                            'wx.redirectTo',
                            'wx.navigateTo',
                            'wx.navigateBack'
                        ):
                            self.route_api_handler(self, child, call_expr_value)

    def jump_api_handler(self, child,call_expr_value):
        if call_expr_value == 'wx.navigateToMiniProgram':
            props = {
                'appId': '',
                'path': '',
                'extraData': '',
                'success': None,
                'fail': None,
                'complete': None
            }
            props = self.search_obj_props(obj_exp=child.children[1], props=props)
            self.navigator['NavigateAPI'].append(
                NavigateAPI(
                    type='jump', name='wx.navigateToMiniProgram', \
                    target={props['appId']: props['path']}, extradata=props['extraData'], \
                    bindsuccess=props['success'], bindfail=props['fail'], \
                    bindcomplete=props['complete']
                )
            )
        elif call_expr_value == 'wx.navigateBackMiniProgram':
            props = {
                'extraData': '',
                'success': None,
                'fail': None,
                'complete': None
            }
            props = self.search_obj_props(obj_exp=child.children[1], props=props)
            self.navigator['NavigateAPI'].append(
                NavigateAPI(
                    type='jump', name='wx.navigateBackMiniProgram', \
                    extradata=props['extraData'], bindsuccess=props['success'], \
                    bindfail=props['fail'], bindcomplete=props['complete']
                )
            )
        else:  # wx.exitMiniProgram
            props = {
                'success': None,
                'fail': None,
                'complete': None
            }
            props = self.search_obj_props(obj_exp=child.children[1], props=props)
            self.navigator['NavigateAPI'].append(
                NavigateAPI(
                    type='jump', name='wx.exitMiniProgram', \
                    bindsuccess=props['success'], bindfail=props['fail'], \
                    bindcomplete=props['complete']
                )
            )

    def route_api_handler(self, child, call_expr_value):
        if call_expr_value in ('wx.switchTab', 'wx.reLaunch', 'wx.redirectTo', 'wx.navigateBack'):
            props = {
                'url': '',
                'success': None,
                'fail': None,
                'complete': None
            }
            props = self.search_obj_props(obj_exp=child.children[1], props=props)
            self.navigator['NavigateAPI'].append(
                NavigateAPI(
                    type='route', name=call_expr_value, target=props['url'], \
                    bindsuccess=props['success'], bindfail=props['fail'], \
                    bindcomplete=props['complete']
                )
            )
        # TODO: 对于'wx.navigateTo'的页面间通信, 暂不支持解析EventChannel通信 
        elif call_expr_value == 'wx.navigateTo':
            props = {
                'url': '',
                'success': None,
                'fail': None,
                'complete': None
            }
            props = self.search_obj_props(obj_exp=child.children[1], props=props)
            self.navigator['NavigateAPI'].append(
                NavigateAPI(
                    type='route', name=call_expr_value, target=props['url'], \
                    bindsuccess=props['success'], bindfail=props['fail'], \
                    bindcomplete=props['complete']
                )
            )

    def search_obj_props(self, obj_exp, props):
        for prop in obj_exp.children:
            key = get_node_computed_value(prop.children[0])
            if key in props.keys():
                if key in ('success', 'fail', 'complete'):
                    props[key] = prop.children[1]  # value is FunctionExpression 
                else:
                    props[key] = get_node_computed_value(prop.children[1])  # value is Literal/ObjectExpression
        return props
                        

class MiniApp:
    '''
        Definition of MiniApp.

        -------
        Properties:
        - miniapp_path: str =>
            Path of the miniapp
        - name: str =>
            Name/AppID of miniapp
        - pdg_node: Node =>
            Head node of the PDG of app.js
        - pages: dict =>
            A dict of (page_path, Page object) parsed from app.json(only main package considered)
        - index_page: str =>
            The index_page_path of the miniapp
        - sensi_apis: dict =>
            A dict of {page_path : sensi_api}
            For simple scan, the implementation is based on regular matching
    '''
    def __init__(self, miniapp_path):
        self.miniapp_path = miniapp_path
        self.name = miniapp_path.split('/')[-1]
        self.pdg_node = get_data_flow(input_file=os.path.join(miniapp_path, 'app.js'), benchmarks={})
        self.app_expr_node = get_page_expr_node(self.pdg_node)
        if self.app_expr_node != None:
            self.app_method_nodes = get_page_method_nodes(self.app_expr_node)
        else:
            self.app_method_nodes = None

        self.pages = {}
        self.index_page = ''
        self.sensi_apis = {}
        self.set_pages(miniapp_path)
        self.find_sensi_api(miniapp_path)

    def set_pages(self, miniapp_path):
        if os.path.exists(os.path.join(miniapp_path, 'app.json')):
            # TODO: 只解析主包页面, 分包页面解析暂不支持
            with open(os.path.join(miniapp_path, 'app.json'), 'r', encoding = 'utf-8') as fp:
                app_config = json.load(fp)
                if app_config.get('pages', False):
                    pages = app_config['pages']
                    self.index_page = pages[0]
                    # Case1: Init self.pages with a list of Page Object
                    # self.pages = list(Page(os.path.join(miniapp_path,page), self) for page in pages)
                    
                    # Case2: Init self.pages with a dict of Page Object
                    self.pages = dict((page, Page(os.path.join(miniapp_path,page), self)) for page in pages if 'plugin' not in page)

                    # Case3: Init self.pages with the value of pages(actrually a list) in app.json
                    # self.pages = app_config['pages']
                else:
                    self.pages = None
        else:
            self.pages = None

    def find_sensi_api(self, miniapp_path):
        for page in self.pages.values():
            try:
                with open(os.path.join(miniapp_path, page.page_path+'.js'), 'r', encoding='utf-8') as fp:
                    data = fp.read()
            except FileNotFoundError:
                with open(os.path.join(miniapp_path, page.page_path+'.ts'), 'r', encoding='utf-8') as fp:
                    data = fp.read()

            sensi_api_matched = []
            for sensi_api in config.SENSITIVE_API.keys():
                res = re.search(sensi_api, data)
                if res is not None:
                    sensi_api_matched.append(res.group(0))
            self.sensi_apis[page.page_path] = sensi_api_matched


# test
# app = MiniApp('/root/minidroid/miniprogram-demo')
# print('success')