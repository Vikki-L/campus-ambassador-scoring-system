# Campus Ambassador Scoring System

> **Python 自研多维评分模型** · 把 Coach 团队从"凭经验清退"变成"看数据清退" · 评估 300+ 校园大使 · 辅助清退 ~100 位低效大使

🎯 这是 [Creator Ops Portfolio](https://github.com/Vikki-L/creator-ops-portfolio) 的精选独立项目。

---

## TL;DR

**Problem**: 一个北美 AI 教育出海产品有 300+ 校园大使（Creator）每周拍视频。Coach 团队需要定期评估谁该重点培养、谁该清退，但**全凭经验，没有量化标准**。

**Approach**: 基于对头部竞品 Creator 数据的回归分析（详见 [02-data-insight](docs/02-data-insight.md)），发现 **"~30 视频判断爆款"** 的规律 → 提炼成**「三段踢人」方法论** → 落地成 Python 自研评分模型（**8 维度评分 + 4 级分级**）。

**Result**:
- ✅ 评估 **300+ 大使**
- ✅ 基于学期数据辅助 Coach 团队**清退 ~100 位低效大使**
- ✅ 决策标准从"感觉这人不行"→"评分 25 分以下且无早期突破"

---

## 🏗️ Repo Structure

```
campus-ambassador-scoring-system/
├── README.md                          ← 你正在看
├── docs/
│   ├── 01-problem-and-context.md      ← 业务背景 + 问题陈述
│   ├── 02-data-insight.md             ← ⭐ "30 视频判断爆款" 数据洞察
│   ├── 03-scoring-model.md            ← 评分模型详细设计（8 维度公式）
│   ├── 04-product-integration.md      ← 与 Coach 工作流的集成
│   └── 05-results.md                  ← 量化效果 + 影响
├── src/
│   ├── scoring.py                     ← 评分算法（脱敏版可运行）
│   └── report_generator.py            ← HTML 报告生成
├── samples/
│   └── sample_data.csv                ← 合成数据样本
└── assets/                            ← (截图待添加)
```

---

## 🚀 Quick Start

```bash
# 1. 安装依赖
pip install pandas numpy

# 2. 用样本数据跑一遍
python src/scoring.py --videos samples/sample_data.csv --output results.json

# 3. 生成 HTML 报告
python src/report_generator.py --input results.json --output report.html
```

---

## 📊 Scoring Model Highlights

### 8 维度评分（满分 100）

| 维度 | 权重 | 说明 |
|------|------|------|
| 100K+ 爆款数 | +40 | 强算法响应信号 |
| 10K+ 视频数 | +20 | 突破信号 |
| 5K+ 视频数 | +10 | 初步算法响应 |
| 10K+ 命中率 | +5~10 | 算法响应稳定性 |
| 视频播放中位数 | +2~10 | 整体内容质量 |
| 早期突破 | +3~10 | 加入后多久出第一个爆款 |
| 后期反向扣分 | -10~20 | 持续 20+ 视频无 10K → 警示 |
| 阶段判断 | (qualitative) | Early / Mid / Potential Validation |

### 4 级分级

| Level | Score | Action |
|-------|-------|--------|
| 🟢 HIGH | 70+ | 重点培养 · 加大投入 |
| 🟡 MEDIUM | 45-69 | 持续观察 · 复制成功模式 |
| 🟠 LOW | 25-44 | 警告 · 改进期 |
| 🔴 DROP RISK | <25 | 清退候选 · 立即干预或终止 |

详见 [docs/03-scoring-model.md](docs/03-scoring-model.md)

---

## 💡 Key Insights from This Project

1. **数据洞察 → 方法论 → 产品落地**是一条比单纯"做分析报告"更有价值的链路
2. **"30 视频判断爆款"** 这种洞察来自对竞品脏数据的耐心回归——不是凭直觉
3. **Trend / Warm-up 视频识别与剔除**是评分公平性的关键（详见 scoring.py 的 `is_likely_trend` 和 `is_warmup`）
4. **Phase 概念**（Early / Mid / Potential Validation）让评分对"新人"和"老人"用不同标准——避免误伤新加入的潜力股

---

## 👤 About

**LIU Zibing (Vikki)** · zibingl2@illinois.edu

- 🎓 UIUC Grainger College of Engineering · 金融工程硕士
- 💼 AI 教育出海产品 · 产品助理（2025.01 – 至今）
- 🐙 [Main Portfolio](https://github.com/Vikki-L/creator-ops-portfolio)

---

*Last updated: 2026-06-03*
