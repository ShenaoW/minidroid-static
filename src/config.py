import os
import sys

PROJECT_PATH = os.path.dirname(os.path.abspath('__file__'))
SAVE_PATH_UTG = os.path.dirname(os.path.abspath('__file__'))+'/result/utg'
SAVE_PATH_FCG = os.path.dirname(os.path.abspath('__file__'))+'/result/fcg'
UNPACK_COMMAND = 'node ' + PROJECT_PATH + os.sep + 'src/utils/wxappUnpacker/wuWxapkg.js {}'


SENSITIVE_API = {
    'wx.getUserInfo': '收集你的微信昵称、头像',
    'wx.getUserProfile': '收集你的微信昵称、头像',
    # '<button open-type="userInfo">': '收集你的微信昵称、头像',
    # 'wx.authorize(scope="scope.userLocation")': '收集你的位置信息',
    # 'wx.authorize(scope="scope.userLocationBackground")': '收集你的位置信息',
    'wx.getLocation': '收集你的位置信息',
    'wx.getFuzzyLocation': '收集你的位置信息',
    'wx.onLocationChange': '收集你的位置信息',
    'wx.startLocationUpdate': '收集你的位置信息',
    'wx.startLocationUpdateBackground': '收集你的位置信息',
    'wx.choosePoi': '收集你的位置信息',
    'wx.chooseLocation': '收集你的位置信息',
    'wx.chooseAddress': '收集你的地址',
    'wx.chooseInvoiceTitle': '收集你的发票信息',
    'wx.chooseInvoice': '收集你的发票信息',
    # 'wx.authorize(scope="scope.werun")': '收集你的微信运动步数',
    'wx.getWeRunData': '收集你的微信运动步数',
    # "<button open-type='getPhoneNumber'>": '收集你的手机号',
    'wx.chooseLicensePlate': '收集你的车牌号',
    'wx.chooseImage': '收集你选中的照片或视频信息',
    'wx.chooseMedia': '收集你选中的照片或视频信息',
    'wx.chooseVideo': '收集你选中的照片或视频信息',
    'wx.chooseMessageFile': '收集你选中的文件',
    # 'wx.authorize(scope="scope.record")': '访问你的麦克风',
    'wx.startRecord': '访问你的麦克风',
    'RecorderManager.start': '访问你的麦克风',
    # '<live-pusher>': '访问你的麦克风',
    'wx.joinVoIPChat': '访问你的麦克风',
    # 'wx.authorize(scope="scope.camera")': '访问你的摄像头',
    'wx.createCameraContext': '访问你的摄像头',
    'wx.createVKSession': '访问你的摄像头',
    'wx.createLivePusherContext': '访问你的摄像头',
    # '<camera>': '访问你的摄像头',
    # '<live-pusher>': '访问你的摄像头',
    # '<voip-room>': '访问你的摄像头',
    'wx.openBluetoothAdapter': '访问你的蓝牙',
    'wx.createBLEPeripheralServer': '访问你的蓝牙',
    # 'wx.authorize(scope="scope.writePhotosAlbum")': '使用你的相册（仅写入）权限',
    'wx.saveImageToPhotosAlbum': '使用你的相册（仅写入）权限',
    'wx.saveVideoToPhotosAlbum': '使用你的相册（仅写入）权限',
    'wx.addPhoneContact': '使用你的通讯录（仅写入）权限',
    'wx.addPhoneRepeatCalendar': '使用你的日历（仅写入）权限',
    'wx.addPhoneCalendar': '使用你的日历（仅写入）权限'
}

ROUTE_API = ['wx.switchTab',
             'wx.reLaunch',
             'wx.redirectTo',
             'wx.navigateTo',
             'wx.navigateBack']

NAVIGATE_API = ['wx.navigateToMiniProgram',
                'wx.navigateBackMiniProgram',
                'wx.exitMiniProgram']

BINDING_EVENTS = [
    # Bubbling Event
    'bindtap',
    'bindlongtap',  # including longtap/longpress event

    # Non-bubbling Event in Specific Compenonts
    'bindgetuserinfo',  # <button open-type='getUserInfo' bindgetuserinfo=handler_fun>
    # <button open-type='getPhoneNumber' bindgetphonenumber=handler_fun>
    'bindgetphonenumber',
    'bindchooseavatar',  # <button open-type='chooseAvatar' bindchooseavatar=handler_fun>
    'bindopensetting',  # <button open-type='openSetting' bindopensetting=handler_fun>
    'bindlaunchapp',  # <button open-type='launchApp' bindlaunchapp=handler_fun>

    'bindsubmit'  # <form binsubmit=handler_fun>
]