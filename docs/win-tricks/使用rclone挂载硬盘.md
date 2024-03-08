---
tags:
    - win
    - rclone
    - awesome-tool

create_time: 2024-02-03
update_time: 2024-03-08
---



# Win 使用 Rclone 挂载硬盘

省流：

*   SFTP 协议：
    ```powershell
    .\rclone.exe mount ^
    	":sftp,ssh=ssh username@hostname,disable_hashcheck=true,shell_type=unix:/path/todir/" ^
    	G: ^
    	--vfs-cache-mode full ^
    	--volname "a remote driver"
    ```





<!-- more -->

## Rclone 安装

1.   从 Rclone 官网下载、安装 [Rclone](https://rclone.org/downloads/)
2.   为了在 Windows 系统挂载硬盘，还需要安装 [winfsp: FUSE for Windows](https://github.com/winfsp/winfsp)



## 挂载硬盘

该方法需要先创建配置，然后再使用指令挂载，稍显麻烦。如果想跳过配置创建，只使用单行命令挂载硬盘，可直接跳转到 [单指令挂载](#_2)

<br />

参考官网教程[rclone mount](https://rclone.org/commands/rclone_mount/)，下面以使用 `SFTP` 协议将远程服务器上的一个路径挂载到本地为例讲解。

1.   执行 `rclone config`，控制台将输出类似下面的信息：
     ``` txt
     Current remotes:
     
     Name                 Type
     ====                 ====
     myserver             sftp
     
     e) Edit existing remote
     n) New remote
     d) Delete remote
     r) Rename remote
     c) Copy remote
     s) Set configuration password
     q) Quit config
     e/n/d/r/c/s/q>
     ```

     *   `myserver` 一行是笔者先前创建的配置，读者的输出可能不同
     *   只要有一定的英语基础，配置引导还是非常简单易懂的，下面的说明将会省略很多步骤

2.   输入`n`，回车，创建新的配置。

3.   程序将提示你输入配置名，为演示方便我输入 `demo`，读者可按照自己的喜好输入。输入后回车

4.   程序将给出一张非常长的列表，形如：
     ``` txt
     Option Storage.
     Type of storage to configure.
     Choose a number from below, or type in your own value.
      1 / 1Fichier
        \ (fichier)
      2 / Akamai NetStorage
        \ (netstorage)
     ...(skip a lot of lines)...
     56 / seafile
        \ (seafile)
     Storage>
     ```

     *   该列表是 `rclone` 支持的协议
     *   任何使用列表中协议的远程储存服务都可由 `rclone` 挂载到本地硬盘
     *   我们关系的是 `45 SSH/SFTP` 协议，所以输入 `45` 回车

5.   然后按照程序提示填写相关信息

     *   在配置 `disable_hashcheck` 时一定要设置为 `true`，否则 `rclone` 的 `VFS` 文件系统将无法正常工作。后文 [VFS 文件系统](#VFS_文件系统) 将有详细说明。
     *   `ssh>` 配置项解释：默认 `rclone` 将使用内部的 SSH 库来建立连接，但内部 SSH 并没有实现所有 SSH 功能，同时如果想获得和系统 SSH 库一致的使用体验，可以使用这个配置项指导 `rclone` 使用系统 SSH 库。个人推荐使用系统 SSH 库来建立连接。平时用什么指令 SSH 到服务器，这里就填写那个指令，例如，我习惯使用 `ssh lab-server` 来连接到服务器，这个配置项就填 `ssh lab-server`
     *   `Edit advanced config?` 可直接跳过

6.   验证配置是否正确：输入指令

     ``` bash
     ./rclone.exe lsd demo:/home/
     ```

     如果能成功列出远程服务器下 `/home/` 的所有文件，说明我们的配置正确无误，rclone 能成功连接到服务器。

     如果输出内容中有类似这样的信息：

     ``` txt
     2024/02/03 13:39:34 NOTICE: demo: --sftp-ssh is in use - ignoring user/host/port from config - set in the parameters to --sftp-ssh (remove them from the config to silence this warning)
     ```

     这是因为我们配置了 `ssh>` 项，该项目将忽略先前配置的 `host` 和 `user` 项目。该警告可忽略，也可打开 rclone 配置文件删除冗余项目来消除该警告。参考 [rclone config file](https://rclone.org/commands/rclone_config_file/)，可知配置文件位于 `%appdata%/rclone/rclone.conf`。打开该文件，找到之前配置的 `demo`：

     ``` ini
     [demo]
     type = sftp
     host = myserver.com
     user = ubuntu
     disable_hashcheck = true
     ssh = ssh lab-server
     shell_type = unix
     ```

      删除 `host = `、`user = ` 两行，保存文件，然后再执行 `./rclone.exe lsd demo:/home/`，程序不在显示警告。

7.   挂载硬盘到本地
     ``` pwsh
     ./rclone mount demo:/remote/dir/ G: --vfs-cache-mode full
     ```

     *   `demo` 是配置过程中的输入的名字，读者应该替换为自己使用名字
     *   `/remote/dir/` 是远程服务器上的一个路径，必须以 `/` 结尾且是一个文件夹。`rclone` 将把该路径下所有文件挂载到本地
     *   `G:` 挂载为本地 G 盘。除了挂载成一个硬盘，也可挂载成本地的一个文件夹，将 `G:` 替换为一个路径即可，例如 `E:\temp\mount_point`。
     *   `--vfs-cache-mode full` 比较复杂，见后文分析解释



## `rclone mount` 可选选项

### rclone 格式

`rclone mount` 格式为：

```
rclone mount <remote>:<path> <mount_point> [OPTIONS]
```

*   `remote` 可以是配置文件中定义的名字，例如前文的 `demo`。也可以是独立于配置文件的一长串字符串，实现无配置文件使用单条指令挂载，详见下一章节
*   `path`、`mount_point` ：将远程文件系统的 `path` 路径挂载到本地的 `mount_point` 路径
    *   `path` 一般要求以 `/` 结尾
    *   在 Win 系统中，`mount_point` 可设置为 `*`，rclone 将自动选择一个没有被使用的盘符作为 `mount_point`
*   `OPTIONS` 一堆参数，其中最重要的是理解 VFS 文件系统



### 细枝末节的参数

*   `--volname <name>` 设置盘符的名字，否则 rclone 将给你生成一个非常丑的名字
*   `--network-mode` 挂载成 Windows 的网络硬盘而不是本地硬盘。实测不好用，挂载成网络硬盘后每次打开都会卡顿，体验不如本地硬盘



### VFS 文件系统 {: id="VFS_文件系统"}

VFS：Virtual File System，是 rclone 提供的一个文件系统兼容层，使通过网络挂载的硬盘“看起来”更像是真实的本地硬盘。

读写云存储对象不像读写本地文件那样容易，例如，本地文件可以随机读写，但许多网络存储服务只支持顺序读写，这就导致虽然确实挂载成了一个本地硬盘，但使用起来却不想本地硬盘那么方便。此时 rclone 提供 VFS，通过在本地建立缓存的方式支持随机读写等等特性，使挂载好出的硬盘易于使用。

VFS 通过缓存来提供兼容性，可通过 `--vfs-cache-mode <mode>` 设置不同缓存级别：

*   `off`：默认设置，完全不缓存。此时，

    *   同一个文件要么读、要么写，不能以 `rw` 模式打开
    *   只能顺序读、顺序写，不支持 `seek` 操作
    *   写文件中途网络出现错误，不能自动回复

    *   除上述限制之外还有其他限制，所以一般都不使用 `off` 模式

*   `minimal`：只缓存以 `rw` 模式打开的文件。此时，

    *   只有`rw` 打开的文件将缓存到本地，支持随机读写。但以 `r` 或 `w` 打开的文件仍然不支持 `seek` 指令。
    *   其他行为类似 `off` 模式，所以用的也不多

*   `writes`：读操作直接走网络，写操作缓存到本地。此时，

    *   所有文件支持随机读写
    *   些文件中途出现网络错误，`rclone` 将自动重试
    *   该模式已经能支持几乎所有对文件系统的操作

*   `full`：读、写都有缓存

    *   读取文件的缓存仅仅缓存读取的那一部分，不会缓存整个文件。
    *   使用稀疏文件来缓存，所以不适合运行在 `FAT/exFAT` 这类不支持稀疏文件的文件系统上，性能会非常非常差。但 Windows 使用的 NTFS，Linux 的 ext4 都支持稀疏文件，可以放心使用。
    *   该模式能够支持几乎所有对文件系统的操作
    *   是最推荐的模式

<br />

**在任何情况下**，我都推荐使用 `--vfs-cache-mode full` 模式。

<br />

**与 SFTP 搭配使用的诡异 bug**

但这套缓存系统和 sftp 搭配使用的时候会有诡异的 bug。具体表现为：rclone 传输文件后会使用 `md5sum` 等程序计算远程、本地同一个文件的 checksum 进行比较，保证没有任何错误发生。但在有缓存的前提下，本地文件只是下载了一部分的稀疏文件，无法计算 checksum。然后 rclone 就卡死在那了，最终导致整个资源管理器重启。网上相关资料很少，不确定是 windows 的问题还是 rclone 的问题。但解决方法很简单，在 `rclone.conf` 配置项中加入 `disable_checksum = true` 禁用 checksum 功能即可，毕竟 TCP/SSH 就非常可靠，只有 rclone 不写出 bug，几乎不会出现传输错误。我实际使用了大半年，没有任何问题。

<br />

**细粒度缓存调优**

rclone 提供了一堆与缓存设置相关的选项，这里列举一些常见选项：

*   对文件夹的缓存（缓存文件夹下有哪些文件）

    ```
    --dir-cache-time duration   Time to cache directory entries for (default 5m0s)
    --poll-interval duration    Time to wait between polling for changes. 
                                Must be smaller than dir-cache-time. Only 
                                on supported remotes. Set to 0 to disable
                                (default 1m0s)
    ```

    *   超出 `--dir-cache-time duration` 指定时间后，rclone 将从远处服务器获取最新的文件夹结构
    *   `--poll-interval duration` 比超时后再完整查询稍稍高效些，但要求协议支持。可惜的是 SFTP 协议不支持 polling。

*   对文件的缓存

    ```
    --cache-dir string                     Directory rclone will use for caching.
    --vfs-cache-mode CacheMode             Cache mode off|minimal|writes|full (default off)
    --vfs-cache-poll-interval duration     Interval to poll the cache for stale objects (default 1m0s)
    --vfs-write-back duration              Time to writeback files after last use when using cache (default 5s)
    ```

    *   `--cache-dir` 缓存文件保存位置，如果不是 C 盘要爆炸了一般不用管
    *   `--vfs-cache-mode` 前文已经分析过了
    *   `--vfs-cache-poll-interval duration` 每 `duration` 时间遍历一遍缓存表，标记陈旧的文件（需要对“缓存”的基本工作方法有了解才可理解次项）
    *   `--vfs-write-back duration` 本地有新的写入，延迟多久后再上传到远程储存服务器 

<br />

这些参数需要依据实际情况设置，下面给出 3 种典型情况的推荐设置：

1.   你不知道自己想干什么，只是想把远程硬盘挂载到本地：啥都不配置，使用默认配置

2.   远程只负责储存，所有修改发生在本地，修改的文件都不会很大，并且希望本地的修改尽快同步到远程：

     ```
     --vfs-write-back 2s
     ```

     *   `--vfs-write-back` 设置为一个非常非常小的数，这样一保存，文件就同步上去了

3.   远程会频繁修改文件，本地仅做查看，希望远程的修改尽快同步到本地：
     ```
     --dir-cache-time 30s
     --poll-interval 10s
     --vfs-cache-poll-interval 10s
     ```

     *   这些设置强迫 rclone 频繁从服务器获取最新的文件

     如果还是有些内容没能同步到本地，可尝试`Remote Control` 功能，在启动挂载时指定

     ``` pwsh
     ./rclone.exe mount --rc-addr=5572 demo:/home/ J: --vfs-cache-mode full
     ```

     然后再另一个控制台输入：

     ``` pwsh
     ./rclone.exe rc --rc-addr=127.0.0.1:5572 vfs/forget
     ```

     强制刷新缓存。

     如果使用的是 linux 系统，可通过向 rclone 进程发送信号实现同样功能：

     ``` bash
     kill -SIGHUP $(pidof rclone)
     ```

     

参考：

*   [rclone mount](https://rclone.org/commands/rclone_mount/)



## 单指令挂载

先 `rclone config` 再 `rclone mount` 还是有些过于繁文缛节了，所以这里介绍一行挂载方法。核心是使用 rcloen 提供的 [Connection strings](https://rclone.org/docs/#connection-strings) 代替 `remote` 配置。

Connection String 构造非常简单，以前文配置的 `demo` 为例，在 `rclone.conf` 文件中是这样的：

``` ini
[demo]
type = sftp
disable_hashcheck = true
ssh = ssh lab-server
shell_type = unix
```

对应的 Connection String 为：

``` txt
:sftp,ssh=ssh lab-server,disable_hashcheck=true,shell_type=unix:<path>
```

也就是说，直接运行下面的指令就可挂载远程文件：

``` pwsh
.\rclone.exe mount ^
	":sftp,ssh=ssh lab-server,disable_hashcheck=true,shell_type=unix:/path/todir/" ^
	G: ^
	--vfs-cache-mode full
```



为了追求极致的便捷，建议编写一个 `bat` 脚本：

``` bat
@echo off 
cd /d %~dp0
rclone.exe mount ^
	":sftp,ssh=ssh <host>,disable_hashcheck=true,shell_type=unix:<path>" ^
	<mount_point>  ^
	--vfs-cache-mode full ^
	--volname <vol_name>
```

注意替换 `<host>`、`<path>`、`<mount_point>`、`<vol_name>`

