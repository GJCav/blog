---
create_time: 2023-07-24
update_time: 2023-07-24
tags:
    - linux
    - lsof
    - cli
---

# lsof 指北

``` bash
lsof -i 6tcp -s :LISTEN -n -P
# list all ipv6 TCP connections that are listening 
#   -n no DNS resolving
#   -P no port->service name resolving

sudo lsof -a -u <user> -i tcp
# list all TCP connections that are opened by <user>
#   -a          logical AND between all options. (default is logical OR)
#   -i <user>   filter by <user>. <user> is a list of names or uid separated by ','
#   use `sudo` to access other users' information

lsof -p <pid>
# list all files opened by <pid>
#   <pid> is a list of pids, separated by ','
```

<!-- more -->


完整文档：[lsof(8) - Linux manual page](https://man7.org/linux/man-pages/man8/lsof.8.html)

但内容实在是太复杂了，所以把其中一些用法单独列出

## 基本概念

- lsof 后面接上的是各种筛选选项
- 每个筛选条件之间的关系默认是并集，说实话不太好用
- 所以可以加上 `-a` 把筛选条件间的条件改为交集
- 注意，有些选项使用同一个字母但不同大小写，其含义多半完全不同

筛选选项：

- `-u s` 列出列表 s 中用户打开的文件
    
    > 注意：`-U` 是列出 unix socket 连接
    > 
- `-c xxx` 筛选 COMMAND 前缀为 xxx 的被打开文件
- `+d dir` 筛选出打开文件夹 dir 和 dir 子文件的实例，不递归、不follow links、mount
    - 若要 follow link、mount 进一步跳转，使用 `-x`
- `+D dir` 同`+d` 但递归筛出以 dir 为根的所有实例，不递归、不处理 link、mount
- `-g grp_list` ：按用户组筛选
- `-p pid_list`：按照 PID 筛选

其他选项：

- `-l`：不作 uid 到用户名的转换
- `+L`：显示实例的 link count
- `-r [sec]` ：每隔 sec 秒输出一次

指定输出格式：`-F field_list` 

- 例如：`-F pcfn0` 显示 PID、command name、fd、file name 并且每个 field 用 NUL 结束
- 详细见：OUTPUT FOR OTHER PROGRAMS

## 网络相关

可以直接`man lsof` 然后搜索 `internet` 能够快速定位

网络相关的文件包括：TCP、UDP 连接

基本格式：

```bash
lsof -i [46][protocol][@hostname|hostaddr][:service|port]
```

默认之列出当前用户的连接，使用 sudo 以读取所有 TCP

可以附加其他选项：

- `-n` 不做 DNS 解析
- `-P` 不做端口号 —> 服务名称的解析
- `-s proto:state` 筛选TCP或UDP的状态，state 例如：LISTEN

例如：

能列出 TCP 连接

- `lsof -i 4tcp` 列出当前用户所有 TCP 链接
- `sudo lsof -a -u user1 -i` 列出 user1 使用的所有网络链接

## 管道

筛选选项：`-E` 

管道包含：pipe 和 UNIX socket