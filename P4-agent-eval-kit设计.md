# P4 · agent-eval-kit 设计文档（v0.1）

> 执行窗口：第 7–8 月｜8 周｜这是你全年**最值钱的交付物**
> 本文只是设计与计划，不含代码。代码从 W1 开始写。

---

## 0. 一句话定位

**为多轮、长任务的 Agent 提供 checkpoint 级、可复现、可进 CI 的评测工具。**

注意这个定位的边界：它不是"又一个 prompt 回归工具"，也不是"又一个通用 eval 框架"。它只解决一个问题——**当 Agent 要跑 20 轮、调用 30 次工具、改 15 个文件时，你怎么知道它到底好在哪、差在哪、贵不贵。**

---

## 1. 为什么这个项目值得做（也是面试叙事）

| 维度 | 说明 |
|---|---|
| **你的独特输入** | 你每天在做的就是"多轮 + checkpoint + 扣分"。市面上的评测工具作者大多没做过这件事 |
| **市场空白** | promptfoo 偏 prompt/单轮回归；inspect_ai 很强但学习曲线陡、偏学术；Langfuse 偏观测不负责评分。**"多轮任务的轨迹级评测 + 成本"这一格是空的** |
| **门槛合适** | 一个人 8 周能做出可用版本，不需要 GPU，不需要数据 |
| **可讲故事** | 面试时能拿出数字：3 个模型 × 20 个任务 × 3 次重复，成功率、pass@k、每成功任务成本 |
| **长期价值** | 它是你后续所有项目的底座——P5 的鸿蒙 Agent 也能用它来测 |

**不做什么，比做什么更重要：**
- 不做 Web UI（最多一个静态 HTML 报告）
- 不做 SaaS / 多租户 / 权限
- 不做分布式调度
- 不自动生成任务（任务由人写，这是 v0.1 的核心假设）
- 不支持鸿蒙（放 v0.3，见第 12 节）

---

## 2. 目标用户与使用场景

**用户画像**：一个要选模型 / 迭代提示词 / 对比 Agent 框架的工程师。

**四个典型场景（每个都要能一句话说清）：**

1. **模型选型**："DeepSeek 和 Qwen 在我们这 20 个任务上，谁是性价比最高的？"
2. **提示词回归**："我改了系统提示词，有没有把原本能过的任务搞挂？"
3. **框架对比**："同一批任务，LangGraph 和自研 harness 的成功率差多少？"
4. **模型升级验收**："新版本模型上线前，跑一遍基线，掉分就拦。"

---

## 3. 核心抽象（只有 4 个对象）

| 对象 | 职责 | 关键属性 |
|---|---|---|
| **Task** | 一个可评测的完整任务 | 初始指令、环境、工具集、检查点、预算、种子 |
| **Environment** | 任务运行的隔离环境 | 镜像（固定 digest）、工作目录、setup 命令、网络开关 |
| **Agent** | 被测对象，只实现一个最小协议 | `step(messages, tools) -> 动作`（工具调用或终止） |
| **Checkpoint** | 一条可判定的断言 | 时机（第 N 轮 / 事件 / 终态）、类型、参数、权重、是否必需 |

**Run Record**（不是对象，是产物）：一次运行 = 任务版本 + Agent 配置 + 模型版本 + 温度 + 种子 + 容器 digest + 全量 trace + 每个检查点的证据。

> 设计原则：**Agent 与 harness 解耦**。被测 Agent 可以是你的代码、可以是 OpenAI 兼容 API、可以是一个 CLI。harness 只负责喂消息、执行工具、记录、判定。

---

## 4. 数据流

```
task.yaml ──┐
            ├─→ Runner ─→ Sandbox(容器) ─→ 多轮循环 ─→ trace.jsonl
agent.yaml ─┘                    │                        │
                                 ↓                        ↓
                          工具执行/文件变更           Checker 判定
                                                          │
                                                          ↓
                                                    Score → SQLite
                                                          │
                                                          ↓
                                              Markdown / HTML 报告
```

---

## 5. 技术选型

