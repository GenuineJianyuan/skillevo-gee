# SkillEvo-GEE 当前架构、论文思路与工作路径

> 用途：用于核对当前工程是否准确表达论文思路，并作为下一阶段开发路线。
>
> 状态基线：2026-11-02 当前本地工程。本文区分“已经实现”“已有结构但尚未闭环”“论文设想”，避免将规划写成实验事实。

## 1. 当前项目的准确定位

当前 SkillEvo-GEE 最适合被定义为：

**一个由多层次领域知识资产约束、以 Hermes 负责运行时推理和角色调度、以 Python/Node 工具负责确定性执行的 GEE 代码生成与执行审计原型。**

系统当前的主线不是“Agent 自主改变自身”，也还不是“完整的 Skill 自动演化系统”。已形成并经过真实验证的核心是：

1. 将 GEE 分析知识组织为 `Capability -> Task -> Subtask`；
2. 将 Example 作为 Subtask 的终端内容，而不是独立资产层；
3. 由需求、规划、数据、代码、审计等职责型 Skill 约束 Hermes 的推理过程；
4. 由 Python CLI 统一启动 Hermes；
5. 由项目插件向 Hermes 暴露知识检索、工作流初始化和 GEE 执行工具；
6. 由真实 Earth Engine 请求检查生成代码的可执行性和部分中间结果。

因此，现阶段论文主问题应优先落在：

> 多层次、可追踪的 Skill 知识能否改善 GEE 需求理解、方案规划、代码生成和执行诊断？

“Skill 演化”可以保留为系统总目标和第二阶段研究问题，但当前不宜声称已经实现自动新增、修改、融合和发布的完整闭环。

## 2. 当前知识层次

当前工程采用的是三类正式资产，而不是四类独立资产：

```text
capabilities.md
    -> Task Markdown
        -> Subtask Markdown
            -> Example section + implementation + evidence + limitations
```

### 2.1 Capability

`capabilities.md` 是能力索引，回答：

- 系统当前覆盖哪些完整分析目标；
- 对应哪个 Task；
- 能力处于 `verified` 还是 `experimental`；
- 已知的不适用情形和验证边界是什么。

它不应包含完整算法和大段代码，也不直接承担代码生成。

### 2.2 Task

Task 表示一个完整分析目标，定义：

- 输入和输出；
- 有序工作流；
- 工作流各步骤引用的 Subtask；
- 数据流和前后依赖；
- 能力边界；
- 最终验收条件。

Task 的作用是为 Planning Agent 提供“整体方案骨架”，而不是提供可直接复制的代码。

### 2.3 Subtask 与内嵌 Example

Subtask 表示可复用的局部方法，包含：

- 方法简述和输入输出语义；
- 算法原理与关键 GEE 算子；
- 参数和软约束；
- 失败模式与限制；
- `## Example` 场景；
- 同一文档内的实现代码、验证状态和证据。

Example 不再具有独立 ID、目录或引用层级。这样做的优点是减少检索跳转，使 Code Agent 获取一个 Subtask 时同时获得方法、约束和实现参考；代价是同一 Example 难以被多个 Subtask 独立复用和评估。论文中需要明确这是当前设计选择，而不是遗漏。

当前目录校验已强制：每个 Subtask 必须有 Example 章节和内嵌代码。

## 3. 核心目录及职责

