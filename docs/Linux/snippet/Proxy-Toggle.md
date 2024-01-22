---
tags:
    - Linux
    - Bash
    - Proxy
create_time: 2024-01-22
update_time: 2024-01-22

# disable_comments: false  # 关闭评论区
# disable_excerpt: false   # 关闭博客摘要（不显示在首页）
---

# Proxy-Toggle

Install: 

``` bash
# in .bashrc, .profile, or .zshrc
source /path/to/this/snippet.sh
```

Usage:

``` bash
proxy-enable                         # use default proxy server
proxy-enable "http://127.0.0.1:8765" # use given proxy server

proxy-disable
```

See more to get the content of the snippet.

<!-- more -->

``` bash

#!/bin/bash

function proxy-disable() {
    echo unset proxy

    unset http_proxy
    unset https_proxy
    unset all_proxy
    unset HTTP_RPOXY
    unset HTTPS_PROXY
    unset ALL_PROXY

    rst=$(which git)
    rst=$?
    if [ "$rst" -eq "0" ]; then
        echo unset git proxy
        git config --global --unset http.proxy
        git config --global --unset https.proxy
    fi
}

function proxy-enable() {
    proxy="http://127.0.0.1:7890"

    if [ "$1" != "" ]; then
        proxy=$1
    fi

    echo set proxy to $proxy

    export http_proxy=$proxy
    export https_proxy=$proxy
    export all_proxy=$proxy
    export HTTP_RPOXY=$proxy
    export HTTPS_PROXY=$proxy
    export ALL_PROXY=$proxy

    rst=$(which git)
    rst=$?
    if [ "$rst" -eq "0" ]; then
        echo set git proxy to $proxy
        git config --global http.proxy "$proxy"
        git config --global https.proxy "$proxy"
    fi
}

```