---
tags:
    - Linux
    - KVM
    - VM
    - Network
create_time: 2024-03-25
update_time: 2024-03-25
---



# 虚拟机网络配置

虚拟网络结构、功能需按照需求配置，典型例子：

* NAT 模式：为 guests 局域网分配局域网 IP
    * Guest -> Internet：使用 NAT 技术依托 host 的网络连接互联网
    * Guest <- Internet：需额外在 host 上配置端口转发
    * Guest <-> Guest：可访问
    * Guest --> Host：可访问
    * Guest <-- Host：可访问
* 隔离模式：为 guests 单独搭建一套网络
    * Guest -> Internet：无
    * Guest <-> Guest：可访问
    * Guest 与 Host：无法相互访问
* 共享网卡：相当于使用交换机连接 guest 和 host 的一个网口
    * Guest -> Internet：需要 guest 自行通过宽带拨号/DHCP等手段获取 IP
* 路由模式
* 网卡直通







<!-- more -->



参考资料：

* [libvirt: Virtual Networking](https://wiki.libvirt.org/VirtualNetworking.html)
* [libvirt: Networking](https://wiki.libvirt.org/Networking.html)
* [libvirt: Network XML format](https://libvirt.org/formatnetwork.html)
* [IPv6 address - Wikipedia](https://en.wikipedia.org/wiki/IPv6_address)
* [Unique local address - Wikipedia](https://en.wikipedia.org/wiki/Unique_local_address)
* [RFC3484  Default Address Selection for IPv6](https://www.rfcreader.com/#rfc3484)



此外，本文使用大量从 [libvirt: Virtual Networking](https://wiki.libvirt.org/VirtualNetworking.html) 下载的图片。



## Virtual Network Switches

libvirt 使用名为 virtual network switch (VNS)的虚拟器件提供虚拟网络。如果读者熟悉 OSI 模型，多半下意识认为这个 “switch” 对应链路层，功能应该与一个交换机类似。但此 switch 非彼 switch，取决于具体网络配置，virtual network switch 可能工作在链路层，也可能工作在网络层。

Libvirt 将 Virtual Network Switches 表示成这个样子：

![images/Linux_host_with_only_a_virtual_network_switch.png](./typora/Linux_host_with_only_a_virtual_network_switch.png)

虽然名字中带着个 "switch"，但他的设备名却显示为 “virbr0”，其中的“br” 暗示着是一个网桥。更让人迷惑的是，VNS 可以实现 NAT，一种通常是路由器才会提供的功能，所以 VNS 多多少少也能理解成一个路由器。

严格来说，switch、bridge、router 应该是不同的东西，VNS 提供又能实现这三种设备的功能，所以最好忽略这些文绉绉的名词定义，不要过多纠结。



## NAT 模式

### 基本使用

NAT 模式是 libvirt 的默认网络模式，VNS：

* 为虚拟机分配局域网 IPv4 地址
* 对 guest 发往 Internet 的数据包实施 SNAT，为 guest 提供网络访问
* 默认阻拦 Internet 到 guest 的数据包，除非它属于从一个从 guest 发起的连接
* 允许 guest 间、guest <--> host 的相互访问



网络结构图：

![images/Host_with_a_virtual_network_switch_in_nat_mode_and_two_guests.png](./typora/Host_with_a_virtual_network_switch_in_nat_mode_and_two_guests.png)



典型配置文件例：

``` xml
<network>
  <name>net_name</name>
  <uuid>UUID</uuid>
  <forward mode='nat' />
  <bridge name='virbr0' stp='on' delay='0'/>
  <mac address='52:54:00:4e:3c:17'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254'/>
    </dhcp>
  </ip>
</network>
```



### 使 Guest 可从 Internet 访问

NAT 模式下 guest 只有局域网 IP 地址，若希望从互联网直接访问 guest，需先将数据发送到具有公网 IP 地址的 host，host 再通过端口转发将数据转发到 guest。本质上是做了一个 DNAT。

配置流程：

* 打开 Linux 的数据包转发，`sudo vim /etc/sysctl.conf`，添加一行：
  
    ```
    net.ipv4.ip_forward = 1
    ```

    然后执行 ` sysctl -p /etc/sysctl.conf` 应用更改

* 使用 `iptables` 配置 DNAT

但 iptables 的配置复杂且易错，还是使用程序自动配置为好。[libvirt: forwarding incoming connections](https://wiki.libvirt.org/Networking.html#forwarding-incoming-connections) 中提供了 3 种自动脚本，个人推荐这个 Python 项目：

* [saschpe/libvirt-hook-qemu: Libvirt hook for setting up iptables port-forwarding rules when using NAT-ed networking](https://github.com/saschpe/libvirt-hook-qemu)

该脚本将在虚拟机启动时自动启用 DNAP，在虚拟机关机时取消。比较好用



### 启用 IPv6

libvirt 默认只为 guests 分配 IPv4 地址，如要为 guests 分配 IPv6 地址，需修改网络的 xml 配置为：

``` xml
<network>
  <name>net_name</name>
  <uuid>UUID</uuid>
  <forward mode='nat' />
  <bridge name='virbr0' stp='on' delay='0'/>
  <mac address='52:54:00:4e:3c:17'/>
  <ip address='192.168.122.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254'/>
    </dhcp>
  </ip>
  <ip family='ipv6' address='fdXX:XXXX:XXXX:NNNN::1' prefix='64'>
    <dhcp>
      <range start='fdXX:XXXX:XXXX:NNNN::10' end='fdXX:XXXX:XXXX:NNNN::ff'/>
    </dhcp>
  </ip>
</network>
```

核心是添加了

``` xml
<ip family='ipv6' address='fdXX:XXXX:XXXX:NNNN::1' prefix='64'>
  <dhcp>
    <range start='fdXX:XXXX:XXXX:NNNN::10' end='fdXX:XXXX:XXXX:NNNN::ff'/>
  </dhcp>
</ip>
```

* 需要将 IP 地址中的 `X`、`N` 更改为随机的 16 进制字母
* `fdXX:XXXX:XXXX::` 属于 `fc00::/7` 地址段，是 unique local address (ULA)，可类比为 IPv4 中的局域网地址段
* `X` 构成 IPv6 中的 prefix 部分，`N` 构成 subnet ID 部分，一般没啥影响，随机一个地址即可



配置文件修改完成后，使用如下指令重启这个虚拟网络：

``` bash
sudo virsh net-destory net_name
sudo virsh net-start net_name
```



现在进入 guest，输入 `ip -c addr`，应该能看到获取到的 IPv6 地址。现在，你可以使用 IPv6 协议进行：

* 该网络下 guests 间通讯
* host 与该网络的 guests 间通讯



但 libvirt 默认关闭 IPv6 NAT，所以现在 guest 仍然无法使用 IPv6 协议访问 Internet。



### 启用 IPv6 NAT

虽然 IPv6 并不推荐使用 NAT，但也有些需要使用 IPv6 的场景，例如：

* Host 只能通过 IPv6 上网
* 你是中国大陆用户：
    * IPv6 网络环境比 IPv4 网络环境更加纯净，网速更快、没有那么拥挤、网络审查较少……
    * 网络运营商为你的 Host 提供的 IPv4 是局域网 IPv4，但为你提供公网 IPv6 地址，并且你希望能直接从互联网访问 guest
* 你正在使用中国教育网（CERNET）：为了鼓励 IPv6 发展，大部分高校并不收取 IPv6 流量费用，你希望顺应国家政策使用 IPv6 <span class="heimu">狠狠地薅国家羊毛</span>



可更具下属教程开启 IPv6 NAT：

* 在 Host 开启 IPv6 转发

    ``` bash
    # sudo vim /etc/sysctl.conf
    # add this line
    net.ipv6.conf.all.forwarding=1
    ```

* 将 VNS 的配置修改为：

    ``` xml
    <network>
    ...other configurations...
    <forward mode='nat'>
      <nat ipv6='yes'>
        <port start='50000' end='65535'/>
      </nat>
    </forward>
    </network>
    ```



现在你的 guest 能正常使用 IPv6 访问 Internet 了，但有个小瑕疵：

* 如果 Linux 系统既有 IPv4 地址又有公网 IPv6 地址，系统优先使用 IPv6 进行通讯
* 但因为分配给 guests 的是 `fc00::/8` 的 UCL 地址，系统会优先使用 IPv4 进行通讯

作者还没能解决该问题，我将一些可能对理解地址选择有帮助的连接列举如下，若读者有解决方法，可在评论区留言：

* [libvirt: Network XML format - IPv6 NAT](https://libvirt.org/formatnetwork.html#ipv6-nat-based-network)

* [RFC3484  Default Address Selection for IPv6](https://www.rfcreader.com/#rfc3484)

* ULA 的混乱历史：[Unique local address - Wikipedia](https://en.wikipedia.org/wiki/Unique_local_address)

* 可能的解决方法：修改 `/etc/gai.conf`，但我瞎改了一波没啥效果

* 如何得知系统的偏好：

    使用指令：

    ``` bash
    getent ahosts ident.me
    ```

    系统会按照该指令列出的顺序建立连接。

    如果是 IPv6 地址在前，说明系统偏好 IPv6，例如：

    ``` 
    2a01:4f8:c0c:bd0a::1 STREAM ident.me
    2a01:4f8:c0c:bd0a::1 DGRAM
    2a01:4f8:c0c:bd0a::1 RAW
    49.12.234.183   STREAM
    49.12.234.183   DGRAM
    49.12.234.183   RAW
    ```

    反之如果 IPv4 地址在前，说明系统偏好 IPv4，例如：

    ```
    49.12.234.183   STREAM ident.me
    49.12.234.183   DGRAM
    49.12.234.183   RAW
    2a01:4f8:c0c:bd0a::1 STREAM
    2a01:4f8:c0c:bd0a::1 DGRAM
    2a01:4f8:c0c:bd0a::1 RAW
    ```

  

### 配置 IPv6 DNAT

与 IPv4 不同，IPv6 暂时没有现成的 DNAT 自动配置脚本。管理员可通过如下指令配置 DNAT：

``` bash
GUEST_IP=xxxxxxxx
GUEST_PORT=22
VNS_DEV=virbr0
HOST_PORT=4023

sudo ip6tables -I FORWARD -o $VNS_DEV -p tcp -d $GUEST_IP --dport $GUEST_PORT -j ACCEPT
sudo ip6tables -t nat -I PREROUTING -p tcp --dport $HOST_PORT -j DNAT --to "[$GUEST_IP]:$GUEST_PORT"
```





## 其他内容

等待施工....



