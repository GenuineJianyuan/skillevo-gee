# 能力外自主求解与受控知识演化

本文说明 Capability → Task → Subtask 正式知识路径之外的第二条执行路径。其目标是区分“当前知识无法覆盖的请求”和“已发布知识资产”，并确保任何新知识在用户明确批准前都停留在候选区。

## 1. 两种执行模式

### 1.1 正式知识模式

```text
Requirement → capabilities.md → Task → Subtask/Example
  → Data → Plan → Code → GEE → Audit
```

只有 `matched` 才能读取 Task 或 Subtask。选中的 Task 定义完整工作流：Required Subtask 必须全部进入计划，Optional Subtask 必须说明加入理由。

### 1.2 自主模式

```text
Requirement → capabilities.md → partial/unmatched
  → 待行记录 → 自主规划
  → 自主数据核查 → 自主方案
  → Code Agent → GEE 执行 → Audit Agent
  → runs 证据 → Add/Modify 候选（仅审计合格时）
```

自主模式不得加载、引用、改写或模仿当前正式 Task/Subtask/Example。它可以使用直接获得的 Earth Engine 证据、通用 API 推理、用户提供的材料和显式假设。

`partial` 也必须把完整用户需求作为一个自主问题处理，不能用正式 Task 完成已覆盖部分，再为剩余部分临时拼接步骤。

## 2. 工作流状态和运行产物

工作流状态记录：

- `coverage_route`：`matched|partial|unmatched`；
- `knowledge_mode`：`published|autonomous`；
- `routing_reason`：路由依据；
- `candidate_id`：开始演化后关联的候选 ID。

自主请求首先写入：

```text
runs/pending/autonomous-planning/<request_id>.json
```

`workflow start-autonomous` 将请求推进到可执行的 `autonomous_planning` 阶段。后续继续使用 `data`、`planning`、`code`、`execution` 和 `audit` 等阶段，但 `knowledge_mode=autonomous` 禁止读取正式领域知识。

一次自主运行应登记以下产物：

```text
runs/<request_id>/
├── requirement.json|md
├── autonomous_plan.json|md
├── data_report.json|md
├── generated.js
├── execution.json
├── audit.json
└── state.json
```

CLI 和 Hermes 插件负责确定性的状态推进、产物登记和审计保存；Agent 负责生成计划、代码和科学判断内容。

为了避免一次请求演变成开放式探索，Supervisor 默认限制为 24 turns/300 秒；Task 引用的 Subtask 通过一次 `get-many` 批量读取。每个状态变更只执行一次，GEE 失败最多进行一次有明确依据的修正重试。正式知识模式下，Data Agent 从 Task/Subtask 记载的数据定义出发；产品和波段已明确时，把数据 checks 合并进最终脚本的一次执行，只有真实未知项才单独 probe，也不探测 Python 或绘图库环境。Hermes 的过程输出默认写入 `runs/hermes-logs/` 而不直接显示在终端；`--show-progress` 只用于诊断。

默认终端状态监视器将阶段映射为负责角色：`requirement/capability` 为 Requirement Agent，`knowledge/planning` 为 Planning Agent，`data` 为 Data Agent，`code` 为 Code Agent，`execution/audit` 为 Audit Agent（execution 同时调用 GEE Executor），candidate 阶段为 Evolution Agent。阶段不变时输出周期心跳；阶段序号倒退时明确标记 `local rollback from <stage>`，用于观察分类回退而不暴露模型思考内容。

## 3. 审计门槛

Audit Agent 分别检查：

1. **执行**：认证、权限、API、语法、超时和资源；
2. **数据**：集合数量、波段、覆盖、比例因子和有效像元；
3. **中间结果**：类型、范围、数量、分布和投影；
4. **任务验收**：是否满足用户输出和计划验收条件；
5. **科学边界**：哪些结论无法由一次执行证明。

`audit.json` 保存上述门槛、证据路径、科学限制和唯一的知识建议：

| 建议 | 含义 |
|---|---|
| `add` | 自主结果填补了真实且可复用的正式知识缺口 |
| `modify` | 现有正式知识需要经过验证的修正或扩展 |
| `needs_more_evidence` | 执行、数据或科学证据仍不足 |
| `reject` | 结果无效、重复、不可复用或不适合保留 |

只有执行、数据、方案和验收四项全部通过，且建议为 `add` 或 `modify` 时，才允许 `candidate_eligible=true`。

## 4. 候选生命周期

```text
audit.json
  → knowledge/candidates/cand-*/
  → proposed Task/Subtask/capabilities
  → 完整目录覆盖校验
  → 用户明确批准
  → 最终目录校验和发布
```

候选目录结构：

```text
knowledge/candidates/cand-*/
├── candidate.json
├── README.md
├── proposed/
│   ├── capabilities.md
│   ├── tasks/*.md
│   └── subtasks/*.md
└── before/                  # 发布替换已有资产时创建
```

Add 候选必须引入新的 Task/Subtask ID，并提供更新后的 `capabilities.md`。Modify 候选必须准确声明所有被修改的已有资产 ID、保持稳定 ID、升级版本并记录受影响引用；只有业务范围或 Task 路由描述改变时才需要提供 `capabilities.md`。

## 5. CLI 操作

记录审计证据：

```powershell
python skillevo.py audit record --request-id req-... `
  --execution-passed --data-passed --plan-passed --acceptance-passed `
  --candidate-eligible --recommendation add `
  --finding "..." --limitation "..." `
  --evidence runs/req-.../execution.json
```

创建、验证和发布候选：

```powershell
python skillevo.py evolution create --request-id req-... --operation add `
  --rationale "新增可复用能力"
python skillevo.py evolution validate --candidate-id cand-...
python skillevo.py evolution approve --candidate-id cand-... --approved-by "human"
python skillevo.py evolution publish --candidate-id cand-...
```

Modify 需要增加一个或多个 `--target-id`。没有明确批准记录时，`publish` 会拒绝执行。发布前会验证候选覆盖后的完整目录；替换资产会备份在候选目录，最终校验失败时会回滚本次应用的文件。

## 6. 自动化边界

已经程序化实现：

- 路由记录和自主阶段推进；
- 运行产物登记和结构化审计保存；
- 候选结构、引用和完整目录验证；
- Add/Modify 状态控制和安全发布检查。

仍由 Agent 与用户共同完成：

- 新科学问题的合理拆解；
- 未知数据集的选择与解释；
- 自主计划和候选 Markdown 的具体内容；
- 判断结果是否具有科学可复用性；
- 发布前的用户明确批准。

因此，当前系统已经具备能力外自主求解和受控知识演化的工程路径，但不声称实现了无人监督的科学发现或自动发布。
