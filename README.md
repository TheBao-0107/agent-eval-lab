# Coding Agent评测台：第1周实战包

## 你到底要做什么

假设你已经拿到了6次Coding任务的评测结果，原来需要人工数通过了几题。
你要写一个小程序，自动统计结果。第一周不调用模型、不接公司环境、不学习Agent框架。
这些记录是练习用的合成数据，不代表真实模型表现。

输入在tasks.py，输出由你编写的main.py打印。这周只需要Python标准库。
提供的数据和自检工具可以直接用；stats.py故意留有TODO，不是完整答案。

## 先把项目打开

1. 解压ZIP。在VS Code中选择“文件→打开文件夹”，选中包含本README和main.py的agent-eval-lab文件夹。
2. 选择“终端→新建终端”。下面的所有命令都在这个文件夹内运行。
3. 输入`python --version`。如果找不到python，试`py --version`；如果py可用，将下文命令中的python统一换成py。
4. 两个命令都不可用时，先安装Python 3并重新打开终端。这是环境问题，不需要改业务代码。
5. 输入`python main.py`，应看到`agent-eval-lab ready`。

先跑通系统Python即可，虚拟环境可以第3周整理依赖时再加。

## 六条输入分别表示什么

| id | status | duration_ms |
|---|---|---:|
| T001 | pass | 120 |
| T002 | fail | 200 |
| T003 | pass | 80 |
| T004 | error | 500 |
| T005 | pass | 100 |
| T006 | fail | 300 |

- id：任务唯一编号。
- pass：候选实现通过验收测试。
- fail：程序已跑完，但答案没有通过验收。
- error：运行过程出错，无法正常完成验收。
- duration_ms：该记录的耗时，单位毫秒。第一周用于输入校验，第4周再统计总耗时。

本练习成功率口径为passed / total，error也计入total，并单独列出数量。
空列表没有可算的成功率，返回None、显示n/a，不伪装成0%。

## 每天照着做

### 第1天：打开、运行、理解数据

20分钟确认Python和编辑器；60分钟运行main.py并逐行看tasks.py；余下时间熟悉终端、保存和再次运行。

只需运行`python main.py`看到`agent-eval-lab ready`。
在Excel当天J列填“main.py运行成功，输出agent-eval-lab ready”。
不会Git可以暂时不建远程仓库，先把本地文件保存好。

### 第2天：遍历六条记录

修改main.py：导入TASKS，先打印`len(TASKS)`，然后用for循环逐条打印id和status。
不要修改tasks.py里的6条原始记录。

运行`python main.py`，第一行应为6，后面依次出现T001 pass、T002 fail、T003 pass、T004 error、T005 pass、T006 fail。
再用纸笔或注释写出计数3/2/1。这一天只练列表、字典取值和for循环。

### 第3天：写统计函数

打开stats.py，先只处理正常输入。函数签名保持`summarize(tasks)`。
遍历输入，根据status增加passed、failed或errors；total是输入条数。
把计数和success_rate放进字典返回，不要在函数内部只打印结果。

然后修改main.py，导入summarize，调用它并逐行打印。运行`python main.py`的目标输出为：

```text
total: 6
passed: 3
failed: 2
errors: 1
success_rate: 50.0%
```

保存真实运行结果：`python main.py > reports/w01_summary.txt`。
注意函数内返回比例0.5；main.py负责把0.5格式化为50.0%。

### 第4天：补空输入和坏数据

继续修改stats.py，而不是另写一个统计工具。

1. tasks为空列表时，四个计数都返回0，success_rate返回None。
2. 每条记录都需要id、status、duration_ms；id必须为非空字符串且不重复。
3. status只允许pass/fail/error。
4. duration_ms是非负数字，不接受字符串、布尔值和None。
5. 不合格输入抛出ValueError，消息中写清字段或原因；不要悄悄跳过记录，也不要修改输入。

可以新建scratch.py，分别调用`summarize([])`和一条错误输入观察结果。
例如`{"id":"X","status":"unknown","duration_ms":1}`应报ValueError。
遇到失败先查是哪条输入触发，不必一次修完所有问题。

### 第5天：运行8项自检，独立解释

运行`python check_week1.py`。目标是末尾出现`Ran 8 tests`和`OK`。
失败时看test名称回到stats.py修复，不要修改验收工具来让测试变绿。

保存结果：`python check_week1.py > reports/w01_checks.txt 2>&1`。
然后不看AI答案，解释：为什么error算进分母？为什么空输入是None？为什么返回字典而不是只打印？
测试不是万能证明，还要手动试一次缺id，并确认错误消息可读。

### 第6天：用60分钟验收

重新运行main.py和check_week1.py，核对输出并填写docs/w01_review.md。
将代码、两份运行结果和复盘文档保存在同一项目目录。
在Excel“每周计划”的M列填项目目录、结果文件路径和自检结论，再按实际情况选择验收状态。
没有完成就写具体卡点，下周先补这一项；不要直接勾“已达成”。

### 第7天：休息

不安排新内容，不要求补课。

## 第1周最后交什么

- 你完成的main.py与stats.py。
- 原始数据tasks.py及未被改动的check_week1.py。
- reports/w01_summary.txt：实际运行的6/3/2/1、50.0%结果。
- reports/w01_checks.txt：实际运行的8项自检结果。
- docs/w01_review.md：真实卡点和下一步。

“交付”指把这些内容保存到自己的项目里，并在Excel填位置或Git提交链接。
不需要交给公司，也不要求第一周发布网站、部署服务器或写复杂报告。

## 卡住时如何用AI

可以发：“我正在实现summarize(tasks)，这是输入、预期结果、当前代码和完整报错。请先指出最小问题，给提示，不要直接重写整个项目。”
得到帮助后自己修改、运行验证，并在复盘里说清楚哪部分用了辅助。

## 后面怎么接着做

- 第2周：把同样6条输入换成data/tasks.json，输出JSON和CSV文件。
- 第3周：保留main.py入口，拆出读取/校验模块，加入--input与--output参数。
- 第4周：交付v0.1，新增总耗时统计，再查看3份JD校准后续方向。
- 第5—8周：给同一个工具加自动化测试、模拟HTTP调用、SQLite。
- 第9—20周：逐步变成真正的批量评测执行器，保存结果并做对照实验。
- 第21—24周：写一个小型代码修复Agent，让评测台评测它。
- 第25—36周：根据真实反馈补不足、整理作品、持续投递。

Excel“项目地图”中的后续命令是你在对应周实现后的目标接口。
这个启动包只提供第1周骨架与第2周数据，不代表后续所有模块已经完成。

## 按需查资料

- 列表与字典：https://docs.python.org/zh-cn/3/tutorial/datastructures.html
- for、if与函数：https://docs.python.org/zh-cn/3/tutorial/controlflow.html
- 第2周JSON：https://docs.python.org/zh-cn/3/library/json.html

先找到当前练习需要的小节，再回代码验证，不需要先读完整本教程。
