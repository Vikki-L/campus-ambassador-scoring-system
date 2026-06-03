# 04 · Product Integration · 与 Coach 工作流的集成

> 评分模型不是"分析报告就结束了"——它和 Coach 团队的日常工作流深度集成。

## 🔄 The Loop · 从评分到清退执行

```
              ┌──────────────────┐
              │  每周/双周跑分    │
              │  (~30 min)       │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  生成 HTML 报告  │
              │  按 Coach 分组    │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │  Coach 团队复核   │
              │  · HIGH → 加投入  │
              │  · MED → 测新模板 │
              │  · LOW → 1on1 沟通│
              │  · DROP → 复核确认│
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  达人池状态更新  │
              │  → CRM 系统       │
              └──────────────────┘
```

## 🎯 Key Integration Points

### 1. **按 Coach 分组 + 排序**

报告里达人**按"所属 Coach"分组**，组内**按潜力评分倒序**——让每位 Coach 一打开报告就能看到自己下属的完整画面，而不是混在 300+ 数据里找。

### 2. **推荐动作 → 转化为具体 Coach 任务**

每条评分输出一段 `recommended_action`，Coach 看完直接知道下一步：

- **HIGH** → 调高发视频 quota / 让 Ta 测新模板
- **MED** → 在周会上 review 这位的 Top 视频，提炼可复制点
- **LOW** → 安排 1-on-1 沟通 + 提供模板库参考
- **DROP RISK** → Coach 复核 → 进入"观察期"或"清退流程"

### 3. **达人池 CRM 联动**

评分输出 → CRM 系统（[A5 Coach × Creator Management](https://github.com/Vikki-L/creator-ops-portfolio/tree/main/01-coach-creator-dual-platform/A5-coach-creator-management) 内部模块）：

- DROP RISK 状态自动标红
- 长期 LOW 的大使触发"清退候选名单"
- Coach 在 CRM 里完成最终清退决策 → 状态变更回流

### 4. **Phase 维度避免新人误伤**

新加入 2 周内（≤10 视频）的 Early Validation 阶段大使，即使评分低也会**触发特殊保护规则**——避免 Coach 误清退新人。详见 [03-scoring-model.md · Phase 特殊保护规则](03-scoring-model.md#phase-特殊保护规则)。

## 🔗 What This Enables · 业务价值

### Before（评分系统上线前）
```
Coach: "我感觉某位大使最近不太行了..."
Manager: "你确定吗？拍了多少条？最高多少？"
Coach: "呃...我得去 Excel 拉一下"
[一周后]
Coach: "好像 10+ 条，最高几 K，但 Ta 上次有个不错的..."
Manager: "再观察看看吧"
```

### After（评分系统上线后）
```
Manager 打开报告 → 看到某位大使: DROP RISK · 评分较低
  · "拍了 N 条有效视频但最高播放偏弱 — weak signal"
  · "10K 命中率为 0% — algorithm not responding"
  · "Phase: Mid Validation"
  · Recommended: "Needs immediate intervention..."

Manager → Coach: "这个数据 Ta 还想继续培养吗？" 
Coach: "我来排 1-on-1，下周给结论"
```

→ **决策从"几周后再说"变成"明天就执行"**。

## 💼 Adoption · 实际使用情况

- **跑分频率**：每周/双周 1 次
- **服务规模**：300+ 大使
- **辅助清退**：基于 Spring Semester 数据 ~100 位
- **达人池质量**：清退后 active 大使数从 ~225 → 125，但 Quota 完成率和平均播放量都显著提升

---

[← Back to README](../README.md)
