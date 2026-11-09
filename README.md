# SkillEvo-GEE

SkillEvo-GEE 是一个基于 Hermes 的研究型系统，用于表示、检索、执行、审计并演化 Google Earth Engine（GEE）分析知识。

环境前提、已验证版本、Hermes/插件配置、GEE 凭据、代理边界和复现风险见 [`ENVIRONMENT_AND_DEPENDENCIES.md`](ENVIRONMENT_AND_DEPENDENCIES.md)。全部文档的用途和权威范围见 [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md)。

## 知识模型

本项目将 Hermes 的过程型 Skill 与地理空间领域知识资产分开：

| 层次 | 作用 | 位置 |
|---|---|---|
| Supervisor Skill | 约束端到端控制顺序 | `.hermes/skills/skillevo-supervisor/` |
| Requirement Skill | 规范化并保存用户需求 | `.hermes/skills/skillevo-requirement-agent/` |
| Planning Skill | 将 Task/Subtask 组织为方案，或构建隔离的自主方案 | `.hermes/skills/skillevo-planning-agent/` |
| Data Skill | 核查数据集、波段、尺度、区域和时间覆盖 | `.hermes/skills/skillevo-data-agent/` |
| Code Skill | 根据已批准方案生成可审计的 GEE JavaScript | `.hermes/skills/skillevo-code-agent/` |
| Audit Skill | 审查执行证据、验收条件和科学限制 | `.hermes/skills/skillevo-audit-agent/` |
| Evolution Skill | 创建并审查 Add/Modify 知识候选 | `.hermes/skills/skillevo-evolution-agent/` |
| 业务能力路由 | 在加载 Task 前对规范化需求分类 | `knowledge/published/capabilities.md` |
| Task | 定义完整分析目标和有序工作流 | `knowledge/published/tasks/` |
| Subtask | 定义可复用操作、约束及内嵌 Example | `knowledge/published/subtasks/` |

Task 通过 Markdown 引用关联 Subtask。Example 是所属 Subtask 的内嵌内容，不是独立资产层。每个 Task 区分 `Required workflow` 和 `Optional workflow`，每个 Subtask 声明 `operation: required|optional`。目录校验器会检查固定结构、操作分类和跨层引用。

Requirement Agent 首次判断时只读取 `capabilities.md`：

- `matched`：使用正式 Task/Subtask 知识；
- `partial/unmatched`：先记录能力缺口，再以 `knowledge_mode=autonomous` 继续运行，不加载当前 Task/Subtask/Example。

自主路径的计划、代码、执行和审计证据保存在 `runs/`。只有通过审计门槛的结果才能形成 `knowledge/candidates/` 下的 Add/Modify 候选；发布必须经过用户明确批准。

Task 和 Subtask 不是独立的 Hermes `SKILL.md`，而是具有稳定 ID、版本和引用关系的领域知识资产。Python 负责解析、校验和检索，Hermes 只加载当前操作所需的角色 Skill。

## 快速开始

首次配置无头 GEE 工具：

```powershell
Copy-Item config/gee.example.json config/gee.local.json
# 编辑 gee.local.json，填写 GEE project、外部凭据路径和 GEE 专用代理。
cd src/gee/runtime
npm ci --omit=dev
cd ../..
```

运行一次完整请求：

```powershell
cd "D:\Project\Paper_Projects\GEE Agent\skillevo-gee"
python skillevo.py run "分析 2020-2022 年指定区域的季节性水域面积变化"
```

维护和诊断命令：

```powershell
python skillevo.py catalog validate
python skillevo.py catalog list
python skillevo.py catalog search --query "Landsat resampling"
python skillevo.py gee execute --script runs/<request_id>/generated.js
```

执行 `pip install -e .` 后，也可以使用等价入口：

```powershell
skillevo-gee run "分析 2020-2022 年指定区域的季节性水域面积变化"
```

`run` 是面向用户的统一入口。Python 以一次性 CLI 客户端方式启动 `hermes chat` 并预加载 Supervisor Skill；Hermes 再调用项目插件和各职责型 Skill。低层命令用于测试、诊断和维护。

