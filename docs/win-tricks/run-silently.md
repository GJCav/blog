---
tags:
    - VB
create_time: 2023-07-19
update_time: 2023-07-23
---

# 无窗口运行某程序

适合用来干坏事

使用VB，创建文件 `run.vbs` 里面写：

```vbs
set ws=WScript.CreateObject("WScript.Shell")
ws.Run "要运行的程序",0
```

击即可静默运行，可以用这个启动python、bat、ps1等