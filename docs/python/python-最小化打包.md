---
tags:
    - Python
    - pack
    - program_distribution
---

# 最小化打包 非pyinstaller

## 为什么不使用 pyinstaller?

想用就用 :laughing:。

不过这篇文章揭示了一些打包的内部机制，具有更高的可玩性和定制性。同时，一般该方案得到的程序包大小小于 `pyinstaller` 打包结果，毕竟其中可以作很多人工优化。

## 打包基本原理

- 使用 embedded 版本的 Python 环境，这个环境的 Python 不含pip，仅占用 10MB 空间，不能在小了
- 利用开发环境中的 pip 将依赖的第三方库提取到 embedded python 中
- 修改 `pythonXX._pth` 文件，使 embedded python 能找到第三方库

## 具体操作

1. 查看开发环境 python 版本，例如 3.8.3
2. 在 python 官网下载该版本 embedded 版本，得到一个 zip 包
3. 打包目录整体结构如下：

```jsx
my-program/
	|- runtime/
	|- main.py
	|- start.bat
```

1. 将 embedded python 解压到 runtime
2. 创建 `runtime/sites-packages` 文件夹
3. 使用`pip install pyqt5 -t runtime/sites-packages` 将需要的第三方库安装到该文件夹（该步骤可先创建虚拟环境，然后再执行）。这里使用 pyqt5 作为例子，其他第三方库同理。
4. 打开 `runtime/pythonXX._pth` ，这里的XX是版本号，嵌入式Python会依据这个文件加载库，修改如下：
    
    ```python
    python38.zip
    .
    ..
    sites-packages
    
    # Uncomment to run site.main() automatically
    # import site
    ```
    
    - `python38.zip` 是内建库，Python版本不同，这里可能不同
    - `.` 添加`._pth` 文件所在目录到搜索路径
    - `..` 添加 `my-program/` 到搜索路径，因为我们的Python代码写在这个目录下
    - `sites-packages` 添加`runtime/sites-packages` 即第三方库到搜索路径
5. 最后编写一个启动脚本`start.bat` ，用来启动程序，例如：
    
    ```powershell
    @echo off
    cd /d %~dp0
    start .\runtime\pythonw.exe screenshot.py
    ```
    
    - 因为示例程序不需要控制台，所以使用 pythonw 启动


已知问题：

- 注意到`python38.zip` 压缩包中有`sites-packages` 文件夹，但把相关第三方库加进去后，还是找不到，不知道为啥


## 其余优化

- 对 pyqt，可以通过删除不会使用到的dll文件进一步压缩体积，实测可以从150M 压缩到 40M 左右。