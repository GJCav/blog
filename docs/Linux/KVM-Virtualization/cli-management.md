---
tags:
    - Linux
    - KVM
    - QEMU
create_time: 2024-02-03
update_time: 2024-02-03
---

# 命令行管理虚拟机

在宿主机上，除了使用 `virt-manager` 管理虚拟机，还可使用命令行工具 `virsh` 及其配套指令管理虚拟机。主要使用指令有：

*   `virsh`：强大的虚拟机管理终端
*   `virt-install`：用于创建虚拟机



<!-- more -->



## 入门

在宿主机终端中输入 

``` bash
virsh
```

即可进入虚拟机管理终端，输入 `help` 然后回车，能看到一堆帮助信息

```
❯ virsh help
Grouped commands:

 Domain Management (help keyword 'domain'):
    attach-device                  attach device from an XML file
    attach-disk                    attach disk device
    attach-interface               attach network interface
    autostart                      autostart a domain
    blkdeviotune                   Set or query a block device I/O tuning parameters.
    blkiotune                      Get or set blkio parameters
    blockcommit                    Start a block commit operation.
    
...(skip a lot of lines)...
```

说明你成功进入了 libvirt 的管理控制台。别被这几十行的命令吓住，没人要求你全部记忆下来。下面用一个简单的例子介绍 `virsh` 使用方法。



### 列出虚拟机

可以使用 

``` bash
virsh list --all
```

列出所有虚拟机。不过这有个小坑，如果之前您创建虚拟机时用的指令带上了 `sudo`，那大概率看不到先前创建的虚拟机。此时可尝试：

``` bash
sudo virsh list --all
```

现在应该能看到先前创建的虚拟机，这是因为：

*   libvirtd 可以有多个实例，分割管理不同用户的虚拟机，习惯上使用 URL 来辨别这些实例
    *   `qemu:///system` 指宿主机上 root 用户的实例，libvirtd 保证开机后自动运行该实例
    *   `qemu:///session` 指这台电脑上当前登录用户的实例，只有当用户运行 `virsh` 之类的指令时，才启动该实例
*   不同实例之间是互不可见的，即 session 实例的虚拟机 system 实例创建的虚拟机
*   `virsh` 默认连接 `qemu:///session`，所以看不到 `qemu:///system` 的虚拟机
*   `virt-manager` 默认链接 `qemu:///system`，所以先前用`virt-manager`指令创建的虚拟机都在 `system` 实例中
*   `sudo virsh` 默认连接 `qemu:///system`，这样才看得到之前创建的虚拟机
*   在所有情况下，都推荐使用 `qemu:///system` 实例，所以后文所有指令都带有 `sudo`



### 如何查询帮助文档

`virsh help` 会列出所有可用指令，但这些指令是在是太多了。为了方便阅读，`virsh` 将这些指令归类，可用：

``` bash
virsh help <keyword>
```

查询某一类别的指令，例如：

``` bash
virsh help volume
```

将查询所有和分区管理相关的指令。



找到某个指令，例如 `vol-list`，可用

``` bash
sudo virsh vol-list --help
```

获得更加详细的解释。



最后，官方文档永远是你忠实的朋友：