```text
skillevo/
├── skillevo.py                 # 源码树统一入口
├── pyproject.toml              # Python 包和 skillevo-gee 命令入口
├── README.md                   # 安装及运行说明
├── src/                        # 确定性程序逻辑
│   ├── cli.py                  # run/catalog/gee/workflow 命令
│   ├── hermes_runner.py        # Python -> hermes chat
│   ├── models.py               # 需求、计划、状态、执行、演化数据模型
│   ├── workflow.py             # 状态机与失败回退规则
│   ├── paths.py                # 项目根目录解析
│   ├── knowledge/              # Markdown 解析、检索和结构校验
│   └── gee/
│       ├── executor.py         # Python GEE 执行适配器
│       └── runtime/            # Node worker 与固定 npm 依赖
├── .hermes/
│   ├── skills/                 # 7 个职责型 Agent Skill
│   └── plugins/skillevo-gee/   # Hermes 可调用的项目工具
├── knowledge/
│   ├── published/              # 运行时只读的正式知识
│   │   ├── capabilities.md
│   │   ├── tasks/
│   │   └── subtasks/
│   ├── candidates/             # 待审查的演化候选区
│   └── evolution/              # 演化规则和模板，当前尚未闭环
├── raw_GEE_case/               # 原始来源案例，不直接进入运行上下文
├── config/                     # GEE 配置模板和本机私有配置
├── runs/                       # 单次请求、生成代码、执行报告等运行产物
└── tests/                      # 目录、状态机、插件、Hermes/GEE 适配测试
```

### 3.1 `src/`：确定性基础设施

`src` 不负责自由推理，而负责模型可以稳定调用和程序可以重复验证的部分：

- 解析和校验 Markdown；
- 保存请求状态；
- 检查引用关系；
- 启动 Hermes；
- 启动 GEE worker；
- 收集结构化执行结果；
- 对状态转换和失败回退施加约束。

这一边界很重要：LLM 负责语义判断和代码生成，Python/Node 负责不可含糊的状态、文件、执行和证据。

### 3.2 `.hermes/skills/`：运行角色的行为约束

当前有 7 个 Skill：

| Skill | 当前职责 | 在代码生成主线中的位置 |
|---|---|---|
| `skillevo-supervisor` | 控制阶段顺序和失败回退 | 总协调 |
| `skillevo-requirement-agent` | 规范化需求并判断覆盖 | 输入端 |
| `skillevo-planning-agent` | 组合 Task/Subtask，建立方案 | 代码生成前置核心 |
| `skillevo-data-agent` | 检查数据、波段、覆盖和预处理 | 代码生成前置核心 |
| `skillevo-code-agent` | 将已批准方案转为 GEE JavaScript | 当前研究核心 |
| `skillevo-audit-agent` | 执行、检查结果并分类失败 | 代码生成后置核心 |
| `skillevo-evolution-agent` | 指导候选知识的新增/修改/融合 | 后续研究模块 |

严格地说，这些目前是 Hermes 中的**职责型 Skill**，并不等同于七个彼此隔离、各自拥有独立上下文和生命周期的进程级 Agent。论文若使用“多 Agent”，需要说明实现形式是“由 Supervisor 调度的角色化 Agent Skill”，或者后续真正实现独立 Agent 调用与消息协议。

### 3.3 `.hermes/plugins/skillevo-gee/`：模型与工程之间的工具边界

当前插件注册三个工具：

| 工具 | 作用 | 成熟度 |
|---|---|---|
| `skillevo_catalog` | list/search/get/validate 正式知识 | 已实现 |
| `skillevo_workflow_init` | 建立请求和初始状态 | 已实现，但仅覆盖初始化 |
| `skillevo_gee_execute` | 执行可信本地 GEE JS 并返回 JSON | 已实现并真实验证 |

这三个工具已经建立最小可用闭环，但还不足以形成严格、可重复的完整代码生成实验流水线。后续需要增加计划保存、数据检查、代码产物登记、审计判定和状态推进等工具。

### 3.4 `knowledge/`：论文的主要研究对象

`knowledge/published` 是运行期只读资产。当前有：

- 1 个 Capability；
- 7 个 Task；
- 15 个 Subtask；
- 5 个 verified 资产，18 个 experimental 资产。

只有影像重采样链条完成了当前 worker 下的真实端到端验证。其余 6 个 Task 主要来自原始案例拆分，适合作为后续代码生成实验和知识修正样本，不能直接视作已经验证的系统能力。

`knowledge/candidates` 和 `knowledge/evolution` 已表达发布隔离思想，但目前前者几乎为空，后者主要是规则文字和模板，尚无完整程序支持。

