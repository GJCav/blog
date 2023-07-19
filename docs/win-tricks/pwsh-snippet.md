---
tags:
    - pwsh
    - Laptop
---

# Powershell Snippet

一些有趣小脚本。


## 锁屏 + 息屏

win 的笔记本锁屏后不会自动息屏，导致浪费电池。如果你是电池葛朗台，那么肯定希望能手动控制息屏，但 win 系统又不提供这个功能，所以就有了这么个脚本。

``` pwsh
rundll32.exe user32.dll,LockWorkStation
(Add-Type 
'
    [DllImport("user32.dll")]
    public static extern int SendMessage(
        int hWnd, 
        int hMsg, 
        int wParam, 
        int lParam
    );
' -Name a -Pas)::SendMessage(-1,0x0112,0xF170,2)
```

但 powershell 启动实在是有点慢，不如把这个编译成可执行文件吧：
[![](https://img.shields.io/badge/GJCav-screenoff-blue?logo=github)](https://github.com/GJCav/screenoff_csharp)