* [libvirt: Documentation](https://libvirt.org/docs.html)
* [Virtualization Deployment and Administration Guide | Red Hat ](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/index)



## 虚拟机管理

帮助文档关键词：

``` bash
virsh help domain
```



### “电源”操作

``` bash
sudo virsh start <domain>
sudo virsh shutdown <domain>   # gracefully shutdown the domain

sudo virsh reboot <domain>     # run a reboot command in the domain
sudo virsh reset <domain>      # shutdown the domain as if by power button

sudo virsh suspend <domain>
sudo virsh resume <domain>
```

* 回忆：libvirt 把一个虚拟机称为一个 domain
* 这里的 domain 就是 `virsh list` 列出的名字



### 删除虚拟机

删除虚拟机：

``` bash
sudo virsh undefine <domain>
```

不过该指令不会连带删除虚拟机使用的储存空间，虽然可以使用 `--remove-all-storage`，但不太安全，所以推荐手动管理。



### 创建虚拟机

因为只能使用命令行，和 virt-manager 相比创建虚拟机的过程会复杂得多，针对不同操作系统又有不同的指令，这里仅列举一些案例，方便读者参考。



#### 创建 Ubuntu 22 Server 虚拟机

参考下列指令

``` bash
sudo virt-install \
    --name="ub22svr" \
    --vcpus sockets=1,cores=2,threads=2 \
    --memory 8192 \
    --disk size=50 \
    --graphics none \
    --autoconsole text \
    --osinfo ubuntu22.04 \
    --location <path/to/iso/file>,kernel=casper/vmlinuz,initrd=casper/initrd \
    -x "console=ttyS0" \
    --network default
```

解释：

* `--vcpus` 配置 CPU 拓扑结构，插入 1 个 CPU，每个 CPU 2 核心，每个核心 2 线程
* `--mempry` 8GB内存
* `--disk size=50` 新建50GB的虚拟硬盘给虚拟机使用
* `--graphics none` 无图形界面
* `--autoconsole text` 使用 `virsh console` 的终端与虚拟机交互
* `--location`
    * 指定镜像文件路径，安装时需要从这个镜像中启动系统。但不同系统的镜像文件结构不同，`virt-install` 也不知道到底把镜像中的哪个文件作为内核，把哪个文件作为文件根目录，只能假定这两个文件在 ISO 镜像中的位置。但显然对于 Ubuntu 的镜像来说，假定是错误的，所以得人工指定
    * `kernel=casper/vmlinuz` 指定启动时使用的内核
    * `initrd=casper/initrd` 启动时需要用到的临时文件系统
    * 这一坨玩意有些深奥，需要对 Linux 的启动过程有深入了解才能完全理解。我们只想创建一个虚拟机，大可先忽略这些细节，记住这一套设置即可
* `-x "console=ttyS0"` 让内核把所有输出重定向到第 ttyS0。
    * `tty`：最初指 teletypewriter，unix 类操作系统指 terminal device，例如一个物理终端、GUI操作系统模拟的终端或者一个串口
    * `S`：指 serial，即串口通信
    * `0`：第一个 tty
    * 必须配置该选项，才能通过 `virsh console` 连接上该虚拟机

运行后会自动进入 `virsh console` 连接到虚拟机，按照输出提示完成安装。

但该过程仍然是需要人来交互的，并不是完完全全的自动安装。



#### Ubuntu 22 Live Server 虚拟机全自动创建

主要使用 ubuntu 官方的 [Automated Server installation](https://ubuntu.com/server/docs/install/autoinstall) 技术和配套的 *preseed* 文件完成自动化。

相关配置还在学习中，在这留个坑。





## 储存空间管理

帮助文档关键词：

``` bash
virsh help pool
virsh help volume
```



**列出所有储存池**：

``` bash
virsh pool-list --all
```

输出例：

```
 Name      State    Autostart
-------------------------------
 default   active   yes
 osimg-1   active   yes
```



**列出某个储存池的所有分区**：

``` bash
virsh vol-list --pool <pool>
```

返回例：

``` 
 Name              Path
------------------------------------------------------------
 ub20-dsk.qcow2    /var/lib/libvirt/images/ub20-dsk.qcow2
 ub_dsk_22.qcow2   /var/lib/libvirt/images/ub_dsk_22.qcow2
```



**删除某个储存池的某个分区**

``` bash
virsh vol-delete <vol> --pool <pool>
```



**删除某个储存池**

1. 停止该储存池：

    ``` bash
    virsh pool-destroy <pool>
    ```

2. (可选)删除储存池所在文件夹

    ``` bash
    virsh pool-delete <pool>
    ```

3. 从储存池列表中移除该储存池

    ``` bash
    virsh pool-undefine <pool>
    ```

非常的繁文缛节，但也没啥办法