默认运行使用项目专用 provider `skillevo-alibaba-fast`，同时传入 `--reasoning none` 和 Qwen `/no_think` 指令；最多 24 个 Hermes turns，运行预算 300 秒。Task 引用的多个 Subtask 会批量读取；数据集和波段已由正式知识明确时，不再另写并执行 probe，而把检查合并到最终 GEE 脚本的一次执行中。

默认模式不会展示思考过程和工具 diff，但会持续显示当前 Agent、工作流阶段、request_id、已生成产物和运行时间。例如：

```text
[SkillEvo-GEE] Agent: Requirement Agent | stage: capability | request: req-...
[SkillEvo-GEE] Agent: Data Agent | stage: data | elapsed: 45s | request: req-...
[SkillEvo-GEE] artifacts ready: data_report
[SkillEvo-GEE] Agent: Planning Agent | stage: planning | request: req-...
```

阶段不变化时默认每 15 秒输出一次心跳，因此长时间 GEE 调用不会看起来像卡死。可以用 `--status-interval-sec 5` 缩短间隔。运行结束后显示最终回答、完成/失败状态及 `runs/hermes-logs/` 中的完整日志。如需查看 Hermes 原始工具过程，可显式执行：

状态监视器只绑定本次首次创建的 request；同一工作区中其他命令创建的 request 不会切换当前显示，也不会反复输出 multiple-requests 警告。对于 matched 请求，Planning 只读取本次 requirement/knowledge/data 产物，一次生成并登记简洁计划，禁止查阅历史 `runs/` 或重新论证已发布方法。

每个进程日志开头都会明确记录：

```text
outcome: succeeded|failed
success: true|false
exit_code: <Hermes exit code>
finished_at: <UTC timestamp>
failure_summary: <失败时的摘要>
```

```powershell
python skillevo.py run "用户需求" --show-progress
```

也可以在另一个终端查询最近一次工作流，或查询指定 request：

```powershell
python skillevo.py workflow status --latest
python skillevo.py workflow status --request-id req-xxxxxxxx
```

状态结果包含当前 Agent、阶段、能力路由、知识模式、已有产物、重试次数和最后一次失败。

这些设置会消除终端中的中间思考展示，并减少模型往返和无界重试；但当前 Qwen 端点在完整多 Agent 工作流中仍会记录 reasoning token，`reasoning none` 不能解释为服务端数学意义上的绝对零。

## 案例测试集

代表性的能力内、部分覆盖和能力外问题定义在 `scripts/run_case_suite.py`。

```powershell
# 只列出案例，不调用 Hermes
python scripts/run_case_suite.py --list

# 运行单个案例
python scripts/run_case_suite.py --case water_area

# 运行某种预期路由或完整测试集
python scripts/run_case_suite.py --route unmatched
python scripts/run_case_suite.py
```

每个案例都调用相同的 `python skillevo.py run ...` 公开入口。汇总结果写入 `runs/case-suite/<timestamp>/summary.json`，单次工作流产物继续保存在 `runs/<request_id>/`。

测试脚本中的 `case_id` 仅用于选择案例和核对预期路由，不会发送给 Hermes；Hermes 只收到该案例的一段 `user_request`。

## 自主求解与知识演化

完整的双路径、审计结构、候选目录、Add/Modify 语义、批准门槛和 CLI 示例见 [`AUTONOMOUS_AND_EVOLUTION_WORKFLOW.md`](AUTONOMOUS_AND_EVOLUTION_WORKFLOW.md)。运行成功本身不构成知识发布授权。

## GEE 适配器与代理

Hermes 工具 `skillevo_gee_execute` 对应项目的 GEE 适配器。Node runtime 位于 `src/gee/runtime/`，本机配置来自被 Git 忽略的 `config/gee.local.json`。

适配器会清除继承的代理变量，只把配置中的代理显式传给 Node GEE worker。因此 Hermes 直接连接模型服务，Earth Engine 单独使用 GEE 代理。凭据保存在工程外部，项目只引用其路径。

## 安全边界

- 正式分析只读取 `knowledge/published/`；演化先写入 `knowledge/candidates/`。
- Hermes 配置为 `skills.write_approval: true`，其 Skill 写入需要审批。
- Earth Engine 成功执行只证明运行链成功，不证明科学方法有效。
- `raw_GEE_case/` 是知识构建来源，不是运行时正式知识。
- 服务账号凭据和本机代理配置不进入 Git。
