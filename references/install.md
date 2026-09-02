# 安装指南 — Claude / Codex / Cursor / OpenClaw / Harness

本 Skill 兼容所有支持 Skill 目录加载机制的 Agent 客户端。下面是 5 种主流环境的安装步骤。

## 目录

1. [通用原则](#通用原则)
2. [Claude Code](#claude-code)
3. [Cursor](#cursor)
4. [Codex](#codex)
5. [OpenClaw](#openclaw)
6. [通用 Harness](#通用-harness)
7. [本地克隆验证](#本地克隆验证)
8. [更新 Skill](#更新-skill)
9. [故障排查](#故障排查)

---

## 通用原则

所有客户端的 Skill 加载机制都遵循一个共同约定：

- 用户目录下存在一个 `skills/` 文件夹；
- 每个 Skill 是该文件夹下的一个**独立子目录**；
- Skill 根目录必须包含一个 `SKILL.md` 文件，包含 YAML frontmatter（`name` + `description`）；
- 客户端启动时扫描该目录，按 `name` 注册 Skill；
- 用户在对话中提到 Skill 名称或触发关键词时，Agent 加载对应 Skill 的 `SKILL.md` + 同目录的其他辅助文件（`references/`、`scripts/` 等）。

`cv-helper` 的目录结构（无论装到哪个客户端都必须保留）：

```
cv-helper/
├── SKILL.md                          ← 入口文件，必须有
├── README.md
├── references/
│   ├── intake_flow.md                ← 多轮引导状态机
│   ├── install.md                    ← 本文件
│   ├── methodology.md
│   ├── patterns.md
│   ├── lexicon.md
│   ├── ats_layout.md
│   ├── recruiter_habits.md
│   ├── interview_prep.md
│   ├── templates.md
│   └── examples.md
└── scripts/
    ├── validate_output.py
    ├── validate_output_en.py
    ├── validate_section.py
    ├── validate_section_en.py
    └── test_*.py
```

**安装步骤通用模板**：

1. 在用户主目录下找到对应客户端的 `skills/` 路径（见下表）；
2. 克隆本仓库到该路径：
   ```bash
   git clone https://github.com/Aliwu-14/cv-helper.git <skills_dir>/cv-helper
   ```
3. （可选）把仓库里 `scripts/` 设为可执行：
   ```bash
   chmod +x <skills_dir>/cv-helper/scripts/*.py
   ```
4. 重启客户端，使 Skill 生效。

---

## Claude Code

`~/.claude/skills/` 是 Claude Code 默认扫描路径。

### macOS / Linux

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Aliwu-14/cv-helper.git ~/.claude/skills/cv-helper
```

### Windows (PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
git clone https://github.com/Aliwu-14/cv-helper.git "$env:USERPROFILE\.claude\skills\cv-helper"
```

### 验证

打开 Claude Code，对话中输入：

> 帮我用 cv-helper 生成一份简历

Claude 应回复开场白并开始问基本信息。

---

## Cursor

`~/.cursor/skills/` 是 Cursor 默认扫描路径。

### macOS / Linux

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/Aliwu-14/cv-helper.git ~/.cursor/skills/cv-helper
```

### Windows

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\skills"
git clone https://github.com/Aliwu-14/cv-helper.git "$env:USERPROFILE\.cursor\skills\cv-helper"
```

### 验证

在 Cursor 聊天中输入：

> @cv-helper 帮我定制一份中文简历

或直接说：

> 帮我用 cv-helper 生成一份简历

---

## Codex

`~/.codex/skills/` 是 Codex 默认扫描路径。

### macOS / Linux

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Aliwu-14/cv-helper.git ~/.codex/skills/cv-helper
```

### Windows

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
git clone https://github.com/Aliwu-14/cv-helper.git "$env:USERPROFILE\.codex\skills\cv-helper"
```

### 验证

在 Codex 命令行启动后，对话里输入：

> 加载 cv-helper 并帮我写一份简历

---

## OpenClaw

`~/.openclaw/skills/` 是 OpenClaw 默认扫描路径。

### macOS / Linux

```bash
mkdir -p ~/.openclaw/skills
git clone https://github.com/Aliwu-14/cv-helper.git ~/.openclaw/skills/cv-helper
```

### Windows

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\skills"
git clone https://github.com/Aliwu-14/cv-helper.git "$env:USERPROFILE\.openclaw\skills\cv-helper"
```

### 验证

在 OpenClaw 客户端对话中：

> 用 cv-helper 帮我生成一份简历

---

## 通用 Harness

很多自建 Agent Harness 使用 `~/.harness/skills/` 或环境变量 `HARNESS_SKILLS_DIR` 指定路径。

### 默认路径

```bash
mkdir -p ~/.harness/skills
git clone https://github.com/Aliwu-14/cv-helper.git ~/.harness/skills/cv-helper
```

### 自定义路径

如果你的 Harness 配置文件里指定了 `skills_dir`：

```yaml
# harness.yaml
skills_dir: /opt/my-harness/skills
```

把 Skill 装到对应位置：

```bash
git clone https://github.com/Aliwu-14/cv-helper.git /opt/my-harness/skills/cv-helper
```

### Docker / 容器化部署

如果 Harness 跑在容器里：

```dockerfile
RUN git clone https://github.com/Aliwu-14/cv-helper.git /root/.harness/skills/cv-helper
```

或挂载：

```bash
docker run -v ~/.harness/skills:/root/.harness/skills my-harness
```

---

## 本地克隆验证

不论装到哪个客户端，安装后都应能跑校验脚本：

```bash
cd ~/.cursor/skills/cv-helper/scripts   # 或其他客户端路径
python -m unittest test_validate_output.py test_validate_section.py \
    test_validate_output_en.py test_validate_section_en.py
```

期望输出：`Ran 88 tests in 1.Xs OK`

---

## 更新 Skill

```bash
cd ~/.cursor/skills/cv-helper   # 或对应路径
git pull origin main
python -m unittest scripts/test_*.py
```

如果有破坏性变更，README.md 与 CHANGELOG 会说明如何迁移。

---

## 故障排查

### Skill 没被加载

1. 检查 `SKILL.md` 是否存在且包含 YAML frontmatter：
   ```bash
   head -3 ~/.cursor/skills/cv-helper/SKILL.md
   ```
   应输出：
   ```
   ---
   name: cv-helper
   description: …
   ```
2. 检查 `name` 字段值是否匹配 `cv-helper`（区分大小写）。
3. 重启客户端。

### Agent 不按引导流程走

1. 检查 `references/intake_flow.md` 是否随仓库一起拉到本地。
2. 在对话中显式提示 Agent：
   > 请按 cv-helper 的 intake_flow.md 状态机，一项一项问我。

### 校验脚本找不到

```bash
cd ~/.cursor/skills/cv-helper
ls scripts/
# 应该有 validate_output.py validate_section.py validate_output_en.py validate_section_en.py
```

如果 `scripts/` 是空目录或缺失，重新 `git pull`。

### 路径含空格或中文

部分 Windows 路径含空格或中文（如 `C:\Users\中文名\...`），客户端可能无法解析。建议把 Skill 装到 `C:\Users\用户名\.cursor\skills\` 这种**纯 ASCII 路径**下。

### 多客户端并存

可以**同时**在多个客户端下安装同一份 Skill，路径各自独立：

```bash
git clone https://github.com/Aliwu-14/cv-helper.git ~/.claude/skills/cv-helper
git clone https://github.com/Aliwu-14/cv-helper.git ~/.cursor/skills/cv-helper
git clone https://github.com/Aliwu-14/cv-helper.git ~/.codex/skills/cv-helper
```

各客户端独立更新，互不影响。