### 3.5 `runs/`：可追踪实验记录

理想情况下，每个请求目录应成为一次实验的完整证据包：

```text
runs/<request_id>/
├── requirement.json|md
├── coverage.json
├── data_report.json|md
├── plan.json|md
├── generated.js
├── code_manifest.json
├── execution.json
├── audit.json|md
└── state.json
```

当前只稳定实现了状态初始化和 GEE 执行结果保存；其他产物主要依赖 Hermes 在对话中自行创建，文件名和结构还未被程序强制。这是近期最应补齐的部分。

## 4. 当前代码生成主链

当前用户入口为：

```powershell
python skillevo.py run "用户的 GEE 分析需求"
```

调用路径为：

```text
用户需求
  -> Python HermesRunner
  -> hermes chat + skillevo-supervisor
  -> Requirement Skill
  -> skillevo_workflow_init
  -> skillevo_catalog
  -> Planning/Data Skills
  -> Code Skill 生成 GEE JavaScript
  -> skillevo_gee_execute
  -> Node Earth Engine worker
  -> Audit Skill
  -> 结果或定向回退
```

### 4.1 推荐的严格阶段顺序

#### 阶段 A：需求规范化

输出应至少包括目标、研究对象、区域、时间、数据偏好、输出、方法约束和未知项。未知信息不得被 Code Agent 静默补造。

#### 阶段 B：能力覆盖判断

先读 `capabilities.md`，再读可能匹配的 Task。输出 `full / partial / uncovered`。能力不覆盖时应停止或进入独立演化流程，不应让代码模型凭常识绕过知识边界。

#### 阶段 C：最小知识包构建

从 Task 引用沿链接读取 Subtask，再读取其内嵌 Example。只注入当前计划所需的最小资产集合，同时记录 ID、版本、状态和用途。

#### 阶段 D：数据检查

确认数据集 ID、数据类型、时间和空间覆盖、波段、单位、比例因子、QA 和空集合风险。数据存在不等于适用于当前方法。

#### 阶段 E：统一规划

计划是 Code Agent 的直接依据。每个步骤必须声明输入、输出、知识引用和验收条件。多 Task 组合必须显式说明接口，不能只是拼接两个示例。

#### 阶段 F：代码生成

Code Agent 应：

- 逐段映射计划步骤；
- 只使用已检查的数据和参数；
- 标注未决占位符；
- 生成空集合、波段和关键中间结果检查；
- 输出计划步骤到代码段的映射；
- 将代码写入当前请求目录，而不是覆盖知识资产。

#### 阶段 G：执行与审计

GEE worker 进行真实云端求值。Audit Agent 分开判断：执行正确性、数据正确性、中间结果、最终结构和科学解释边界。退出码为 0 只表示运行层成功，不表示方法科学有效。

#### 阶段 H：定向回退

- 数据/空集合问题回到 Data；
- 方法或数据流问题回到 Planning/Knowledge；
- JS 语法或 GEE API 问题回到 Code；
- 权限和用户资产问题转为等待用户；
- 达到重试上限后失败，不无限自修复。

## 5. 当前实现成熟度

| 能力 | 当前状态 | 说明 |
|---|---|---|
| Python 一条命令启动 Hermes | 已实现 | 已真实运行 |
| Hermes 不走代理、GEE 单独走代理 | 已实现 | 已真实验证 |
| Capability/Task/Subtask 解析与校验 | 已实现 | 23 个资产通过校验 |
| Task 到 Subtask 的稳定引用 | 已实现 | 无缺失或跨层引用 |
| Subtask 内嵌 Example | 已实现 | 15/15 有章节和代码 |
| GEE 云端执行与结构化结果 | 已实现 | 冒烟链 3 成功、0 失败 |
| 工作流状态模型与失败分类 | 部分实现 | Python 有模型，插件只暴露 init |
| 需求产物标准化 | 部分实现 | 模型存在，落盘协议未完全强制 |
| 数据自动核查 | 初步定义 | 有 Data Skill，无专用数据探测工具 |
| 计划门槛 | 初步定义 | 有 `AnalysisPlan` 模型，无保存/校验工具 |
| 代码生成产物协议 | 初步定义 | 主要依赖 Hermes 自由写文件 |
| 自动审计计划验收条件 | 部分实现 | 有运行统计，无通用判定器 |
| 多 Task 组合实验 | 尚未验证 | 设计存在，缺少系统实验 |
| 语义检索 | 未实现 | 当前是简单词项计数检索 |
| Evolution add/modify/merge | 规则草案 | 尚无完整 CLI、候选状态机和发布器 |
| 演化效果评估 | 未实现 | 尚无前后版本基准和回归集 |

