# SkillEvo-GEE 文档索引

本文区分当前实现说明、演化规范、Agent 行为约束、正式领域知识和历史来源材料。

## 当前实现说明

| 文档 | 包含内容 | 主要用途 |
|---|---|---|
| `README.md` | 项目目标、知识层次、快速启动、案例命令和安全边界 | 项目入口和日常操作 |
| `PROJECT_OVERVIEW.md` | 研究动机、知识表示、Agent 职责、双执行路径和演化研究定位 | 核对论文与系统总体思路 |
| `CURRENT_ARCHITECTURE_AND_RESEARCH_PATH.md` | 当前目录、已实现与部分实现功能、成熟度、论文表述边界和路线图 | 对照当前代码与论文贡献 |
| `AUTONOMOUS_AND_EVOLUTION_WORKFLOW.md` | 正式/自主路径、运行产物、审计门槛、Add/Modify 生命周期和发布命令 | 检查能力缺口处理与演化闭环 |
| `ENVIRONMENT_AND_DEPENDENCIES.md` | Hermes 版本、Python/Node/GEE 依赖、代理边界、插件/Gateway 配置和健康检查 | 复现本地运行环境 |

若文档描述不一致，当前代码和测试是运行行为的最终依据；`CURRENT_ARCHITECTURE_AND_RESEARCH_PATH.md` 说明实现状态，`PROJECT_OVERVIEW.md` 说明更广的研究框架。

## 演化规范

| 文档 | 内容 |
|---|---|
| `knowledge/evolution/skill_evolution.md` | 演化边界、候选优先规则、操作类型和发布原则 |
| `knowledge/evolution/add_skill.md` | 如何把审计合格的自主结果拆解为新 Task/Subtask/Example |
| `knowledge/evolution/modify_skill.md` | 如何依据审计证据修正或扩展已有资产 |
| `knowledge/evolution/merge_skills.md` | 未来 Merge 的语义比较和引用迁移规则 |
| `knowledge/evolution/templates/task.md` | Task 的固定 Markdown 结构 |
| `knowledge/evolution/templates/subtask.md` | 包含内嵌 Example 的 Subtask 固定结构 |

当前 CLI 已实现 Add/Modify 候选的创建、验证、批准、拒绝和发布。Merge 仍是后续操作。

## Agent 行为约束

`.hermes/skills/` 下的七个文件定义运行时角色：

| Skill | 职责约束 |
|---|---|
| `skillevo-supervisor` | 阶段顺序、正式/自主分支、重试和候选控制 |
| `skillevo-requirement-agent` | 需求规范化及仅依据 Capability 的首级路由 |
| `skillevo-data-agent` | 数据集、覆盖、波段、尺度和适用性核查 |
| `skillevo-planning-agent` | 正式 Task/Subtask 规划或隔离的自主规划 |
| `skillevo-code-agent` | 在正式或自主模式下依据方案生成 GEE JavaScript |
| `skillevo-audit-agent` | 执行/科学审计及 Add/Modify/Reject/More-evidence 建议 |
| `skillevo-evolution-agent` | 候选拆解、验证、人工批准和发布规则 |

它们是由 Hermes 调度的角色型 Skill，不是七个长期运行的操作系统进程。

## 正式领域知识

| 位置 | 内容 |
|---|---|
| `knowledge/published/capabilities.md` | 业务能力分类及 `matched/partial/unmatched` 路由语义 |
| `knowledge/published/tasks/` | 带 Required/Optional 工作流的完整分析目标 |
| `knowledge/published/subtasks/` | 带固定约束和内嵌 Example 的可复用操作 |
| `knowledge/candidates/` | 尚未发布、等待验证或批准的 Add/Modify 候选 |

正式知识在分析运行期间只读。候选发布是一个独立且必须明确批准的操作。

## 来源与历史材料

| 文档或位置 | 状态 |
|---|---|
| `SkillEvo-GEE_开发实施指导大纲-初版v5.md` | 原始设计基线；可用于理解意图，但不是当前实现细节的最终依据 |
| `raw_GEE_case/` | Task/Subtask 的来源案例；运行时不会作为正式知识加载 |

原始大纲可能保留已经调整的概念，例如旧的独立 Example 层或早期能力缺口处理方式。检查当前系统时应优先使用上面的当前实现说明。
