---
tags:
    - Baidu
    - Baiduyun
    - bat
---

# 限制百度云 CPU 占用

<style>
.hide {
    background-color: black;
    color: black;
    display: inline-block;
}

.hide:hover {
    background-color: inherit;
    color: inherit;
}
</style>

<div class="hide">
脑瘫百度云占用你奶奶个腿的CPU扫我硬盘是吧给爷爬
</div>

所以通过设置 CPU 相关性，限制百度云只能在某个核心上运行，降低 CPU 占用。

``` bat
cd /d %~dp0
start /affinity 4000 BaiduNetdisk.exe
```

`/affinity` 后面的是一个 16 进制数字，转换为二进制后每一位和一个 CPU 对应，值为 1 表示这个程序可以在这个 CPU 上运行。