| 层 | 选择 | 为什么 | 备选 |
|---|---|---|---|
| 语言 | **Python 3.12** | 你的主线语言；生态最全 | Node（不推荐，生态分叉） |
| 包管理 | **uv** | 快、锁文件干净、CI 友好 | poetry |
| 数据模型 | **Pydantic v2** | 任务 YAML 的 schema 校验与错误提示是核心竞争力 | dataclass + jsonschema |
| CLI | **Typer** | 三行出子命令，`--help` 自带 | argparse |
| 沙箱 | **Docker（官方 SDK + subprocess 兜底）** | 隔离 + 可复现是评测的生命线 | testcontainers（在其上层） |
| 存储 | **SQLite + JSONL** | 零运维；JSONL 存 trace，SQLite 存查询用的索引 | DuckDB |
| 报告 | **Jinja2 → 静态 HTML** + Markdown | 面试时能发链接 | Streamlit（太重） |
| 模型调用 | **openai SDK + `base_url` 覆盖** | 一套代码通吃 DeepSeek / 智谱 / 通义 / Anthropic 兼容网关 | LiteLLM（多 provider 时再引入） |
| 终端输出 | **rich** | 进度、表格、富文本 | — |
| 测试 | **pytest** | 用 mock agent 测 harness 本身 | — |
| 静态检查 | **ruff + pyright** | 一个人维护代码，靠工具兜底 | mypy |
| CI | **GitHub Actions** | 跑 mock 模式的端到端自测（30 秒内） | — |
| 可观测（可选） | Langfuse exporter | v0.2 再加，不阻塞主线 | OTel |

**明确不用：**
- **LangChain / LangGraph**：作为被测 Agent 可以用，但 harness 本身**不能用**。评测工具需要完全掌控上下文、循环和预算，框架会把细节藏起来——而细节恰恰是你要测的东西。
- **直接 fork inspect_ai**：它的抽象很强，但你会被它的任务模型绑住。正确做法是**读它的设计，自己实现一遍更小的**。
- 任何 ORM（SQLModel/SQLAlchemy）：SQLite 直接写，省掉一层。

---

## 6. 七个关键设计决策（这部分定了项目的档次）

### 6.1 任务即数据，不是代码
任务必须是一个 YAML 文件，人能读、能 diff、能 review。检查逻辑写在 Checker 里，不写进任务文件。**否则任务一多就变成一团 Python 脚本。**

### 6.2 环境不可变
镜像必须**固定 digest**（`@sha256:...`），不用 `latest`。每次运行记录 digest。
否则同一个任务在不同时间跑出不同结果，你会分不清是模型变强了还是依赖变了。

### 6.3 检查点分层
这是你和市面工具的**核心差异**。检查点分四层：

| 层 | 例子 | 作用 |
|---|---|---|
| **过程检查**（turn N 时判定） | 第 3 轮是否先复现了 bug | 测"方法论"而非"结果" |
| **终态检查** | 测试是否通过、文件是否存在 | 测"结果" |
| **轨迹检查** | 工具调用次数、无效调用、重复动作、上下文溢出 | 测"效率与可靠性" |
| **回归检查** | 原有测试是否仍通过、有没有改测试 | 测"破坏性" |

只有终态检查的叫"判分器"，四层都有的才叫"评测"。

### 6.4 评分：权重 + 必需项闸门 + 重复采样
- 单任务分 = Σ(权重 × 通过) / Σ权重
- **必需项（required）失败 → 该任务直接 0**，防止"作弊式部分得分"
- 每个任务跑 3 个种子，报 **pass@k** 与方差
- 报告里必须同时出现**成功率**和**每成功任务成本**

### 6.5 可复现
三件事保证可复现：容器 digest、模型版本字符串（不是"gpt-4 系列"这种）、确定的种子与温度。
再加一条：**mock agent**——一个按脚本回放动作的假模型，用来在 CI 里测 harness 本身（不花钱、30 秒跑完）。

### 6.6 预算硬上限
每个任务必须设 `max_turns / max_tokens / max_seconds / max_cost`，超了立即终止并记为"预算耗尽失败"。
这条不做，你会在调试期烧掉几百块。

