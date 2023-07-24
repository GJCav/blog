---
create_time: 2023-07-24
update_time: 2023-07-24
tags:
    - linux
    - waydroid
    - android
---

# Waydroid 折腾

Waydroid 是一个可以在 Linux 上运行 Android 的工具。但是，Ubuntu 20 默认使用的是 X11 后端，而 Waydroid 必须使用 Wayland 后端。

有两种解决方法：使用 Weston 进行中转或者升级到 Ubuntu 22。使用 Weston 进行中转时剪切板不能共享了。但升级到 Ubuntu 22 又无法接受，因为我使用的是 NVIDIA 显卡，和 Waydroid 还有很多冲突。

<!-- more -->

## 失败尝试

坑1：ubuntu 20 默认桌面后端是 x11，但 waydroid 必须使用 wayland 后端

- 解决1：使用 weston 进行中转
    - 导致新坑：剪切板不共享了
    - 参考：https://github.com/waydroid/waydroid/issues/309#issuecomment-1329881878
- 解决2：更新到 ubuntu 22，默认使用 wayland 但是 wayland 和 nvidia 显卡有些小冲突
    - 似乎 2023 年后这些冲突慢慢被解决了

采用 weston 进行中转：

坑2：启动 waydroid 后，导致系统在 weston 中新建窗口

- 参考： [Waydroid in Weston](https://unix.stackexchange.com/questions/742977/waydroid-in-weston-all-newly-windows-open-in-weston-can-not-multitask-linux)

- 解决：启动 weston 时更换 socket 名

最终启动脚本如下：

```bash
#!/bin/sh

weston --socket=wayland-waydroid &
sleep 2
export WAYLAND_DISPLAY=wayland-waydroid
waydroid session start &
```

然后在其他终端使用：

```bash
waydroid show-full-ui
```

坑3：没有 Google Protect 验证，所以不能使用 Google Play

- 官方解决：https://docs.waydro.id/faq/google-play-certification
- 但似乎不太好用

坑4：这个是 x86_64 的安卓，但现在大多都是 arm64 的安卓，所以很容易出现apk安装不了的情况

- 解决：安装指令转译层
- 参考：https://github.com/casualsnek/waydroid_script
- 这一套小连招还能装 magisk 等东西，感觉更好用，但还没试过

> 安装微信参考：https://github.com/waydroid/waydroid/issues/844
> 

~~坑5：waydroid 似乎不提供 IMEI~~

~~但微信要用imei加密~~

~~坑6：安装微信似乎容易导致被封号~~

这些问题不大，没有遇到过

无法解决的坑：

在 ubuntu20 安装 waydroid，系统重启后 waydroid container 会损坏，所以不考虑在 ub20 上继续做事了

## 最终解决

使用 ubuntu22 安装 waydroid

使用 https://github.com/casualsnek/waydroid_script 安装 ARM 翻译层

然后可以正常安装微信

## SB 微信

微信不允许同时在两台手机上登陆账号，意味着如果在 waydroid 上登陆，那么手机上就会登出

此外，SB微信不能很好的处理宽屏幕显示，会导致屏幕横过来显示，解决方法：

- 法一，锁定方向：`sudo waydroid shell wm set-fix-to-user-rotation enabled` 但会导致很大的黑边
- 法二，把安卓分辨率设置为高瘦型：
    
    ```bash
    waydroid prop set persist.waydroid.width 380
    waydroid prop set persist.waydroid.height 600
    ```
    
    但这样 waydroid 的窗口不能移动，会显示在屏幕的左上角
    

我的评价是，不如安装 win 虚拟机，跑一个电脑版微信