## 6. 与论文思路的符合程度

### 6.1 已经符合的部分

1. **知识与执行分离**：Markdown 知识、Hermes 推理、Python/Node 执行边界清楚。
2. **能力边界显式**：Capability 和状态字段能区分 verified/experimental。
3. **方案先于代码**：Skill 和状态机均表达该约束。
4. **可追踪知识引用**：Task/Subtask 有稳定 ID、版本和 references。
5. **真实运行审计**：不是只检查代码文本，能够访问 Earth Engine 求值。
6. **运行成功与科学有效性分离**：Audit Skill 已明确这一点。
7. **演化与单次分析隔离**：published 只读、candidate 待审查的方向正确。

### 6.2 需要修改论文表述的部分

1. 原始大纲中的“四层 Markdown Skill”应改为：
   **三类知识资产，Example 作为 Subtask 内嵌实现证据。**
2. Task/Subtask 不是 Hermes 的独立 `SKILL.md`；它们是领域知识资产，由程序检索后注入 Agent 上下文。
3. 当前七个 Agent 更准确地说是七个角色 Skill。若论文强调真正的多 Agent 协作，需要补充独立调用、上下文隔离和消息记录机制。
4. 当前“演化”只改变知识上下文的目标是合理的，但自动新增、修改、融合、验证、发布尚未形成工程事实。
5. 当前实验能力主要证明代码执行基础设施，不足以证明复杂地理空间分析的科学正确性。

### 6.3 建议的论文中心论点

建议把中心论点收敛为：

> 与直接提示生成 GEE 代码相比，使用 Capability、Task、Subtask 和内嵌 Example 构成的可追踪知识上下文，并经过需求、数据、规划和执行审计门槛，可以提高生成代码的结构一致性、知识依据可追踪性、可执行率和失败可诊断性。

演化部分可作为第二个论点：

> 在审计证据和人工审批约束下，对知识资产执行新增、修改和融合，能否在不改变模型参数和运行编排的情况下持续提高后续任务表现，并控制知识回归？

这两个论点应分阶段验证。第一个论点是当前工程的重点，第二个论点需要后续专门实现和实验。

## 7. 代码生成部分的近期建设重点

### 7.1 建立强制性的运行产物协议

新增程序工具，而不是只依赖 Hermes 自由组织文件：

- `workflow update`：合法推进阶段并登记产物；
- `requirement save/validate`；
- `plan save/validate`；
- `code save`：保存 JS 和知识映射 manifest；
- `audit save`：保存分类结果和回退目标；
- `run inspect`：检查一次请求是否完整可复现。

这会把“Prompt 中要求先规划”提升为“程序上没有有效 Plan 就不能进入 Code”。

### 7.2 给 Data Agent 增加只读探测工具

当前 Data Agent 只有行为规则。建议增加：

- 检查 Earth Engine asset 是否可访问；
- 获取 Image/ImageCollection/FeatureCollection 类型；
- 读取 bands、properties 和时间范围；
- 对指定区域与时间执行 collection size；
- 返回少量元数据或统计，不执行大规模分析。

这样可以将数据核查从语言模型猜测变为工具证据。

### 7.3 将 Code Agent 输出结构化

