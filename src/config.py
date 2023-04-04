import os
import sys
import argparse

PROJECT_PATH = os.path.dirname(os.path.abspath('__file__'))
SAVE_PATH_UTG = os.path.dirname(os.path.abspath('__file__'))+'/result/utg'
SAVE_PATH_FCG = os.path.dirname(os.path.abspath('__file__'))+'/result/fcg'
SENSITIVE_API = {'wx.getUserInfo': '收集微信昵称、头像', 
                 'wx.getUserProfile': '收集微信昵称、头像',
                 'wx.getFuzzyLocation': '收集模糊位置信息',
                 'wx.getLocation': '收集精确位置信息',
                 'wx.onLocationChange': '收集精确位置信息',
                 'wx.startLocationUpdate': '收集精确位置信息',
                 'wx.startLocationUpdateBackground': '后台收集精确位置信息',
                 'wx.choosePoi': '收集选择的位置信息',
                 'wx.chooseLocation': '收集选择的位置信息',
                 'wx.chooseAddress': '收集选择的地址信息',
                 'wx.chooseInvoiceTitle': '收集发票信息',
                 'wx.chooseInvoice': '收集发票信息',
                 'wx.getWeRunData':	'收集用户过去三十天微信运动步数',
                 'wx.chooseLicensePlate': '收集用户选择的车牌号信息',
                 'wx.chooseImage': '收集用户从本地相册选择的图片或使用相机拍照',
                 'wx.chooseMedia': '拍摄或从手机相册中选择图片或视频',
                 'wx.chooseVideo': '拍摄视频或从手机相册中选视频',
                 'wx.chooseMessageFile': '收集用户从客户端会话选择的文件',
                 'wx.startRecord': '访问麦克风并开始录音',
                 'wx.joinVoIPChat': '访问麦克风并加入/创建实时语音通话',
                 'RecorderManager.start': '访问麦克风并开始录音',
                 'wx.createCameraContext': '访问摄像头并创建camera上下文',
                 'wx.createVKSession': '访问摄像头并创建vision kit会话对象',
                 'wx.createLivePusherContext': '访问摄像头并创建live-pusher上下文',
                 'wx.openBluetoothAdapter': '访问蓝牙并初始化蓝牙模块',
                 'wx.createBLEPeripheralServer': '访问蓝牙并建立本地作为蓝牙低功耗外围设备的服务端',
                 'wx.saveImageToPhotosAlbum': '访问相册并写入照片',
                 'wx.saveVideoToPhotosAlbum': '访问相册并写入视频',
                 'wx.addPhoneContact': '访问通讯录并写入号码',
                 'wx.addPhoneRepeatCalendar': '访问日历并写入重复事件', 
                 'wx.addPhoneCalendar': '访问日历并写入事件'
                 }

# def params():
#     parser = argparse.ArgumentParser(prog='minidroid', \
#                                      formatter_class=argparse.RawTextHelpFormatter)
#     parser.add_argument("-i", "--input", dest="input", metavar="path", type=str, required=True,
#                         help="path of input mini program(s)."
#                              "Single mini program directory or index files will both fine.")
#     parser.add_argument("-o", "--output", dest="output", metavar="path", type=str, default="results",
#                         help="path of output results."
#                              "The output file will be stored outside of the mini program directories.")
#     parser.add_argument("-c", "--config", dest="config", metavar="path", type=str,
#                         help="path of config file.")
