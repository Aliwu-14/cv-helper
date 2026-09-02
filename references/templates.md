# 简历模板代码片段

本文件提供三种导出格式的模板代码：LaTeX（排版质量最佳，适合学术/技术岗位）、Marp（Markdown 转 PPT，可用于路演/面试演示）、HTML（可嵌入网页或通过浏览器打印为 PDF）。

> **重要**：内容结构完全由 cv-helper skill 生成，本文件只负责排版样式。导出前请先用 `validate_output.py` 和 `validate_section.py` 校验内容。

## 目录

1. [LaTeX 模板](#latex-模板)
2. [Marp 幻灯片模板](#marp-幻灯片模板)
3. [HTML 单页模板](#html-单页模板)
4. [从 Markdown 到各类格式的工作流](#从-markdown-到各类格式的工作流)

---

## LaTeX 模板

### 依赖

```latex
% 在导言区加入
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage{enumitem}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage{booktabs}
\usepackage{titlesec}

% 字体设置（macOS / Windows / Linux 三选一）
% macOS:
\setmainfont{Times New Roman}
\setsansfont{Helvetica Neue}
\setCJKmainfont{PingFang SC}

% Windows:
% \setmainfont{Times New Roman}
% \setsansfont{Segoe UI}
% \setCJKmainfont{微软雅黑}

% 标题格式
\titleformat{\section}{\large\bfseries}{}{0em}{}
\titlespacing*{\section}{0pt}{6pt}{6pt}
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}
\titlespacing*{\subsection}{0pt}{4pt}{4pt}

% 去除页面编号
\pagestyle{empty}
```

### 完整简历模板

```latex
\documentclass[10pt, a4paper]{article}

% ── 导言区 ──────────────────────────────────────────────────────────────
\usepackage[left=1.8cm, right=1.8cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage{enumitem}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage{booktabs}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{color}

% 字体
\setmainfont{Times New Roman}
\setsansfont{Helvetica Neue}
\setCJKmainfont{苹方-简}

% 颜色定义（ATS 安全色）
\definecolor{accent}{RGB}{31, 78, 121}   % #1F4E79
\definecolor{header}{RGB}{44, 62, 80}     % 深灰

% 标题格式
\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{\uppercase}
\titlespacing*{\section}{0pt}{8pt}{4pt}
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}
\titlespacing*{\subsection}{0pt}{4pt}{2pt}

% bullet 样式
\setlist{
  leftmargin=0pt,
  labelsep=0.3em,
  itemsep=2pt,
  topsep=2pt,
}

% 去除页面编号
\pagestyle{empty}

\begin{document}

% ── 个人总结（四行）────────────────────────────────────────────────────
\section*{Personal Summary}

\begin{itemize}
  \item[\bfseries 1.] 第一行：职业定位 + 核心能力标签（2–3 个关键词）
  \item[\bfseries 2.] 第二行：可量化技能或方法论（强动词 + 工具 + 成果）
  \item[\bfseries 3.] 第三行：行业经验深度或项目亮点（1–2 个量化锚点）
  \item[\bfseries 4.] 第四行：语言/证书 + 软技能信号（可量化 + 自然能力语言）
\end{itemize}

% ── 基本信息 ───────────────────────────────────────────────────────────
\section*{Contact}

\begin{tabular}{l l}
  Name     & Your Full Name  \\
  Phone    & +86 xxx xxxx xxxx \\
  Email    & \hrefmailto{your.email@example.com}  \\
  Location & City, Country   \\
  LinkedIn & \href{https://linkedin.com/in/your-id}{linkedin.com/in/your-id} \\
  GitHub   & \href{https://github.com/your-id}{github.com/your-id} \\
\end{tabular}

% ── 教育背景 ───────────────────────────────────────────────────────────
\section*{Education}

\subsection*{University Name | Degree | Major | Start -- End}
\begin{itemize}
  \item GPA X.X/X.X（Top X\%）; Relevant coursework: Course 1, Course 2
\end{itemize}

% ── 经历 ────────────────────────────────────────────────────────────────
\section*{Experience}

\subsection*{Company Name | Job Title | Start -- End}
\begin{itemize}
  \item Led / Built / Drove ... [verb + object + quantitative result + method/tool + business value]
  \item ...
\end{itemize}

\subsection*{Company Name | Job Title | Start -- End}
\begin{itemize}
  \item ...
\end{itemize}

% ── 技能 ────────────────────────────────────────────────────────────────
\section*{Skills}

\begin{itemize}
  \item Tools \& Platforms: tool1 (proficient), tool2 (familiar)
  \item Programming \& Query: language1 (proficient), language2 (familiar)
  \item Methods \& Frameworks: method1 (familiar), method2 (familiar)
  \item Language / Certifications: language, certification
\end{itemize}

% ── 奖项与证书 ──────────────────────────────────────────────────────────
\section*{Awards \& Certifications}

\begin{itemize}
  \item Year Award Name --- Organization --- Quantitative anchor (Top X\% / rank / score)
\end{itemize}

\end{document}
```

### ATS 友好的 LaTeX 注意事项

```latex
% ✅ 推荐：使用标准文档类，单栏布局
% ❌ 避免：使用双栏 (twocolumn)、图表浮动体 (figure/table)
% ❌ 避免：自定义颜色字体导致 PDF 解析失败
% ✅ 推荐：PDF 页面尺寸 = A4，字体嵌入
```

---

## Marp 幻灯片模板

Marp 将 Markdown 转成可演示的 PPT，适合面试自我介绍、线上评估、或发送给 HR 的视觉版简历。

### 安装

```bash
pip install marp-cli
# 或 VS Code 插件 Marp for VS Code
```

### 简历幻灯片模板（每节一页）

```markdown
---
marp: true
theme: default
paginate: true
math: katex
backgroundColor: #ffffff
color: #2c3e50
style: |
  section {
    font-family: 'Helvetica Neue', 'PingFang SC', '微软雅黑', sans-serif;
    font-size: 24px;
  }
  strong { color: #1F4E79; }
  h1 { color: #1F4E79; border-bottom: 2px solid #1F4E79; }
  h2 { color: #1F4E79; }
  table { font-size: 20px; }
  blockquote { border-left: 4px solid #1F4E79; color: #555; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Your Name
**Job Title** | your.email@example.com | +86 xxx xxxx xxxx

---

## Personal Summary

1. **职业定位 + 核心能力标签**（2–3 个关键词）
2. **可量化技能或方法论**（强动词 + 工具 + 成果）
3. **行业经验深度或项目亮点**（1–2 个量化锚点）
4. **语言/证书 + 软技能信号**（可量化 + 自然能力语言）

---

## Experience

### Company A | Job Title | 2023 – Present

- **Led** merchant backend redesign, reducing operation steps by 22%
- **Coordinated** 3 R&D squads, increasing release frequency by 35%
- **Built** funnel monitoring with SQL + Python, 12 consecutive weekly reports adopted

### Company B | Job Title | 2021 – 2023

- **Led** competitive benchmark research, plan adopted by 3 BUs
- **Wrote** 6 executive reports, 5 adopted as quarterly strategy material

---

## Skills

| Category | Details |
|----------|---------|
| Tools | Figma (proficient), Jira (familiar), GA4 (applied) |
| Programming | Python (proficient), SQL (proficient), TypeScript (learning) |
| Methods | A/B Testing (familiar), PMO/WBS/RAID (familiar) |
| Language | English CET-6 550, PMP Certified |

---

## Education

**University Name | Degree | Major | 2020 – 2023**
- GPA X.X/X.X (Top X%); Relevant coursework: Course 1, Course 2

---

## Awards \& Certifications

- **2024** CFA Level II Pass — CFA Institute — Global Top 35%
- **2023** National Mathematical Modeling Contest — 1st Prize — Top 1%

<!-- _class: lead -->
<!-- _paginate: false -->

# Thank You
your.email@example.com | linkedin.com/in/your-id
```

### 导出命令

```bash
# 转 PDF
marp resume.md --pdf --allow-local-files

# 转 PPTX
marp resume.md --pptx --allow-local-files

# 转 HTML 单页
marp resume.md --html --allow-local-files
```

---

## HTML 单页模板

纯 HTML + CSS，无需任何构建工具，可直接在浏览器中打开并打印为 PDF。ATS 兼容性最优。

### 完整 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Name — Resume</title>
  <style>
    /* ── 重置与基础 ─────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Helvetica Neue', 'PingFang SC', '微软雅黑', Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.5;
      color: #2c3e50;
      background: #fff;
      max-width: 210mm;          /* A4 宽度 */
      margin: 0 auto;
      padding: 15mm 18mm;
    }

    /* ── 颜色 ────────────────────────────────────── */
    :root {
      --accent: #1F4E79;
      --text: #2c3e50;
      --muted: #555;
      --border: #ddd;
    }

    /* ── 标题样式（ATS 友好）─────────────────────── */
    h1 { font-size: 18pt; font-weight: 700; color: var(--accent); margin-bottom: 2pt; }
    h2 { font-size: 11pt;  font-weight: 700; color: var(--accent); border-bottom: 1.5px solid var(--accent); padding-bottom: 2pt; margin: 10pt 0 5pt; text-transform: uppercase; letter-spacing: 0.5px; }
    h3 { font-size: 10pt;  font-weight: 600; color: var(--text); margin: 6pt 0 2pt; }
    p  { font-size: 10pt;  color: var(--text); }

    /* ── 个人信息行 ─────────────────────────────── */
    .contact {
      display: flex;
      flex-wrap: wrap;
      gap: 6pt 14pt;
      font-size: 9.5pt;
      color: var(--muted);
      margin-bottom: 8pt;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6pt;
    }
    .contact span::before { content: attr(data-label) "："; }

    /* ── 四行总结 ────────────────────────────────── */
    .summary {
      list-style: none;
      padding: 0;
      margin: 0 0 8pt;
    }
    .summary li {
      font-size: 10pt;
      padding-left: 18pt;
      position: relative;
      margin-bottom: 3pt;
    }
    .summary li::before {
      content: attr(data-n) ". ";
      font-weight: 700;
      color: var(--accent);
      position: absolute;
      left: 0;
    }

    /* ── 经历模块 ────────────────────────────────── */
    .experience-item { margin-bottom: 8pt; }
    .exp-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 2pt;
    }
    .exp-company { font-weight: 700; color: var(--text); }
    .exp-dates   { font-size: 9pt; color: var(--muted); }
    .exp-bullets {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .exp-bullets li {
      padding-left: 12pt;
      position: relative;
      margin-bottom: 2pt;
      font-size: 10pt;
    }
    .exp-bullets li::before { content: "–"; position: absolute; left: 0; color: var(--accent); }

    /* ── 技能模块 ────────────────────────────────── */
    .skills-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 10pt;
    }
    .skills-table td { vertical-align: top; padding: 1pt 6pt 1pt 0; }
    .skills-table td:first-child { font-weight: 600; white-space: nowrap; width: 30%; color: var(--text); }
    .skills-table td:last-child  { color: var(--muted); }

    /* ── 奖项模块 ────────────────────────────────── */
    .award-item {
      display: flex;
      justify-content: space-between;
      font-size: 10pt;
      margin-bottom: 2pt;
    }
    .award-org { color: var(--muted); font-size: 9pt; }

    /* ── 打印优化 ────────────────────────────────── */
    @media print {
      body { padding: 0; margin: 0; }
      h2 { break-before: avoid; }
      .experience-item { break-inside: avoid; }
      @page {
        size: A4;
        margin: 12mm 15mm;
      }
    }
  </style>
</head>
<body>

  <!-- 姓名 + 联系方式 -->
  <h1>Your Name</h1>
  <div class="contact">
    <span data-label="电话">+86 xxx xxxx xxxx</span>
    <span data-label="邮箱"><a href="mailto:your.email@example.com">your.email@example.com</a></span>
    <span data-label="城市">City, Country</span>
    <span data-label="LinkedIn"><a href="https://linkedin.com/in/your-id">linkedin.com/in/your-id</a></span>
  </div>

  <!-- 个人总结（四行） -->
  <h2>个人总结</h2>
  <ol class="summary">
    <li data-n="1">职业定位 + 核心能力标签（2–3 个关键词）</li>
    <li data-n="2">可量化技能或方法论（强动词 + 工具 + 成果）</li>
    <li data-n="3">行业经验深度或项目亮点（1–2 个量化锚点）</li>
    <li data-n="4">语言/证书 + 软技能信号（可量化 + 自然能力语言）</li>
  </ol>

  <!-- 教育背景 -->
  <h2>Education</h2>
  <div class="experience-item">
    <div class="exp-header">
      <span class="exp-company">University Name</span>
      <span class="exp-dates">2020 – 2023</span>
    </div>
    <p>Degree | Major</p>
    <ul class="exp-bullets">
      <li>GPA X.X/X.X（Top X%）; Relevant coursework: Course 1, Course 2</li>
    </ul>
  </div>

  <!-- 工作经历 -->
  <h2>Experience</h2>

  <div class="experience-item">
    <div class="exp-header">
      <span class="exp-company">Company A</span>
      <span class="exp-dates">2023 – Present</span>
    </div>
    <p><em>Job Title</em></p>
    <ul class="exp-bullets">
      <li>Led merchant backend redesign, reducing operation steps by 22%</li>
      <li>Coordinated 3 R&D squads, increasing release frequency by 35%</li>
      <li>Built funnel monitoring with SQL + Python, 12 consecutive weekly reports adopted</li>
    </ul>
  </div>

  <div class="experience-item">
    <div class="exp-header">
      <span class="exp-company">Company B</span>
      <span class="exp-dates">2021 – 2023</span>
    </div>
    <p><em>Job Title</em></p>
    <ul class="exp-bullets">
      <li>Led competitive benchmark research, plan adopted by 3 BUs</li>
      <li>Wrote 6 executive reports, 5 adopted as quarterly strategy material</li>
    </ul>
  </div>

  <!-- 技能 -->
  <h2>Skills</h2>
  <table class="skills-table">
    <tr><td>工具与平台</td><td>Figma（熟练）, Jira（熟悉）, GA4（能够应用）</td></tr>
    <tr><td>编程与查询</td><td>Python（熟练）, SQL（熟练）, TypeScript（了解边界）</td></tr>
    <tr><td>方法与框架</td><td>A/B Testing（熟悉）, PMO/WBS/RAID（熟悉）</td></tr>
    <tr><td>语言/证书</td><td>英语 CET-6 550, PMP 已认证</td></tr>
  </table>

  <!-- 奖项 -->
  <h2>Awards &amp; Certifications</h2>
  <div class="award-item">
    <span>2024 CFA Level II 通过 — CFA Institute — 全球 Top 35%</span>
  </div>
  <div class="award-item">
    <span>2023 全国大学生数学建模竞赛 — 国家级一等奖 — Top 1%</span>
  </div>

</body>
</html>
```

### 导出为 PDF 的两种方法

**方法 1：浏览器打印（推荐，ATS 最友好）**

```bash
# 1. 在浏览器中打开上面的 HTML 文件
# 2. Ctrl+P 打开打印对话框
# 3. 目标打印机选择 "另存为 PDF"
# 4. 布局：横向；边距：无；背景图形：✓（打勾）
```

**方法 2：wkhtmltopdf（命令行）**

```bash
# 安装：https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf
pip install pdfkit
```

```python
import pdfkit

pdfkit.from_file(
    "resume.html",
    "resume.pdf",
    options={
        "page-size": "A4",
        "margin-top": "12mm",
        "margin-bottom": "12mm",
        "margin-left": "15mm",
        "margin-right": "15mm",
        "encoding": "UTF-8",
        "no-outline": None,
        "enable-local-file-access": None,
    }
)
```

---

## 从 Markdown 到各类格式的工作流

```
cv-helper 生成的 Markdown
        │
        ├── ① 内容校验
        │   python scripts/validate_output.py resume.md
        │   python scripts/validate_section.py --mode experience resume.md
        │
        ├── ② 导出 LaTeX → PDF
        │   xelatex resume.tex  （需要本机安装 LaTeX 发行版）
        │
        ├── ③ 导出 Marp → PPTX / PDF
        │   marp resume.md --pptx
        │
        └── ④ 导出 HTML → 浏览器打印 PDF
            直接用 Chrome / Edge 打印（见上方方法 1）
            或 wkhtmltopdf resume.html resume.pdf（方法 2）
```

> **ATS 小贴士**：ATS 系统（Workday / Greenhouse / iCIMS）最喜欢的是纯文本或简单 HTML 的 PDF。LaTeX 生成的 PDF 如果字体嵌入不当，ATS 可能无法正确解析。建议优先导出 HTML → PDF 格式提交给招聘系统。