建议每次生成同时输出：

```text
generated.js
code_manifest.json
```

manifest 至少记录：

- request ID 和 plan 版本；
- 每个代码段对应的 plan step；
- 使用的 Task/Subtask ID 与版本；
- 数据集、波段、参数和占位符；
- 预期输出及验收检查；
- 生成时间和重试编号。

### 7.4 扩展执行 worker，但保持边界明确

当前 worker 适合 `print(eeObject)` 和 `Map.addLayer(ee.Image)` 的小区域检查。后续按实验需求逐步支持：

- ImageCollection 数量和聚合检查；
- FeatureCollection 样本和属性检查；
- 表格型结果；
- 受控的批处理 Export 状态监测；
- 更清晰的资源限制和超时分类。

不应直接模拟全部 Code Editor UI。UI、图例和交互控件可以标记为不可执行展示代码，避免把展示成功当成分析成功。

### 7.5 建立代码生成评估集

从 `raw_GEE_case` 和额外人工需求中构建固定测试集，每个案例保存：

- 用户需求；
- 目标 Task/Subtask；
- 必需数据和参数；
- 关键代码结构；
- 应出现的检查；
- 可执行的验收条件；
- 已知错误类型。

建议指标包括：

- 能力覆盖判断准确率；
- Task/Subtask 检索准确率；
- 计划完整率；
- 代码首次执行成功率；
- 修复后成功率与重试次数；
- 数据集/波段幻觉率；
- 计划步骤到代码的覆盖率；
- 审计错误定位准确率；
- 科学边界声明完整率。

## 8. 演化部分的合理设计

演化不应在代码生成失败后直接改 published 知识。建议使用以下独立流程：

```text
来源或审计问题
  -> evolution candidate
  -> add / modify / merge 分类
  -> 结构校验
  -> Example 执行验证
  -> 回归测试
  -> 人工审查 diff
  -> 显式批准
  -> 发布新版本
  -> 更新 capabilities
```

### 8.1 Add

适用于现有 Task/Subtask 无法覆盖的新目标或新方法。先搜索重复资产，再分解为 Task 和 Subtask，并把实现与证据嵌入 Subtask。

### 8.2 Modify

适用于错误修正、约束补充、数据版本升级或实现改进。必须列出所有引用者、版本变化、受影响案例和回归结果。

### 8.3 Merge

适用于高度重叠的 Task/Subtask。相似度只能提出候选，不能自动决定合并。合并需要检查语义、输入输出、算法假设、参数和引用迁移，避免把名称相似但科学含义不同的方法合并。

### 8.4 演化的最低工程闭环

后续至少需要：

- candidate manifest 和唯一 ID；
- add/modify/merge CLI；
- published/candidate 双目录校验；
- 引用影响分析；
- Markdown 结构 diff；
- Example 批量执行及证据关联；
- 固定回归集；
- 审批记录；
- 原子发布和回滚；
- capabilities 自动或半自动重建。

在这些功能完成前，`EvolutionOperation`、`EvolutionCandidate`、演化指南和模板只能被描述为**演化数据结构与流程草案**。

## 9. 建议的实验设计

用户已明确暂不需要对照组，因此近期可先完成单系统工程验证和案例研究，不必立即构建无 Skill 对照。但论文最终若要回答“Skill 是否带来改善”，仍建议保留后续对照设计的可能性。

### 9.1 第一阶段：系统可行性

- 验证不同 Task 是否能完成需求到代码到执行；
- 记录首次成功率、失败类别和回退路径；
- 验证产物是否完整可复现；
- 验证能力外请求是否正确停止。

### 9.2 第二阶段：知识结构有效性

- 检查 Task/Subtask 选择是否正确；
- 检查 Example 是否被错误越界复用；
- 检查计划与代码映射；
- 分析 verified 与 experimental 知识对结果的影响。

### 9.3 第三阶段：演化案例

选择有限、可审计的真实问题：

