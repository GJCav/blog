---
tags:
    - Linux
    - Bash
    - Proxy
create_time: 2024-01-22
update_time: 2024-01-22
---


# N 卡开启持久模式

N 卡默认电源管理策略会在显卡长时间不使用后“休眠”显卡，但这一休眠很有可能就启动不起来了，或者
能手动启动，但会导致很多程序莫名奇妙崩溃，甚至导致 `nvidia-smi` 无法响应，输出一些神奇的错误
信息。

另一方面，如果是在配置家庭影院，为了实时转码自然希望 N 卡随时在线，所以需要开启 N 卡 **持久模式**。

启用方法：

``` bash
sudo systemctl edit nvidia-persistenced.service
```

输入：

``` 
[Service]
ExecStart=
ExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --persistence-mode --verbose

```

执行 
``` bash
nvidia-smi -q
```
检查 `Persistence Mode` 行是否为 `Enabled`。

<!-- more -->

## 解释

`systemctl edit nvidia-persistenced.service` 会在 `/etc/systemd/system` 创建文件夹 `nvidia-persistenced.service.d`
和 `override.conf` 文件覆盖 `/lib/systemd/system/nvidia-persistenced.service` 中的配置信息。

唯一的修改是把 `--no-persistence-mode` 改成了 `--persistence-mode`。

参考：

* [systemd 配置覆盖](https://askubuntu.com/questions/659267/how-do-i-override-or-configure-systemd-services)
* [Stackoverflow 上关于 N 卡持久化的回答](https://askubuntu.com/questions/1400122/how-to-enable-nvidia-persistence-mode-on-boot-for-ubuntu-20-04-server)
* [N 卡官方说明](https://docs.nvidia.com/deploy/driver-persistence/index.html#security)