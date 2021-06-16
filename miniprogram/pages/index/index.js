// miniprogram/pages/index/index.js
var app = getApp();
Page({
  /**
   * 页面的初始数据
   */
  data: {
    rank: '倔强青铜III',
    checked: false,
    points: 300,
    percent: 83.4,
    taskfinished: false,
    wrongfinished: false,
    hiddensetting: true,
    numLearnDone: 0,
    numWrongDone: 0,
    learnNum: 10,
    wrongNum: 10,
    learnSetNum: 0,
    wrongSetNum: 0,
    minusStatusLearn: 'disabled',
    minusStatusWrong: 'disabled',
  },

  bindMinusLearn: function () {
    var learnSetNum = this.data.learnSetNum;
    // 如果大于1时，才可以减  
    if (learnSetNum > 10) {
      learnSetNum -= 10;
    }
    // 只有大于一件的时候，才能normal状态，否则disable状态  
    var minusStatusLearn = learnSetNum <= 10 ? 'disabled' : 'normal';
    // 将数值与状态写回  
    this.setData({
      learnSetNum: learnSetNum,
      minusStatusLearn: minusStatusLearn
    });
  },
  /* 点击加号 */
  bindPlusLearn: function () {
    var learnSetNum = this.data.learnSetNum;
    // 不作过多考虑自增1  
    learnSetNum += 10;
    // 只有大于一件的时候，才能normal状态，否则disable状态  
    var minusStatusLearn = learnSetNum < 10 ? 'disabled' : 'normal';
    // 将数值与状态写回  
    this.setData({
      learnSetNum: learnSetNum,
      minusStatusLearn: minusStatusLearn
    });
  },

  bindMinusWrong: function () {
    var wrongSetNum = this.data.wrongSetNum;
    // 如果大于1时，才可以减  
    if (wrongSetNum > 10) {
      wrongSetNum -= 10;
    }
    // 只有大于一件的时候，才能normal状态，否则disable状态  
    var minusStatusWrong = wrongSetNum <= 10 ? 'disabled' : 'normal';
    // 将数值与状态写回  
    this.setData({
      wrongSetNum: wrongSetNum,
      minusStatusWrong: minusStatusWrong
    });
  },
  /* 点击加号 */
  bindPlusWrong: function () {
    var wrongSetNum = this.data.wrongSetNum;
    // 不作过多考虑自增1  
    wrongSetNum += 10;
    // 只有大于一件的时候，才能normal状态，否则disable状态  
    var minusStatusWrong = wrongSetNum < 10 ? 'disabled' : 'normal';
    // 将数值与状态写回  
    this.setData({
      wrongSetNum: wrongSetNum,
      minusStatusWrong: minusStatusWrong
    });
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    console.log(app.globalData.questionDone);
    var numLearnDone = app.globalData.questionDone;
    if (this.data.learnNum <= numLearnDone) {
      this.setData({
        taskfinished: true,
      })
    }
    this.setData({
      numLearnDone: numLearnDone,
    })
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },

  Check: function () {
    console.log(this.data.checked);
    this.setData({
      checked: true,
    })
  },

  Confirm: function () {
    console.log(this.data.learnNum);
    var learnNum = this.data.learnSetNum;
    var wrongNum = this.data.wrongSetNum;
    if (learnNum > app.globalData.questionDone) {
      this.setData({
        taskfinished: false,
      })
    }
    this.setData({
      learnNum: learnNum,
      wrongNum: wrongNum,
      hiddensetting: true,
    })
    console.log(this.data.numLearnDone);
    console.log(this.data.learnNum);
    console.log(this.data.taskfinished);
  },

  Cancel: function () {
    console.log(this.data.hiddensetting);
    this.setData({
      hiddensetting: true,
    })
  },

  OpenSetting: function () {
    var wrongSetNum = this.data.wrongNum;
    var learnSetNum = this.data.learnNum;
    this.setData({
      hiddensetting: false,
      wrongSetNum: wrongSetNum,
      learnSetNum: learnSetNum,
    })
  },

  OpenRank: function(){
    wx.navigateTo({
      url: '../ranking/ranking' 
    })
  }
})