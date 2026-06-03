# 云直播开发指南

> 云直播仅支持H264（视频编码）和AAC（音频编码）的出流，请在设备IP本地局域网管理页面切换设备编码格式，以提高播放器兼容性。

## 零门槛玩转直播

#### 1，购买视频流量

点击<a href="https://open.imoulife.com/consoleNew/resourceManage/myResource">”控制台-我的资源“</a>进入我的资源服务页面，查看开发者当前剩余流量，如流量不足（或即将不足）请先购买流量或者带宽。

![演示图片](https://resource-public.oss-cn-hangzhou.aliyuncs.com/open/develop/source_1606896889402/flow.PNG)

#### 2，添加直播设备

创建直播前需要将直播的设备添加到开发者账号下（即乐橙账号下），一共有两种方式添加设备：

> 方式一：乐橙app登陆开发者账号，并添加相应设备；
>
> 方式二：参考开放平台SDK DEMO添加设备；

注：若您的乐橙账号下面还没有设备，请前往乐橙官方商城[www.imoulife.com](http://www.imoulife.com/)购买设备，并且下载乐橙APP添加购买的设备：

#### 3，直播控制台

通过[控制台-产品与服务-直播服务](https://open.imoulife.com/consoleNew/vas/live)可以获取设备创建的直播地址，对直播设置直播时间段，以及配置自定义H5页面。

自定义H5页面的配置选项包括：标题、简介、logo图片、直播视频封面、直播清晰度、直播是否加密。开发者可根据自身直播应用场景上传不同主题的图片、文案，点击预览获取二维码，开发者可以直接将二维码分享到微信、微博。

![演示图片](https://resource-public.oss-cn-hangzhou.aliyuncs.com/open/develop/source_1606896898287/live.png)

