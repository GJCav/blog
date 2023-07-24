---
create_time: 2023-07-24
update_time: 2023-07-24
tags:
    - linux
    - alias
---

# alias 别名

```
alias [name[=value]] # 设置别名，=后不能有空格，可用单引号包括value，双引号也可
alias                # 查看别名
alias [name]         # 单独查看别名
unalias [name]       # 取消别名
```

<!-- more -->

## 单双引号差别

如果value中含有`$PWD`等变量，双引号会在设置时替换`$PWD`，单引号不会，所以**推荐单引号**

## 永久激活别名

在`$HOME`目录下`.bashrc`文件中添加别名即可。

## shell 脚本中不能执行别名？

在 Shell 脚本中，alias 别名功能默认是关闭的，使用如下模板即可：

```
#!/bin/bash --login
#上面一句使用login shell方式执行子shell，这样就会读取profile和rc文件，加载别名
shopt expand_aliases # 打开脚本的alias扩展

#...
```