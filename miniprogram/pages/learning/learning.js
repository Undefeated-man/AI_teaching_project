Page({
  data: {
    currLevel : 2,
  },
  onLoad: function (options) {

  },
  toTestPage: function (e) {
    switch (this.data.currLevel) {
      case '1':
        let testId = e.currentTarget.dataset['testid'];
        wx.navigateTo({
          url: '../choice/choice?testId=' + testId //跳转到答题页， 传入试题
        })
        break;
      case '2':
        wx.navigateTo({
          url: '../speak/speak' //
        })
        break;

    }
  },

  changeState: function (e) {
    var that = this;
    if(e.currentTarget.dataset.unlock) {
        that.setData({
          currLevel: e.currentTarget.dataset.level
        });
    };
  },
})