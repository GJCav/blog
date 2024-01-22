---
tags:
    - Linux
    - Bash
create_time: 2024-01-22
update_time: 2024-01-22
---

# ln-mv 移动软连接

``` text
move links to another directory and maintain the link
if the file is not a link, do nothing

usage: ln-mv <links...> <destination>
example: ln-mv *.txt ~/Documents

```

<!-- more -->

``` bash
#!/bin/bash

# move links to another directory and maintain the link
# if the file is not a link, do nothing
#
# usage: ln-mv <links...> <destination>
# example: ln-mv *.txt ~/Documents

dest=${@: -1}
if [ -z "$dest" ]; then
    echo "Usage: ln-mv <links...> <destination>"
    exit 1
fi

if [ ! -d "$dest" ]; then
    echo "Destination $dest does not exist"
    exit 1
fi

for file in "${@:1:$#-1}"; do
    name=$(basename "$file")
    if [[ -L "$file" ]]; then
        # move the link and maintain the link
        realpath=$(readlink --canonicalize  "$file")
        ln -s -r "$realpath" "$dest/$name"
    else
        echo "$file is not a link. ignore"
    fi
done
```