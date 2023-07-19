# pytest-cov 代码覆盖率测试

官方文档：

[Welcome to pytest-cov's documentation! - pytest-cov 3.0.0 documentation](https://pytest-cov.readthedocs.io/en/latest/index.html)

## 最小示例

 基本示例：`myproj` 是被测项目，tests是测试脚本文件夹。

```bash
pytest --cov=myproj tests/
```

会使用`test` 文件夹下的所有`pytest` 测试脚本测试`myproj` 下的测试覆盖率，对`myproj`子文件夹下的代码，如果被`import`过了，会显示在覆盖率测试中，如果完全没有被`myproj` 文件夹下的文件`import`到，那直接不显示。 

**其他常用参数：**

- `--cov-report term-missing`：输出未覆盖的行号
- `--cov-report html:cov_html`：输出html报告到`cov_html` 文件夹下
- 注：这些参数可重复、叠加给出

## 使用配置文件

官方配置文件：

[Configuration reference - Coverage.py 6.3.2 documentation](https://coverage.readthedocs.io/en/latest/config.html)

在测试脚本同目录下创建`.coveragerc`文件：

```
[run]
# 被测代码所在文件夹
source = ../
# 忽略对当前文件夹下Python文件的覆盖率测试
omit = ./*
# 分支覆盖率统计
branch = on
# 被测代码使用的多线程库，默认是thread
# concurrency = greelet
```

然后使用`pytest --cov` 即可运行测试