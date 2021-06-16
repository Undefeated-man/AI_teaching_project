// pages/speak/speak.js
const recorderManager = wx.getRecorderManager()

Page({
  data: {
      qnum: 1,
      qcontent: "How to say \"人人为己\" ？",
      recordState: false,
      result:true,
      answer:"",
      done: false,
      collected: false,
  },

  onLoad: function (options) {
    this.initRecord()
  },

  Collect: function() {
    console.log(this.data.collected);
    if(this.data.collected) {
      wx.showToast({
        title: '取消收藏',
        icon: 'none',
        duration: 2000,
        success: function(){
          return;
        }
      })
      this.setData({
        collected: false,
      })
    }else{
      wx.showToast({
        title: '收藏成功',
        icon: 'none',
        duration: 2000,
        success: function(){
          return;
        }
      })
      this.setData({
        collected: true,
      })
    }
    
  },

  initRecord() {
    let that = this;
    recorderManager.onError((res) => {
      console.log("error", res)
    })
    recorderManager.onStart(() => {
      console.log('recorder start')
    })
    recorderManager.onStop((res) => {
      console.log('recorder stop', res)
      //that.upload(res.tempFilePath)
      that.setData({
        answer: "Everybody's out for himself.",
        done: true,
        result: true,
      })
    })
  },

  upload(filePath) {
    let that = this
    wx.uploadFile({
      url: 'http://34.92.251.246:8091',
      filePath: filePath,
      name:"file",
      header: {
        "Content-Type": "multipart/form-data"
      },
      formData:{
        qnum: that.qnum
      },
      success:function(res){
        console.log(res)
        var ans = JSON.parse(res.data)
        that.setData({
          result: ans
        })
      },
      fail: function(res){
        console.log(res);
      }
    })
  },

  // start recording
  start() {
      wx.showLoading({
        title: 'Recording',
      })
    const options = {
      duration: 10000,
      sampleRate: 44100,
      numberOfChannels: 1,
      encodeBitRate: 192000,
      format: 'mp3',
      frameSize: 50
    }
    recorderManager.start(options)
  },

  // end recording
  end() {
    wx.hideLoading({
      success: (res) => {},
    })
    recorderManager.stop()
  },

  nextQuestion: function() {
    wx.navigateTo({
      url: '../speak/speak'
    })
  }
})
