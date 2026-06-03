# Campus Ambassador Scoring System

> Python 自研多维评分模型 · 把 Coach 团队从"凭经验清退"变成"看数据清退" · 评估 600+ 校园大使 · 辅助清退 ~400 位低效大使

🎯 这是 [Creator Ops Portfolio](https://github.com/Vikki-L/creator-ops-portfolio) 的精选独立项目。

---

## TL;DR

**Problem**：一个北美 AI 教育出海产品有 600+ 校园大使（Creator）每周拍视频。Coach 团队需要定期评估谁该重点培养、谁该清退——全凭经验，没有量化标准。

**Approach**：基于对头部竞品 Creator 数据的回归分析（详见 [02-data-insight](docs/02-data-insight.md)），发现 _"~30 视频判断爆款"_ 的规律 → 提炼成 _「三段踢人」方法论_ → 落地成 Python 自研评分模型（多维度评分 + 4 级分级）。

**Result**：

- ✅ 评估 600+ 大使
- ✅ 基于学期数据辅助 Coach 团队清退 ~400 位低效大使
- ✅ 决策标准从"感觉这人不行" → 量化指标 + 推荐动作

---

## 🏗️ Repo Structure

```
campus-ambassador-scoring-system/
├── README.md                          ← 你正在看
├── docs/
│   ├── 01-problem-and-context.md      ← 业务背景 + 问题陈述
│   ├── 02-data-insight.md             ← ⭐ "30 视频判断爆款" 数据洞察
│   ├── 03-scoring-model.md            ← 评分模型设计（多维度·已模糊化）
│   ├── 04-product-integration.md      ← 与 Coach 工作流的集成
│   └── 05-results.md                  ← 量化效果 + 影响
├── samples/
│   └── sample_data.csv                ← 合成数据样本
└── assets/                            ← (截图待添加)
```

> ⚠️ **代码 & 详细权重未公开**：评分公式的具体权重、阈值、Python 实现因含商业逻辑敏感性暂不在本仓库公开。本仓库以**方法论 + 设计原理 + 业务集成**为主，可在面试时单独 demo。

---

## 📊 Scoring Model Highlights

### 多维度评分（满分 100）

模型按以下维度对每位大使的视频表现打分：

| 维度 | 权重档位 | 衡量什么 |
|------|---------|---------|
| 100K+ 爆款数 | 🟥 高 | 强算法响应信号 |
| 10K+ 视频数 | 🟧 中 | 突破信号 |
| 5K+ 视频数 | 🟨 低 | 初步算法响应 |
| 10K+ 命中率 | 🟧 中 | 算法响应稳定性 |
| 视频播放中位数 | 🟧 中 | 整体内容质量 |
| 早期突破（前 5 视频）| 🟨 低 | 加入后多久出第一个爆款 |
| 后期反向扣分 | 🟥 高（负向）| 拍了很多但没突破 = 警示 |
| Phase 阶段判断 | (qualitative) | Early / Mid / Potential Validation |

> 具体权重 / 阈值已模糊化，详细设计逻辑见 [docs/03-scoring-model.md](docs/03-scoring-model.md)

### 4 级分级

| Level | 含义 | Recommended Action |
|-------|------|--------------------|
| 🟢 HIGH | 高潜力 | 重点培养 · 加大投入 |
| 🟡 MEDIUM | 算法响应中 | 持续观察 · 复制成功模式 |
| 🟠 LOW | 初步信号弱 | 警告 · 改进期 |
| 🔴 DROP RISK | 已无希望 | 清退候选 · 立即干预或终止 |

---

## 💡 Key Insights from This Project

1. **数据洞察 → 方法论 → 产品落地**是一条比单纯"做分析报告"更有价值的链路
2. _"30 视频判断爆款"_ 这种洞察来自对竞品脏数据的耐心回归——不是凭直觉
3. **Trend / Warm-up 视频识别与剔除**是评分公平性的关键
4. **Phase 概念**（Early / Mid / Potential Validation）让评分对"新人"和"老人"用不同标准——避免误伤新加入的潜力股

---

## 👤 About

**LIU Zibing (Vikki)** · zibingl2@illinois.edu

- 🎓 UIUC Grainger College of Engineering · 金融工程硕士
- 💼 AI 教育出海产品 · 产品助理（2025.01 – 2026.06）
- 🐙 [Main Portfolio](https://github.com/Vikki-L/creator-ops-portfolio)

---

*Last updated: 2026-06-03*
