---
tags:
    - Linux
    - Bash
create_time: 2024-01-22
update_time: 2024-01-22
---

# ln-all 创建软连接

一次性为当前文件夹下所有内容创建软连接，主要用在 NAS 管理上。

Usage: 

```
ln-all <dest>
```

在 `<dest>` 下创建软连接。

<!-- more -->

``` bash

#!/bin/bash

dest=$1
if [ -z "$dest" ]; then
    echo "Usage: ln-all <destination>"
    exit 1
fi

if [ ! -d "$dest" ]; then
    echo "Destination $dest does not exist"
    exit 1
fi

for file in *;
do
    ln -s -r "$file" "$dest/$file"
done
```

这里 `-r` 选项意为使用相对路径创建软连接。好处是在把本地路径 mount 到 docker 环境时灵活一
些，坏处是创建的软连接不能简单的使用 `mv` 移动到其他文件夹。`mv` 移动软连接并不会修改相对
软连接的连接路径，所以移动后相对路径就不对了。此时可使用 [ln-mv.sh 脚本](ln-mv.md)