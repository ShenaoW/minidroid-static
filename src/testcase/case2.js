Page({
    onLoad(options) {
        wx.authorize({
            scope: 'scope.bluetooth',
            scope: 'scope.camera'
        })
        wx.openBluetoothAdapter({
            success (res) {
              console.log(res)
            }
        })
        camera = wx.createCameraContext()
        camera.startRecord({
            success(res) {
                console.log("success")
            }
        })
    }
})
    