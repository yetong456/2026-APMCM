# 2026 APMCM · Problem D

本仓库整理这次的选题判断、D 题研究方案、已运行实验、环境依赖、两人协作和英文论文规范。选题已确定为 **D — Application of Special Purpose Quantum Computer to Rare-Target Search in Perovskite Candidate Materials**。

论文、摘要、图表和附录说明使用英文。中文文档用于队内研究和交接。

## 当前进度

| 项目 | 状态 |
|---|---|
| 选题与三问拆解 | 已整理 |
| Python 3.12、建模库、Kaiwu 1.4.4 | 本机基础导入和 QUBO 构造通过 |
| 验证排序、近目标留出、精确消元、软件量化 | 已运行，日志与预测表见 results |
| Kaiwu 实际优化调用 | 本地精确求解器完成 338 个九自旋实例，逐块核验全部合法与非法状态 |
| 模型与计算成本 | 已冻结评分表并记录分项耗时，SPQC 真机尚无实测 |
| 英文论文 | [阅读 PDF](problem_d/paper/D_review.pdf) · [LaTeX 源稿、预测与复现](problem_d/paper/README.md) · [支撑材料 ZIP](problem_d/paper/D_review_support.zip)。审阅版暂空队号，正式提交前须填写真实队号 |

探索结论以脚本、预测表和日志为依据。隐藏测试集物理标签未公开，候选分数是代理预测。

## 文档入口

| 文档 | 内容 |
|---|---|
| [四题初评与选题依据](docs/01_problem_selection.md) | A–D 比较及选择 D 的原因 |
| [D 题模型与任务步骤](docs/02_modeling_plan.md) | 数据口径、三问数学模型及验收 |
| [创新方案与已有证据](docs/03_innovations_and_evidence.md) | 两条主线、推导、改善和失败案例 |
| [两人分工与同步](docs/04_team_workflow.md) | 版本交接、看板和比赛时间安排 |
| [文献检索任务](docs/05_literature_search.md) | 检索方向、已核对 DOI、给其他 AI 的任务 |
| [环境与复现](docs/06_environment.md) | 安装运行、依赖版本和授权状态 |
| [英文论文与提交要求](docs/07_paper_requirements.md) | 页序、匿名、命名、截止和交付 |
| [外部笔记评审与修正](docs/08_external_notes_review.md) | 可读来源、我们方案的不足、物理预测与官方 8 位新实验 |
| [论文修订与 24 项核验](docs/09_paper_revision.md) | 评审意见、英文逐句修改、逐图处置与交稿待办 |
| [实验记录](problem_d/results/README.md) | 逐行预测、日志、指标及环境版本 |

## 目录

```text
docs/                         队内方案与进度
problem_d/date/               D 题原始 CSV 与官方数据说明
problem_d/exploration/        本次讨论中运行的探索代码
problem_d/results/            日志、预测、指标和环境版本
problem_d/requirements.txt    直接依赖
problem_d/requirements-lock.txt  完整依赖版本
skills/apmcm-problem-d/       亚太杯 D 题专用技能
sources/problems/            四题原始 PDF
sources/rules/               本届规则与空白表单
sources/latex/               赛包 LaTeX 模板源文件
```

## 快速运行

Windows PowerShell，在仓库根目录使用 Python 3.12。

```powershell
py -3.12 -m venv .venv
& .venv/Scripts/python.exe -m pip install -r problem_d/requirements.txt
& .venv/Scripts/python.exe problem_d/exploration/audit_data.py
& .venv/Scripts/python.exe problem_d/exploration/compare_surrogates.py --seed 26
& .venv/Scripts/python.exe problem_d/exploration/test_innovation_ideas.py stress --seed 26
& .venv/Scripts/python.exe problem_d/exploration/test_innovation_ideas.py encoding --seed 26
```

若启动器找不到已安装的 3.12，按[环境文档](docs/06_environment.md)指定解释器。代码从自身位置定位数据，可从不同目录运行。

AI 接手时先读专用技能、模型方案、创新证据和最新结果，再推进当前负责的步骤。正式提交按本届规定准备论文、签名控制页和适用的支撑材料，支撑包排除原始比赛数据。
