# -*- encoding=utf8 -*-
__author__ = "Shenao Wang"

from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from poco import exceptions
from airtest.core.api import *
from airtest.cli.parser import cli_setup


def start_miniapp(miniapp):
    start_app('com.tencent.mm')
    poco = AndroidUiautomationPoco()
    poco.swipe((0.5,0.15),(0.5,0.9),duration=0.2)
    poco(text='搜索小程序', type='android.widget.TextView').click()
    sleep(1)
    try:
        # 页面解析不稳定，try except捕获异常
        poco(text='搜索', type='android.widget.EditText').set_text(miniapp)
        poco(text='搜索', type='android.widget.TextView').click()
        poco = AndroidUiautomationPoco()
        poco(name=miniapp, type='View').click()
    except exceptions.PocoNoSuchNodeException:
        # 如果没有解析到控件则基于相对位置点击 
        poco.click((0.5, 0.05))
        text(miniapp)
        poco.click((0.9, 0.05))
        sleep(3)
        poco.click((0.5, 0.2))

        
        
def traversal_ingle_page():
    poco = AndroidUiautomationPoco()
    poco.freeze
    

def minidroid(miniapp):
    start_miniapp(miniapp)
    
    
if __name__ == '__main__':
    if not cli_setup():
        auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/emulator-5554?cap_method=MINICAP&&ori_method=MINICAPORI&&touch_method=MINITOUCH",])
    minidroid('小程序示例')