- Add：加入一个原系统不覆盖的新 Task；
- Modify：修复一个已知数据集或算法错误；
- Merge：合并两个重复 Subtask。

比较演化前后固定案例的覆盖、执行、诊断和回归情况。此时研究的是知识上下文演化，而不是模型参数或 Agent 编排自修改。

## 10. 推荐工作路径

### P0：冻结当前基线

- 保留当前 23 个资产及版本；
- 将重采样链作为 infrastructure baseline；
- 保存当前测试和真实 GEE 冒烟结果；
- 修订原始论文大纲中的 Example 层和多 Agent 表述。

### P1：完成代码生成工程闭环

- 标准化 `runs/<request_id>` 产物；
- 暴露 workflow transition 和 artifact registration；
- 实现 plan/code/audit 的保存与校验；
- 增加 Data Agent 的 GEE 元数据工具；
- 确保无 Plan、无数据报告时不能调用代码生成。

### P2：逐个验证现有 6 个 experimental Task

建议顺序：

1. 水域面积时间序列；
2. 土壤湿度时间序列；
3. 风速时间序列；
4. EVI 物候；
5. 干旱指数；
6. 盐渍化展示。

顺序依据是先处理公开数据、非私有资产、较少 UI 依赖的案例。每个 Task 都应经历数据核查、代码修正、真实执行、证据写回和状态升级，而不是一次性把全部 experimental 标记为 verified。

### P3：构建固定评估集和运行报告

- 为每个 Task 准备多个需求变体；
- 增加能力外请求；
- 自动汇总执行和审计指标；
- 固定模型、Hermes 配置、知识版本和 GEE runtime 版本；
- 形成可重复的论文实验协议。

### P4：实现受控演化最小闭环

- 先实现 Add；
- 再实现 Modify 和引用影响分析；
- 最后实现 Merge；
- 所有发布均需要验证、回归和人工批准。

### P5：开展演化效果研究

- 用固定评估集测量演化前后变化；
- 同时报告能力提升和回归；
- 分析错误是来自知识、检索、规划、代码还是执行；
- 避免把一次成功修复直接解释为系统具有普遍自我演化能力。

## 11. 当前最重要的边界

1. 当前系统重点是 Skill 约束的代码生成，不是自主研究设计。
2. Example 是实现证据，不是 Task 方案的唯一来源。
3. published 知识在分析运行中只读。
4. GEE 成功执行不等于科学结论正确。
5. experimental 资产不应被描述为已验证能力。
6. Evolution Agent 当前是流程规范，不是完整演化引擎。
7. Hermes Skill 写入审批只保护 Hermes Skill；领域知识发布仍需要自己的候选、验证和审批机制。
8. 如果论文主张多 Agent 优于单 Agent，需要补充真正的 Agent 隔离或清楚说明“角色化 Skill 调度”的实现定义。

## 12. 建议优先核对的论文问题

请首先检查以下判断是否符合论文意图：

1. 论文的第一贡献是否应是“多层知识约束的 GEE 代码生成与执行审计”，而不是泛化的自主 Agent？
2. Example 是否确定作为 Subtask 内嵌内容，不再作为独立第四层资产？
3. 多 Agent 是否允许以 Hermes 的角色 Skill 形式实现，还是必须具有独立 Agent 上下文和通信？
4. 数据检查是代码生成前的强制门槛，还是可选辅助步骤？
5. 执行审计的目标是运行正确性和方案一致性，是否明确不承担完整科学有效性证明？
6. 演化是否严格限定为知识资产的 Add/Modify/Merge，不改变 Agent 编排、验证策略和模型参数？
7. 演化是否必须经过人工审批，还是论文希望研究一定范围内的自动发布？
8. 当前阶段是否先完成代码生成主链和单系统实验，再单独构建演化实验？

如果以上答案成立，当前工程方向与论文核心是一致的，但论文大纲需要从“完整系统已经具备演化能力”的语气，调整为“先建立可追踪代码生成闭环，再研究受控知识演化”的分阶段表述。
