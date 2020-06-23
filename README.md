# 简介

一个能够实现在学堂在线(next.xuetang.com) 自动完成作业的小脚本

原理也很简单，通过发送HTTP POST请求

如果喜欢，请给我一个星星 :)

# 测试环境

- Python 3.7.4
- Windows 10 1909
- Requests 2.22.0

```bash
pip(3) install requests
```

- Uncurl

```bash
pip(3) install uncurl
```

# 功能实现

- 通过`Curl`进行登录
- 列出当前学习的课程列表并使用序号选择
- 自动跳过已经做过的题
- 自动跳过简答题
- 答题间隔`3s`以防被ban

# 使用注意

## 提取Curl

因为学堂在线的登录采用`TencentCaptcha`，目前没有什么思路去实现模拟登录，所以需要手动提取一个Curl来为程序提供身份验证信息。 

提取的`curl`中的`cookie`需要包含`x-csrftoken`，否则会出现跨域请求错误。

### Chrome(Chromium) 下的提取

打开课程页面，比如

```
https://next.xuetangx.com/learn/NUDT12041000081/NUDT12041000081/1510792/
```

按下`F12`以打开`Chrome developer tools`,  并且切换到`Network`选项卡

如下操作打开`Filter` 并选中`XHR`类型

![README](https://raw.githubusercontent.com/BakaFT/XuetangX-AutoAnswering/master/README.png)

然后刷新页面，等待加载完毕。

寻找任意一条，如图所示，在`Headers`属性卡里包含`x-csrftoken`的请求

![README2](https://raw.githubusercontent.com/BakaFT/XuetangX-AutoAnswering/master/README2.png)

右键这条请求，依次选择`Copy` - `Copy as cURL(bash)`，程序要求输入cURL时，直接粘贴即可。
