---
tags:
    - Python
    - conda
    - virtualenv
---

# conda 推荐配置

## anaconda or miniconda ?

本配置同时适用于 anaconda 和 miniconda，但我推荐使用 miniconda。

anaconda 自带了太多的库，miniconda 相比起来简洁很多。

## Windows 下安装

从官网下载安装包，安装，在中间步骤选择 `register as system python` 啥的。

安装好后，在`%userprofile%` 目录新建文件`.condarc`，进行换源，参考 [清华开源镜像站](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/) 中的示例。但**存在一些修改**。

推荐配置如下：

```yaml linenums="1"
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch-lts: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
envs_dirs:
  - D:\path\to\store\conda\data

auto_activate_base: false
```

- `auto_activate_base: false` ，避免直接进入 base 环境，后续将分析这一步的目的。
- `envs_dirs` 之后使用 conda 创建的虚拟环境默认安装在 C 盘，C 盘比较寸土寸金，所以换个地方存放。

打开控制台，输入`conda` 理应返回 `找不到指令`  之类的错误提示，这是正常的。然后网上的教程就会让我们向系统 Path 变量中添加`conda` 的路径，经过我的实践，这个做法**不是最优的**，而且可能导致后续一些非常令人烦躁的问题。

下面给出我认为最优的解决方案：

- 使用管理员权限打开 powershell 

    !!! warning 

        如果是 win10 系统且自行安装了最新版本的 powershell 和 windows terminal。那系统的pwsh和terminal的pwsh大概率不是一个东西。系统的pwsh 是一个老版本的 pwsh，而 win terminal 中的 pwsh 大概率是自行安装的新版本的 pwsh。
        
        vscode 中默认使用的大概率是系统的老版本 pwsh。

        要小心这两个不同版本的 pwsh 造成困扰。

        win11 系统暂未测试。

- 执行下述命令
    
    ```powershell
    cd path_to_miniconda/Scripts
    .\conda init
    ```
    
- 等待命令执行完毕，重新打开 powershell，输入 `conda` 可以看到命令被正常执行

解释：conda 为了管理版本，需要在 shell 中做很多工作，这些工作远远比我们自己在 path 中添加一些路径复杂，自行添加环境变量并且没有执行 `conda init` 会导致 conda 还没有正常 activate 一个环境，我们在命令行中就能直接使用 base 环境的 python，相当于绕过了 conda 的管理机制，所以就不要自作多情给 conda 帮倒忙了。

现在再说配置`auto_activate_base: false` 的原因，我建议**不要使用base环境**。因为 base 环境是 conda 用于运行自身的环境，base 的 `sites-packages` 目录也是被默认设置为 readonly 的，conda 官方就不太想让我们修改 base 环境中的包。如果在 base 环境下使用 `pip install` ，因为没有访问 base 的 `sites-packages` ，pip 会把库安装到 `%appdata%/Python` 下，占用可怜的 C 盘空间。经过测试，此时就算修改`sites.py` 中的`USER-SITES`也没用。

所以，我建议不要使用base环境，而是**重新创建一个名为 default 的环境，**然后配置 powershell 的的`$userprofile` ，每次运行前激活 `default` 环境。这样既方便，又能定义环境安装位置和pip安装库位置，也能保证使用的环境是最干净的（base 环境默认安装了 pyyaml 等 conda 会用到的库）。

## Linux 下安装

基本同 win 配置，无非是改改路径、改改 `.bashrc`。

