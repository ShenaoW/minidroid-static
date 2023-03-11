const app = getApp()

Page({
  data: {

  },
  onLoad() {
    wx.authorize({
      scope: 'scope.record',
      success(){
        wx.startRecord()
      },
      fail(){
        wx.showModal({
          title: '获取授权',
          content: '如果您不授权，相应功能无法使用',
          showCancel: true,
          success: (res) => {
            if (res.cancel) {
              wx.exitMiniProgram({
                success(){
                  console.log('exit success')
                },
                fail(){
                  console.log('exit fail')
                }
              })
            }
            if (res.confirm) {
              wx.openSetting({
                success (res) {
                  console.log(res.authSetting)
                  // res.authSetting = {
                  //   "scope.userInfo": true,
                  //   "scope.userLocation": true
                  // }
                }
              })
            }
          }
        })
      }
    })

  },
})