### 6.7 证据留存
每个检查点判定失败时，必须能点开看到**证据**：哪一行日志、哪一个 diff、哪一轮的模型输出。
**"不可解释的失败分"没人信，包括你自己。**

---

## 7. 目录结构

```
agent-eval-kit/
├── README.md                  # 30 秒说清是什么、怎么跑、对比表
├── pyproject.toml
├── Makefile                   # make test / make eval / make report
├── src/agent_eval/
│   ├── cli.py                 # run / list / report / validate
│   ├── schema/                # Task / Agent / Checkpoint / Run 的 Pydantic 模型
│   ├── runner/
│   │   ├── harness.py         # 多轮循环主逻辑
│   │   ├── context.py         # 上下文策略：全量 / 滑窗 / 摘要
│   │   ├── budget.py          # token / 时间 / 费用上限
│   │   └── sandbox.py         # 容器生命周期、文件快照、diff
│   ├── agent/
│   │   ├── base.py            # Protocol 定义
│   │   ├── openai_compat.py   # 适配器
│   │   └── mock.py            # 回放脚本的假模型（CI 用）
│   ├── tools/                 # read_file / write_file / list_dir / run_shell / search
│   ├── checks/                # 各类型 Checker，统一接口 check(ctx) -> Result
│   ├── judge/                 # rubrics、采样、与人工标注的一致性计算
│   ├── store/                 # sqlite.py / jsonl.py
│   └── report/                # markdown.py / html.py
├── tasks/
│   ├── _template/             # 复制即用的任务模板
│   ├── coding/                # v0.1：4 个
│   └── tool_use/              # v0.1：1 个
├── rubrics/                   # judge 用的评分细则
├── docker/
│   ├── base-python/Dockerfile
│   └── base-node/Dockerfile
├── tests/                     # harness 自身单测（全部走 mock agent）
└── docs/
    ├── task-spec.md           # 任务怎么写
    ├── scoring.md             # 分数怎么算
    └── adding-a-task.md       # 30 分钟新增一个任务
```

**为什么这样分层：** `checks/` 与 `tools/` 是唯一会频繁改动的地方，其余模块尽量冻结。发布后让用户写任务只需要碰 `tasks/` 和 `rubrics/`。

---

## 8. 任务格式规范（v0.1）

这是一个完整的、可直接照抄改写的任务文件：

```yaml
id: py-csv-off-by-one
version: 1
category: coding              # coding | tool_use | long_context | regression
difficulty: 2                 # 1–5
tags: [python, bugfix, multi-file]

env:
  image: ghcr.io/agent-eval/python:3.12@sha256:REPLACE_WITH_DIGEST
  workdir: /workspace/repo
  setup:
    - pip install -e . --no-deps
  network: none               # none | restricted | full

task:
  initial_prompt: |
    /workspace/repo 里的 CSV 解析器在行尾为 \r\n 时会多解析出一列空值。
    请修复，不要修改 tests/ 下的任何文件，也不要修改已有测试断言。
  max_turns: 20

agent:
  tools: [read_file, write_file, list_dir, run_shell, search]
  context_policy: sliding_window    # full | sliding_window | summarize
  context_window_tokens: 32000

budget:
  max_tokens: 200000
  max_seconds: 600
  max_cost_usd: 1.0

checkpoints:
  - id: reproduces-first
    at: turn:3
    type: trajectory
    params: {require_tool: run_shell, pattern: "pytest.*repro|python -c"}
    weight: 0.05
    required: false

  - id: unit-tests-pass
    at: final
    type: command
    params: {cmd: "python -m pytest -q", expect_exit: 0}
    weight: 0.45
    required: true

  - id: no-test-tampering
    at: final
    type: diff
    params: {paths: ["tests/**"], allow: none}
    weight: 0.2
    required: true

  - id: no-regression
    at: final
    type: command
    params: {cmd: "python -m pytest tests/test_regression.py -q", expect_exit: 0}
    weight: 0.15
    required: true

  - id: patch-minimal
    at: final
    type: diff_metric
    params: {max_files: 3, max_lines: 40}
    weight: 0.1
    required: false

  - id: explanation-quality
    at: final
    type: llm_judge
    params:
      rubric: rubrics/bugfix_explanation.md
      model: judge-default
      samples: 3
    weight: 0.05
    required: false

seeds: [1, 2, 3]
artifacts: [patch.diff, pytest.log, trace.jsonl]
```

