<div align="center">

# NoneBot-Adapter-DoDo

_✨ DoDo 协议适配 ✨_

</div>

## 配置

修改 NoneBot 配置文件 `.env` 或者 `.env.*`。

### Driver

参考 [driver](https://nonebot.dev/docs/appendices/config#driver) 配置项，添加 `HTTPClient` 和 `WebSocketClient` 支持。

如：

```dotenv
DRIVER=~aiohttp
```

> websockets 驱动器存在一些问题，建议使用 aiohttp 驱动器。


### DODO_BOTS

> 暂只支持 `WebSocket` 连接， `WebHook` 开发中，请先使用 WebSocket 连接模式

从[DoDo开放平台](https://doker.imdodo.com/)创建机器人，获取 `client_id` 和 `token`，并在配置文件中配置机器人帐号列表。如：

```dotenv
DODO_BOTS='
[
  {
    "client_id": "xxx",
    "token": "xxx"
  }
]
'
```

## 使用

### 支持消息段

可收发：

- `MessageSegment.text` 文本(支持[Markdown](https://open.imdodo.com/dev/api/message.html#markdon%E8%AF%AD%E6%B3%95))
- `MessageSegment.at_user` @用户
- `MessageSegment.channel_link` 跳转频道
- `MessageSegment.reference` 引用(回复)消息
- `MessageSegment.picture` 图片
- `MessageSegment.video` 视频
- `MessageSegment.card` 卡片消息

> 发送图片和视频所需要的链接通过 `Bot.set_resouce_picture_upload` 接口来上传，返回结果中的的 `url` 即为所需的链接。

> 图片和视频只能单独发送，不能和其他消息段一起发送。卡片消息可以和文本消息段一起发送。

仅支持接收：

- `type:at_role`: 艾特身份组
- `type:at_all`: 艾特所有人
- `type:share`: 分享消息
- `type:file`: 文件消息
- `type:red_packet`: 红包消息

### 支持事件

- `ChannelMessageEvent` 频道消息事件
- `MessageReactionEvent` 消息表情反应事件
- `CardMessageButtonClickEvent` 卡片消息按钮点击事件
- `CardMessageFormSubmitEvent` 卡片消息表单回传事件
- `CardMessageListSubmitEvent` 卡片消息列表回传事件
- `ChannelVoiceMemberJoinEvent` 成员加入语音频道事件
- `ChannelVoiceMemberLeaveEvent` 成员退出语音频道事件
- `ChannelArticleEvent` 帖子发布事件
- `ChannelArticleCommentEvent` 帖子评论回复事件
- `MemberJoinEvent` 成员加入事件
- `MemberLeaveEvent` 成员离开事件
- `MemberInviteEvent` 成员邀请事件
- `GiftSendEvent` 赠礼成功事件
- `IntegralChangeEvent` 积分变更事件
- `GoodsPurchaseEvent` 商品购买成功事件
- `PersonalMessageEvent` 私信事件
