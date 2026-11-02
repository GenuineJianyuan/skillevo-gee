# SkillEvo-GEE 环境、Hermes 版本与依赖说明

> 基线日期：2026-11-02（Asia/Shanghai）
>
> 本文记录当前已验证环境、运行模式、安装顺序和已知依赖风险。密钥、服务账号正文和其他凭据不得写入本文或提交到版本库。

## 1. 一键运行的前提

是的，当前主入口：

```powershell
python skillevo.py run "用户的 GEE 分析需求"
```

依赖本机已经安装并配置好 Hermes。该命令本身不会下载、安装或登录 Hermes，其真实调用链是：

```text
Python 3
  -> hermes chat
  -> skillevo-supervisor Skill
  -> SkillEvo-GEE Hermes 插件
  -> 项目 Python CLI
  -> 可选：Node.js GEE worker
  -> Google Earth Engine
```

因此，“一条命令使用”表示**完成一次环境部署后的一条业务命令**，不是完全无前置依赖的单文件程序。

## 2. 三种运行模式及依赖范围

### 2.1 只检查知识资产

```powershell
python skillevo.py catalog validate
```

需要：

- Python；
- 项目 Python 依赖。

不需要：Hermes、Node.js、GEE 凭据或代理。

### 2.2 运行 Hermes Agent 工作流

```powershell
python skillevo.py run "分析需求"
```

需要：

- Python；
- Hermes 已安装并位于 `PATH`；
- Hermes 已选择模型并配置有效认证；
- 项目 Skills 已加入 Hermes 外部 Skill 目录；
- `skillevo-gee` 插件已安装、启用并能解析项目根目录；
- 当前插件宿主使用的 Hermes Gateway 已就绪。

若本次请求只做知识检查，可以不配置 GEE。若工作流进入真实执行阶段，还需要 2.3 的依赖。

### 2.3 执行 GEE JavaScript

```powershell
python skillevo.py gee execute --script runs/<request_id>/generated.js
```

需要：

- Python；
- Node.js；
- `src/gee/runtime/node_modules`；
- 已启用 Earth Engine 的 Google Cloud project；
- 对该 project 和所用数据有权限的 service account JSON；
- `config/gee.local.json`；
- 当前网络环境要求的 GEE HTTP(S) 代理。

这一模式不要求 Hermes，因为它直接调用项目 GEE executor。

## 3. 当前已验证机器快照

### 3.1 操作系统与基础工具

| 组件 | 当前版本 | 项目要求/说明 |
|---|---:|---|
| Windows | Windows 11, build `10.0.26300` | 当前唯一完成端到端验证的平台 |
| PowerShell | `7.6.5` | 用于安装和诊断命令 |
| Git | `2.53.0.windows.2` | 项目运行非必需；安装/维护 Hermes 时使用 |

### 3.2 Hermes

| 项目 | 当前值 |
|---|---|
| Hermes Agent | `v0.22.5` |
| Hermes 发布日期 | `2026.9.24` |
| Channel | `stable` |
| Local revision | `bf0203a794a0` |
| 安装方式 | `git` |
| 安装目录 | `%LOCALAPPDATA%\hermes\hermes-agent` |
| Hermes 内部 Python | `3.14.9` |
| Hermes OpenAI SDK | `2.24.0` |
| 当前默认模型 | `qwen3.8-flash` |
| 当前 provider | `alibaba-cn` |
| `run` 默认 reasoning | `none` |

说明：

- Hermes 内部 Python 与本工程运行用 Python 是两个环境，不应混为一谈。
- 模型和 provider 会影响代码生成结果。正式论文实验应固定并记录 Hermes 版本、模型、provider、reasoning、知识版本和运行日期。
- 认证凭据来自本机 Hermes/env 配置，不属于项目文件。本文不记录 API key 或 credential ID。
- 当前只在 Hermes `0.22.5` 上做过完整验证；其他版本属于未验证兼容性。

### 3.3 SkillEvo-GEE Hermes 集成