**规范要点：**
- `required: true` 的检查点失败 → 任务直接判 0（模拟你的"硬性扣分项"）
- `weight` 之和不必等于 1，会归一化
- `at` 支持 `turn:N` / `event:tool_call` / `final`
- 所有时间、费用、token 都有上限，缺省值由全局配置兜底

---

## 9. 检查器清单（v0.1 只做 6 类）

| 类型 | 参数 | 测什么 | v0.1 |
|---|---|---|---|
| `file` | path / exists / contains / regex / hash | 产物是否存在、内容是否符合 | ✅ |
| `command` | cmd / expect_exit / timeout | 测试、编译、lint | ✅ |
| `diff` | paths / allow / forbid | 有没有动不该动的文件 | ✅ |
| `diff_metric` | max_files / max_lines / max_files_touched | 改动是否克制 | ✅ |
| `trajectory` | max_tool_calls / invalid_calls / repeated_actions / first_action | 过程是否合理 | ✅ |
| `llm_judge` | rubric / model / samples / threshold | 主观质量（文档、解释、代码风格） | ✅ |
| `json_path` | path / equals | 结构化输出正确性 | v0.2 |
| `snapshot_diff` | before / after | 环境副作用 | v0.2 |

**LLM judge 的硬性要求（做不好就会毁掉整个项目）：**
1. 规则优先——能用命令判定的，绝不用模型；
2. judge 必须独立于被测模型（不能用同一个模型自评）；
3. 每个 judge 至少采样 3 次取多数；
4. **必须做校准**：人工标注 20–30 条作为 gold，算与 judge 的一致率（Cohen's kappa），低于 0.6 就重写 rubric。

> 这第 4 条，就是你和其他玩具项目的分水岭。面试时能说出"我的 judge 和人工标注 kappa 是 0.72"，比"我用了 LLM-as-judge"值钱一百倍。

---

## 10. 评分规范

```
单任务得分 = Σ(通过检查点的权重) / Σ(全部权重)
若任一 required 检查点失败 → 得分 = 0
任务成功率 = 得分 ≥ 0.8 视为通过（阈值可配）

pass@k：同一任务 k 次独立运行中至少一次通过的比例
报告必须同时给：通过率、pass@k、平均成本、P50/P95 延迟、平均轮数
```

**报告必须回答的 5 个问题：**
1. 总榜：哪个模型/配置最好？差多少？
2. 失败分布：哪个检查点最常挂？（这是最有洞察力的一张图）
3. 失败模式分类：预算耗尽 / 工具误用 / 提前终止 / 上下文丢失 / 改测试作弊
4. 成本：每成功任务多少钱？每提升 1% 成功率要花多少？
5. 稳定性：同样配置跑 3 次，分数方差多大？方差大的模型不能上生产。

---

## 11. 8 周里程碑

| 周 | 交付 | 验收标准 |
|---|---|---|
| **W1** | schema + mock agent + 1 个任务 + CLI 跑通 | `agent-eval run tasks/xxx.yaml --agent mock` 能输出一份 trace |
| **W2** | Docker 沙箱 + `command` / `file` / `diff` 三类检查 | 容器内跑 pytest，正确判定通过/失败，记录 digest |
| **W3** | 工具调用 + trajectory 检查 + 预算上限 | 能识别"工具调用超 20 次"并终止 |
| **W4** | 5 个任务 + 3 种子 + pass@k + Markdown 报告 | 一次跑完 5×3 个 run，报告含成本与轮数 |
| **W5** | LLM judge + 人工标注 20 条 + kappa 计算 | kappa ≥ 0.6，写出校准过程的文档 |
| **W6** | OpenAI 兼容适配器（DeepSeek/智谱/通义各跑一次） | 3 个模型在同一任务集上的对比表 |
| **W7** | HTML 报告 + GitHub Actions（mock 模式 30 秒自测）+ 全部文档 | 陌生人不看源码能在 30 分钟内新增一个任务 |
| **W8** | 发布 v0.1 + 3 篇博客 + 找 2 个真实用户试用 | 有 star、有 external issue、有反馈记录 |

