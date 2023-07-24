---
create_time: 2023-07-24
update_time: 2023-07-24
tags:
    - linux
    - screen
    - terminal-multiplexer
---

# screen 速查

[TOC]

<!-- more -->

## 基本概念

**会话 session**包含多个**窗口 screen**

## 使用

命令：

```bash
screen -S test     # 创建名为 test 的会话
screen -r test    # 回复会话
screen -r       # 回复仅有的会话
screen -d test    # 断开连接到 test 的会话
screen -d -r    # 若必要先分离，再回复
# 更多参见man screen
screen -ls       # 列出所有会话
exit         # 退出会话

```

常用快捷键：

`^c` 的含义是`Ctrl+a, c`

```
^?    # 显示所有快捷键

^d    # 分离会话

^c    # 创建窗口
^k    # 删除当前窗口
^A    # 给当前窗口取名字
^i    # 显示窗口信息
^"    # 选择窗口

^[    # 进入复制模式，主要用途是查看之前的输出（scrollback buffer）
^:    # 进入指令模式
			# 常用指令
			#   hardcopy -h <filename>  把所有 scrollback buffer 保存到文件

^S    # 水平分割当前区域
^|    # 竖直分割点前区域
^Q    # 删除其他所有区域
^X    # 删除当前区域
```