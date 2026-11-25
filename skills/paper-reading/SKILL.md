---
name: paper-reading
description: 阅读、精读或审查材料科学、高分子科学、计算材料科学与分子动力学相关论文。用于处理 PDF、DOI、论文网址或本地论文文件，解释公式、图表或科研逻辑，评估可复现性，并生成证据可追溯的 Obsidian 中文 Markdown 笔记。
---

# Paper Reading

1. 确定输入、模式和关注点。默认 **Standard**，可显式选择 **Quick**、**Deep** 或 **Reproduce**。用户只问单个公式、图表或概念时，保留其问题范围和必要的定位。
2. 读取 [来源与证据](references/sources-and-evidence.md)。确认论文标识、实际阅读的版本和覆盖范围。PDF 以文件页序定位。图表、公式或抽取异常涉及关键结论时，打开相关原页核对。
3. 判定主要贡献，选择 [原创研究](templates/original-research.md)、[综述](templates/review.md) 或 [软件与算法](templates/software-algorithm.md) 模板。混合论文以主要贡献为主，只加入与次要贡献相关的检查。
4. 按 [模式与分析](references/modes-and-analysis.md) 调整阅读深度。完整笔记交付前核对研究背景、研究空白、科学问题、研究方法、核心发现、创新和局限七项。受查阅范围限制的项目标明依据。处理材料体系、聚合物、计算方法或 MD 时，读取 [材料与分子动力学](references/materials-and-md.md) 中相关段落。需要专门工具时，先找已安装的技能和可用运行时。
5. 用中文 Markdown 交付。保留 DOI、源链接、实际版本、英文术语、原图表和公式编号。每条核心结论带独立 ID、来源类别和可核对的位置。外部资料给出实际查阅的链接。数字保留原单位和统计口径，证据不足时陈述缺口。文件仅保存到用户明确指定的位置，未指定时在回复中交付 Markdown。

本地 PDF 的可选辅助命令为 python scripts/extract_pdf_pages.py INPUT.pdf --output pages.json。它保留页序并报告文本提取状态，公式和图表仍由读者结合原页核对。若已生成笔记，运行 python scripts/check_note.py NOTE.md --pages P1=N 可检查证据表的结构、来源 ID、结论引用及主 PDF 页码范围。将相对命令路径解析为本技能目录下的脚本。未确认页数时省略对应的 --pages。脚本不可用时，保留相同的人工检查。
