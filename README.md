# paper-reading

`paper-reading` 是一个AI辅助论文阅读的 Codex Skill。给它一篇论文，它会整理研究问题、方法和发现，并把核心结论定位到实际查阅版本的页码、图表、公式或章节。输出为中文 Markdown，保留 DOI、原文链接和关键英文术语。

可以从 **PDF 附件或本地路径、DOI、论文网页、PDF 直链**开始。也支持本地 Markdown、纯文本和 HTML。DOCX 通过可用的文档读取或转换工具处理。

## 安装

将完整的 `skills/paper-reading` 目录放到用户级 `~/.agents/skills/`，即可在不同项目中使用。以下命令适用于首次安装。如果目标位置已有同名 Skill，请先确认要保留的版本。 [Codex 技能安装文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

**Windows PowerShell**

```powershell
git clone https://github.com/illhanna/paper-reading-skills.git
Set-Location paper-reading-skills
$skillsDir = Join-Path $env:USERPROFILE '.agents/skills'
$target = Join-Path $skillsDir 'paper-reading'
if (Test-Path -LiteralPath $target) { throw "Skill 已存在：$target" }
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
Copy-Item -LiteralPath 'skills/paper-reading' -Destination $target -Recurse
```

**macOS / Linux**

```bash
git clone https://github.com/illhanna/paper-reading-skills.git
cd paper-reading-skills
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/paper-reading" ]; then
  printf '%s\n' 'paper-reading 已安装，请先确认要保留的版本。'
else
  cp -R skills/paper-reading "$HOME/.agents/skills/"
fi
```

在 Codex 中输入 `$paper-reading` 选择该 Skill。若未出现在选择列表中，重新启动 Codex 后再试。

## 快速开始

附上 PDF 后，可以直接发送下面的请求。不指定模式时使用 **Standard**。

> 用 $paper-reading 阅读这篇论文。重点解释作者如何控制变量，并把主要结论对应到原文图表。

也可以指定 DOI、模式和关注点。

> 用 $paper-reading 以 Deep 模式阅读 10.1080/14686996.2025.2587391。请推导工程应变与 Hencky 应变的关系，并说明 Fig. 4 支撑哪些结论。

需要 Markdown 文件时，在请求里给出保存路径。未指定路径时，Codex 会在回复中交付笔记。

## 阅读模式

| 模式                       | 主要产出                                                                               |
| -------------------------- | -------------------------------------------------------------------------------------- |
| **Quick**            | 速览背景、研究空白、科学问题、方法、发现、创新和局限，并为主要发现附上原文定位。       |
| **Standard**（默认） | 建立核心结论与证据表，解释决定性的图表、公式和术语。                                   |
| **Deep**             | 逐步推导关键公式，核对假设、量纲及适用条件，逐面板读图并审查对照和替代解释。           |
| **Reproduce**        | 梳理软件版本、输入、参数、预期结果和验证判据，记录缺失项与执行状态。默认交付复现方案。 |

原创研究、综述和软件与算法论文分别使用对应模板。材料与高分子论文关注体系、制备或建模、表征和结构–性能关系。MD 论文还会按需核对力场、系综、时间步长、平衡与采样及有限尺寸效应。

## 笔记如何追溯原文

笔记开头记录 DOI、实际阅读版本、来源链接和查阅范围。每条核心结论都有编号，来源类别使用 **原文事实、作者观点、AI 推断、外部资料** 四种标记。PDF 文件页序从 1 开始，能确认印刷页码时另记。网页和无固定页码的文件按章节或锚点定位。

| 结论 ID | 结论                                                                                      | 来源类别 | 证据与定位             | 支撑与边界                           |
| ------- | ----------------------------------------------------------------------------------------- | -------- | ---------------------- | ------------------------------------ |
| C1      | 升高 Lennard–Jones 截断以保留吸引尾后，柔性链在所测高温状态点的均方位移（MSD）变化较小。 | 原文事实 | P1 PDF p. 4–5，Fig. 1 | 限于图示珠簧模型的链长、密度和温度。 |

示例中的 P1 指 Grest 论文的 arXiv v1 预印本。 [示例原文](https://arxiv.org/pdf/1610.00391v1)

只有摘要可查时，笔记会标明覆盖范围。PDF 抽取失败时可尝试页面渲染或可用的本地 OCR。读不到的页、公式或图表面板会明确列出，缺失的数值和引文保留为待核验。

## 可选工具

在 Codex 命令行之外，可以从仓库根目录运行两个辅助脚本。抽页脚本需要 Python 和 **PyMuPDF 或 pypdf**。笔记校验脚本仅使用 Python 标准库。

```text
python -X utf8 skills/paper-reading/scripts/extract_pdf_pages.py paper.pdf --output pages.json
python -X utf8 skills/paper-reading/scripts/check_note.py note.md --pages P1=11
```

`P1=11` 表示主文来源 P1 的 PDF 共 11 页，按实际页数填写。校验器检查证据表结构、来源 ID、结论引用和已知页码范围。结论是否由证据支撑，仍需回到原文核对。

如果已安装相关科研 Skill，Codex 会在需要时复用，例如用 `paper-lookup` 查找全文、用 `scientific-critical-thinking` 审查论证、用 `sympy` 复核符号推导。图表和扫描页的处理效果取决于实际可用的 PDF 渲染器和 OCR 工具。

## 仓库结构

```text
skills/paper-reading/
├── SKILL.md       # Codex 入口
├── agents/       # 技能显示配置
├── references/   # 来源、证据、阅读模式和领域检查
├── templates/    # 原创研究、综述、软件与算法
└── scripts/      # PDF 分页抽取与笔记结构校验
```

## 设计参考

- `sci-extract` 的分类阅读与来源记录。 [Aut_Sci_Write](https://github.com/ShZhao27208/Aut_Sci_Write/releases/tag/v1.8.0)
- 图表和公式的逐项解释。 [Agentchengfeng/paper-reading-skills](https://github.com/Agentchengfeng/paper-reading-skills)
- 核心结论编号及证据定位。 [sodalone/paper-reading-skill](https://github.com/sodalone/paper-reading-skill)
- 科研工具按需复用。 [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills)