**里程碑纪律：每周五必须能演示。** 演示不了就砍范围，不要顺延——这个项目最可能死在"想做完再做"。

---

## 12. 风险与对策

| 风险 | 对策 |
|---|---|
| **鸿蒙任务容器化难**（DevEco 依赖 GUI、SDK 授权、模拟器） | v0.1/v0.2 只做 Python/TS 任务。鸿蒙任务放 v0.3，用**混合方案**：静态检查（`tsc` + ArkTS lint + 结构断言）+ 构建脚本 + 真机/模拟器半自动跑。**不要在 v0.1 碰它** |
| LLM judge 不稳定 | 规则优先；多采样取多数；做 kappa 校准；rubric 写死输出 schema（JSON 字段 + 打分理由） |
| 任务写得慢，5 个任务写两周 | 先写 `_template/`，每写一个任务记录耗时，第 3 个开始必须 < 45 分钟 |
| 变成又一个玩具项目 | 从 W5 起就找人用；每月发一次版本；README 必须有"3 条命令跑通" |
| 调试期烧钱 | 全局 `max_cost_usd` 默认值设很低（如 0.5/任务）；开发期全部走 mock 与本地小模型 |
| **触碰公司资产** | 任务集**全部自己写**，不用公司的题目、评分规则、内部提示词。方法论可以借鉴，数据一律不碰。项目开源前做一次自检 |
| 范围膨胀 | 每周回顾"不做什么"清单；任何新想法写进 `docs/backlog.md`，不进 v0.1 |

---

## 13. 配套的 3 篇博客（发布节奏：W8 前写完）

1. **《为什么 Agent 评测不能只看结果：轨迹级检查的 5 个理由》**——立论，解释四层检查点
2. **《checkpoint 设计的 5 个反模式》**——把你现在工作里的直觉系统化：重复扣分、检查点耦合、只测终态、权重拍脑袋、不可复现
3. **《3 个模型 × 20 个任务：成功率、pass@k 与每成功任务成本》**——数据篇，最有传播力

> 三篇的顺序有讲究：先立论，再方法论，最后数据。数据篇发出去时，前两篇已经给你积累了可信度。

---

## 14. 面试时怎么讲（STAR + 数字）

```
背景：我在评测岗发现，只看最终产物打分，分不清模型是"能力强"还是"碰巧对了"。
设计：我把评测拆成过程/终态/轨迹/回归四层检查点，做了 xx 个任务，
      每个任务 3 个种子，judge 与人工标注 kappa 0.72。
数据：3 个模型对比，成功率 A 78% / B 71% / C 65%，
      但 C 的每成功任务成本只有 A 的 1/3，P95 延迟低 40%。
结论：没有绝对最好的模型，只有场景下最优的性价比。
踩坑：第一版 judge 把"代码长"当"代码好"，校准后被我用 diff_metric 替代。
```

**面试官听到"我做了个 eval 框架"不会兴奋，听到"我发现 A 模型在长任务上方差是 B 的 3 倍，所以不能上生产"会。**

---

## 15. 一句话收尾

这个项目的价值不在于代码量，而在于**你是否真的用它回答过一个你关心的问题**。

哪怕只做了 5 个任务，只要你能拿出"我因此改变了某个决策"的证据，它就成立。

---

## 附：开工前的 3 个前置检查

- [ ] Docker 能跑起来，且知道怎么固定镜像 digest
- [ ] 拿到 1 个便宜模型的 API key（DeepSeek / 智谱 / 百炼免费额度），**不要用公司的**
- [ ] 想清楚 v0.1 的 5 个任务分别测什么：建议 3 个 coding（bugfix / 新功能 / 多文件重构）+ 1 个 tool_use（检索后编辑）+ 1 个 long_context（跨 10 个文件改接口）