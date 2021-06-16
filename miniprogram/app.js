//app.js
var jsonList = require('data/json.js');

App({
  globalData: {
    questionList: jsonList.questionList,
    questionDone: 0,
  }
})