| 项目 | 当前状态 |
|---|---|
| 项目插件 | `skillevo-gee v0.1.0` |
| 插件状态 | enabled |
| 插件隔离模式 | Hermes host process |
| Plugin Doctor | 通过 |
| 注册工具数 | 3 |
| 外部 Skills | 7 个 |
| `skills.write_approval` | `true` |
| Gateway | 正在运行，当前为手动启动 |
| Gateway 登录自启动 | 未安装 |

三个插件工具为：

- `skillevo_catalog`；
- `skillevo_workflow_init`；
- `skillevo_gee_execute`。

当前外部 Skill 目录为：

```text
D:/Project/Paper_Projects/GEE Agent/skillevo/.hermes/skills
```

当前 Gateway 不是 Windows 登录自启动服务。机器重启后，一键运行前需要先执行：

```powershell
hermes gateway ensure
```

如需登录后自动启动，可显式安装：

```powershell
hermes gateway install --if-missing --start-now --start-on-login
```

这会改变本机启动配置，应由使用者自行决定是否执行。

### 3.4 项目 Python

| 组件 | 当前版本 | 声明范围 |
|---|---:|---|
| Python | `3.14.7` | `>=3.11` |
| pip | `26.2.1` | 未固定 |
| setuptools | `84.0.0` | 构建要求 `>=75` |
| pydantic | `2.13.5` | `>=2.7,<3` |
| SkillEvo-GEE | `0.1.0` | 当前工程版本 |

运行时 Python 直接依赖只有 `pydantic`。标准库承担 JSON、Path、subprocess、状态保存和测试等功能。

可选开发依赖：

| 组件 | pyproject 声明 | 当前全局 Python 状态 |
|---|---|---|
| pytest | `>=8` | 未安装 |
| ruff | `>=0.8` | 未安装 |

当前测试使用 `unittest`，所以不安装 pytest 也能执行现有 8 个测试。建议新机器使用项目虚拟环境，不依赖全局 Python 状态。

### 3.5 Node.js 与 Earth Engine runtime

| 组件 | 当前版本 | 声明范围 |
|---|---:|---|
| Node.js | `24.14.1` | `>=20` |
| npm | `11.11.0` | 未固定 |
| `@google/earthengine` | `1.7.31` | 精确固定 |
| `https-proxy-agent` | `9.1.0` | 精确固定 |

Node 直接依赖由以下文件管理：

```text
src/gee/runtime/package.json
src/gee/runtime/package-lock.json
```

当前 lockfile SHA-256：

```text
C60AD534EB54345FCF8CE8527C2AE79BD7655459BDC88B2E1424921339E6A900
```

部署时优先使用 `npm ci --omit=dev`，以复现 lockfile，而不是自动改变依赖版本。

## 4. 本机私有配置

### 4.1 Hermes 配置

当前 Hermes 主配置位于：

```text
%LOCALAPPDATA%\hermes\config.yaml
```

项目依赖以下配置语义：

```yaml
skills:
  write_approval: true
  external_dirs:
    - D:/Project/Paper_Projects/GEE Agent/skillevo/.hermes/skills
```

`write_approval=true` 表示 Hermes 对 Skill 写入执行审批保护。它不等价于领域知识发布审批；`knowledge/published` 仍需项目自己的 candidate/review/publish 流程。

### 4.2 插件安装位置

当前用户插件位于：

```text
%LOCALAPPDATA%\hermes\plugins\skillevo-gee
```

该目录包含插件代码、`plugin.yaml` 和本机项目根指针 `project-root.txt`。项目根指针是机器相关文件，不应提交到公共版本库。

### 4.3 GEE 本机配置

模板：

```text
config/gee.example.json
```

本机文件：

```text
config/gee.local.json
```

结构：

```json
{
  "ee_project": "your-earth-engine-project",
  "node_executable": "node",
  "node_service_account_key_path": "D:/external/path/service-account.json",
  "proxy_url": "http://127.0.0.1:7890"
}
```

当前机器已经配置：

