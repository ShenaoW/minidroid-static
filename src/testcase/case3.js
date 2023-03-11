Page({
    onLoad(options) {
        wx.authorize({
            scope: 'scope.userLocation',
            success () {
                // 用户已经同意小程序使用位置功能，后续调用 wx.getLocation 接口不会弹窗询问
                wx.getLocation({
                    type: 'wgs84',
                    success (res) {
                        console.log(res.longtitude, res.latitude)
                    },
                    fail(res){
                        console.log("fail")
                    }
                })
            },
            fail () {
                wx.navigateTo({
                    url: 'pages/authorize/authorize'
               }) 
            }
        })
    }
})