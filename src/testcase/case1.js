Page({
    onLoad(options) {
        wx.authorize({
            scope: 'scope.userLocation',
        })
        wx.getLocation({
            type: 'wgs84',
            success (res) {
                console.log(res.longtitude, res.latitude)
            },
            fail(res){
                console.log("fail")
            }
        })
    }
})
    