- Earth Engine project；
- Node 可执行文件；
- GEE 代理 `http://127.0.0.1:7890`；
- 外部 service account 路径，且文件存在。

凭据 JSON 保留在工程外部，只通过路径引用。`config/gee.local.json` 已被 `.gitignore` 忽略。

## 5. 网络和代理边界

Hermes 和 GEE 使用不同网络策略：

```text
HermesRunner
  -> 清除 HTTP_PROXY / HTTPS_PROXY / ALL_PROXY
  -> 设置 NO_PROXY=*
  -> Hermes 直接访问模型 provider

GEEExecutor
  -> 清除继承的代理环境变量
  -> 从 config/gee.local.json 读取 proxy_url
  -> 仅将该代理显式传给 Node GEE worker
```

因此，不应在系统环境中为 Hermes 和 GEE 共用一个全局代理。若当前网络不需要 GEE 代理，将 `proxy_url` 设置为 `direct`。

## 6. 新机器部署顺序

以下步骤假设项目已经复制或克隆到目标目录。

### 6.1 安装并配置 Hermes

Hermes 不由本项目自动安装。应按 Hermes 自身安装方式部署，并验证：

```powershell
hermes --version
hermes setup --quick
hermes model
hermes auth list
```

认证应通过 `hermes auth` 管理；`hermes login` 在当前版本中已经标记为 deprecated。

本项目验证版本为：

```text
Hermes Agent v0.22.5
```

### 6.2 创建 Python 虚拟环境

```powershell
cd "D:\Project\Paper_Projects\GEE Agent\skillevo"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

需要开发工具时：

```powershell
python -m pip install -e ".[dev]"
```

安装后可以使用两种等价入口：

```powershell
python skillevo.py catalog validate
skillevo-gee catalog validate
```

### 6.3 安装 Node 依赖

```powershell
cd "D:\Project\Paper_Projects\GEE Agent\skillevo\src\gee\runtime"
npm ci --omit=dev
cd ..\..\..
```

### 6.4 创建 GEE 本机配置

```powershell
Copy-Item config\gee.example.json config\gee.local.json
```

随后编辑 `config/gee.local.json`，填写：

- Earth Engine project ID；
- service account JSON 的外部绝对路径；
- Node 命令或绝对路径；
- GEE 专用代理或 `direct`。

必须确保：

- Google Cloud project 已开通 Earth Engine；
- service account 对 project 和目标资产有权限；
- 凭据文件不是工程内受版本控制的文件。

### 6.5 注册项目 Skills

```powershell
hermes config set skills.write_approval true
hermes config set skills.external_dirs "D:/Project/Paper_Projects/GEE Agent/skillevo/.hermes/skills"
```

然后检查：

```powershell
hermes config get skills.write_approval
hermes config get skills.external_dirs
```

### 6.6 安装项目插件

当前插件是 workspace-owned 手工插件，不在 Hermes 公共插件目录中。PowerShell 示例：

```powershell
$projectRoot = "D:\Project\Paper_Projects\GEE Agent\skillevo"
$pluginSource = Join-Path $projectRoot ".hermes\plugins\skillevo-gee"
$pluginTarget = Join-Path $env:LOCALAPPDATA "hermes\plugins\skillevo-gee"

New-Item -ItemType Directory -Force -Path $pluginTarget | Out-Null
Copy-Item -Recurse -Force -Path "$pluginSource\*" -Destination $pluginTarget
Set-Content -LiteralPath (Join-Path $pluginTarget "project-root.txt") `
  -Value ($projectRoot -replace '\\', '/') -Encoding utf8

hermes plugins enable skillevo-gee --no-allow-tool-override
hermes plugins doctor skillevo-gee
```

该插件不需要覆盖 Hermes 内置工具。

### 6.7 启动或确认 Gateway

```powershell
hermes gateway ensure
hermes gateway status
```

更新插件代码或项目指针后，应重启 Gateway：

```powershell
hermes gateway restart
```

### 6.8 最终验证

