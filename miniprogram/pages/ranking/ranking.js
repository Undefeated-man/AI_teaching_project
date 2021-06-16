Page({
  data: {
    rankingList: [
      {
        id: 1,
        userName: "Aaaa",
        userImg: "image/a.jpg",
        rank: "荣耀王者",
        score: 283874
      }, 
      {
        id: 2,
        userName: "Bbbb",
        userImg: "image/b.jpg",
        rank: "荣耀王者",
        score: 28387
      },
      {
        id: 3,
        userName: "Cccc",
        userImg: "image/c.jpg",
        rank: "最强王者",
        score: 2838
      },
      {
        id: 4,
        userName: "Dddd",
        userImg: "image/d.jpg",
        rank: "最强王者",
        score: 283
      },
      {
        id: 5,
        userName: "Eeee",
        userImg: "image/e.jpg",
        rank: "至尊星曜I",
        score: 277
      },
      {
        id: 6,
        userName: "Ffff",
        userImg: "image/f.jpg",
        rank: "至尊星曜I",
        score: 235
      },
      {
        id: 7,
        userName: "Gggg",
        userImg: "image/g.jpg",
        rank: "至尊星曜I",
        score: 28
      },
    ],
    selfRanking: {
      userName: "my",
      userImg: "image/self.jpg",
      rank: "倔强青铜",
      index: "-",
      score: 15
    }, 
  },

  onLoad(){
    wx.setNavigationBarTitle({
      title: '排行榜'  //修改title
    })
  }
})