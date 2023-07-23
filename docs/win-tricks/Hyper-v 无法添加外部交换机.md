---
tags:
    - Hyper-V
    - Bug
create_time: 2023-07-19
update_time: 2023-07-23
---

# Hyper-v 添加外部交换机问题

!!! note "可能过时"

    这篇文章写于 2023 年，当你在阅读时本文信息可能以及过时。


## 错误提示

* 找不到对象
* 无法绑定端口

参考解决方案：https://pomeroy.me/2020/08/hyper-v-virtual-switch-creation-woes/#comment-411452

## 省流

> I had this same issue with the Intel Wifi 6 AX201 today. Here’s what I discovered.

> When I created the Hyper-V External switch for the first time, it failed to create with an error about not being able to find some component. And of course, I was no longer connected to any wireless network. I tried the usual things of course (MS diagnostic fixer, netcfg -d, etc), nothing worked. BUT, I did notice one thing. To get networking back, all I did was disable my wireless card and re-enable. But when I did that, the Network Bridge network device all of a sudden appeared in the network adapters list. Hmm, if only I could create a switch and tell it to “connect itself” to the bridge. But alas, that is not possible.

> Then it hit me what the problem might be. Something is not working correctly such that, when trying to create the switch and attach it to the Network Bridge, the bridge could not be found. BUT when I disable/enable the WiFi card, the bridge magically “shows up”.

> So, armed with this knowledge, I followed these steps:1. Open Network Sharing Center2. Click ‘Change Adapter Settings’ in the left-hand menu3. Create the new External Switch in Hyper-V Manager. Or, you can also use New-VMSwitch PowerShell cmdlet. Both methods work.4. While the “Applying” dialog is spinning away, or the PowerShell Progress “dialog”, switch over to the network adapters dialog you have open in Control Panel.5. Disable your WiFi adapter6. Reenable your Wifi adapter

> In a few moments, your new Hyper-V External Switch should be created.


## 解决方案翻译

1. 打开网络适配器配置页
2. 在 Hyper-V 中新建虚拟外部交换机
3. 当 Hyper-V 弹出提示正在配置更改的窗口时，迅速切换到网络适配器配置页，禁用交换机附加到的那个网卡，然后再启用
4. 过一会儿，Hyper-V 就成功添加交换机了