```powershell
python skillevo.py catalog validate
hermes chat --reasoning none -q "Reply with exactly: ok"
python skillevo.py run "只读调用 skillevo_catalog validate，只返回 ok 和 asset_count；不要执行 GEE。"
```

需要验证真实 GEE 时，再使用可信的本地脚本执行：

```powershell
python skillevo.py gee execute --script runs/<request_id>/generated.js
```

## 7. 当前健康检查结果

截至本文基线日期：

| 检查 | 结果 |
|---|---|
| Hermes 本体查询 | 正常 |
| Hermes 配置检查 | Required 项无缺失 |
| `skillevo-gee` 插件 | enabled |
| Plugin Doctor | 通过，3 个工具注册成功 |
| Gateway | 运行中 |
| Python 知识目录校验 | `ok=true`，23 个资产 |
| Python 自动测试 | 8/8 通过 |
| Node 直接依赖 | 安装完整 |
| GEE 云端冒烟 | 3 成功、0 失败 |

## 8. 已知依赖风险

### 8.1 Node 传递依赖漏洞

2026-11-02 执行：

```powershell
npm audit --omit=dev
```

报告：

- 3 个 moderate；
- 6 个 high；
- 0 个 critical；
- 合计 9 个 vulnerability entries。

问题主要来自 `@google/earthengine@1.7.31` 引入的旧版 `googleapis`、`google-auth-library`、`node-forge`、`qs` 和 `uuid` 等传递依赖。npm 对部分链路报告 `fixAvailable=false`。

当前项目没有自动执行 `npm audit fix --force`，因为这可能改变 Earth Engine SDK 依赖图并破坏已验证行为。发布或论文冻结环境前应：

1. 检查新版 Earth Engine SDK；
2. 在独立分支升级；
3. 重新执行全部 GEE 冒烟和案例回归；
4. 重新记录 lockfile hash 和 audit 结果；
5. 如无法升级，在论文复现材料中保留风险说明。

### 8.2 Hermes 与项目未形成单一锁文件

Hermes 是外部应用，不在 `pyproject.toml` 中。因此 Python lockfile 不能保证 Hermes 版本、模型和插件宿主行为一致。正式实验应额外保存：

- `hermes --version` 输出；
- 默认模型和 provider；
- 插件版本与 Doctor 结果；
- Skill 目录的版本快照；
- Gateway 模式；
- 运行命令和 reasoning 设置。

### 8.3 Python 依赖目前只有范围，没有锁文件

`pyproject.toml` 使用 `pydantic>=2.7,<3`，没有锁定精确 Python 依赖。当前可复现版本是 `pydantic 2.13.5`。论文实验冻结前建议生成 requirements lock 或采用支持锁定的环境管理工具。

### 8.4 模型输出并非完全确定

即使固定代码和依赖，Hermes 背后的模型服务仍可能更新。实验记录应保存模型名称、provider、日期、reasoning、完整输入和运行产物；需要严格比较时还应固定采样参数或使用 provider 支持的确定性设置。

## 9. 不应提交的内容

以下内容已经或应当被忽略：

- `config/gee.local.json`；
- service account JSON；
- Hermes API keys 和认证状态；
- `.hermes/plugins/skillevo-gee/project-root.txt`；
- `runs/`；
- Python 虚拟环境；
- `node_modules/`；
-缓存和构建产物。

可以提交：

- `config/gee.example.json`；
- `src/gee/runtime/package.json`；
- `src/gee/runtime/package-lock.json`；
- 插件源代码和 `plugin.yaml`；
- Skill 文档；
- published knowledge；
- 不含密钥的测试与复现说明。

## 10. 最小日常启动检查

每次开始工作前建议运行：

```powershell
cd "D:\Project\Paper_Projects\GEE Agent\skillevo"
hermes --version
hermes gateway ensure
python skillevo.py catalog validate
```

若要执行 GEE，再检查：

```powershell
Test-Path config\gee.local.json
Test-Path src\gee\runtime\node_modules\@google\earthengine\package.json
node --version
```

最后执行统一入口：

```powershell
python skillevo.py run "用户的 GEE 分析需求"
```

