# 03 · Scoring Model · 评分模型详细设计

> 8 维度评分 → 4 级分级 → 推荐动作。本文档详细说明每个维度的设计逻辑。

## 🏗️ Architecture

```
                   ┌─────────────────────────────────┐
                   │  Raw Videos (per Creator)       │
                   │  · views / likes / comments     │
                   │  · duration / desc / date       │
                   └────────────────┬────────────────┘
                                    │
                   ┌────────────────▼────────────────┐
                   │  Pre-filter                     │
                   │  · Warm-up videos (前 3 条 + 时长≤15s)
                   │  · Trend videos (关键词识别)    │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                       ┌──────── Valid Videos ────────┐
                       │  used for scoring            │
                       └──────────────┬───────────────┘
                                      │
                  ┌───────────────────┴───────────────────┐
                  │                                       │
        ┌─────────▼─────────┐                  ┌──────────▼──────────┐
        │  Scoring (8 dims) │                  │  Phase Detection    │
        │  outputs: 0-100   │                  │  Early/Mid/Potential│
        └─────────┬─────────┘                  └──────────┬──────────┘
                  │                                       │
                  └───────────────┬───────────────────────┘
                                  │
                       ┌──────────▼──────────┐
                       │  Level Assignment   │
                       │  HIGH/MED/LOW/DROP  │
                       └──────────┬──────────┘
                                  │
                       ┌──────────▼──────────┐
                       │  Recommended Action │
                       └─────────────────────┘
```

## 📐 Scoring Dimensions (8 维度)

### 维度 1: 100K+ 爆款数 · 强算法响应信号
```python
if views_100k > 0:
    score += 40
```
**为什么权重最高**：100K+ 是质变信号，证明账号能突破算法上限。一个 100K 爆款的招新价值 ≈ 20 个 5K 视频。

### 维度 2: 10K+ 视频数 · 突破信号
```python
if views_10k > 0:
    score += 20
```
**意义**：证明账号已经突破"小池子"，进入算法推荐扩散阶段。

### 维度 3: 5K+ 视频数 · 初步算法响应
```python
if views_5k > 0:
    score += 10
```
**意义**：起步信号，算法开始"愿意推"。

### 维度 4: 10K+ 命中率 · 算法响应稳定性
```python
if rate_10k >= 0.3:    score += 10  # 30%+ 视频破 10K = 持续稳定
elif rate_10k >= 0.15: score += 5
```
**为什么是 rate**：避免"运气好出过 1 个爆款"的假阳性。30% 命中率说明算法稳定喜欢这个账号。

### 维度 5: 视频播放中位数 · 整体内容质量
```python
if median_views >= 10000:   score += 10
elif median_views >= 5000:  score += 7
elif median_views >= 2000:  score += 4
elif median_views >= 1000:  score += 2
```
**为什么用中位数不用平均数**：平均数容易被单个爆款拉高（误判）；中位数代表"日常水准"。

### 维度 6: 早期突破 · 加入后多久出第一个爆款
```python
early_videos = valid_videos.head(min(5, n_valid))
if early_videos has 100K:  score += 10
elif early_videos has 10K: score += 6
elif early_videos has 5K:  score += 3
```
**意义**：早期突破（前 5 视频内出爆款）= 账号天赋好 + 算法快速识别 → 加分。

### 维度 7: 后期反向扣分 · 拍了很多但没突破 = 警示信号
```python
if n_valid >= 10 and max_views < 5000:
    score -= 10  # 拍了 10+ 视频但最高才 5K
if n_valid >= 20 and max_views < 10000:
    score -= 10  # 拍了 20+ 视频但没有 10K = 严重警示
```
**为什么要扣分**：这是 [02-data-insight.md](02-data-insight.md) 里"30 视频判断爆款"洞察的直接应用——投入很多但回报极低 = 应该降低评分。

### 维度 8: Phase 阶段判断 · 给新人留余地
```python
if n_valid <= 10:    phase = 'Early Validation'    # 数据不够，谨慎判断
elif n_valid <= 20:  phase = 'Mid Validation'      # 进入观察期
else:                phase = 'Potential Validation' # 数据充分，可以下结论
```

### Phase 特殊保护规则

对 Early Validation 阶段（≤10 视频）的特殊处理：
```python
if phase == 'Early Validation' and level in ('LOW', 'DROP RISK'):
    if max_views >= 2000 or early_has_5k:
        # 给新人一点缓冲——"还看不出来"而不是"已经不行了"
        level = 'LOW'
        reason += "Too early to judge — limited data but some positive signal"
```

**为什么需要这条**：避免误伤刚加入 2 周的新人——他们可能本来就是潜力股。

## 🎚️ Level Assignment (4 级)

```python
if score >= 70:
    level = 'HIGH'        # 🟢 重点培养
elif score >= 45:
    level = 'MEDIUM'      # 🟡 持续观察
elif score >= 25:
    level = 'LOW'         # 🟠 警告期
else:
    level = 'DROP RISK'   # 🔴 清退候选
```

## 🎯 Recommended Actions (针对性建议)

每个 Level 输出**一段具体的建议**，让 Coach 拿到评分后**直接知道下一步做什么**：

| Level | Recommended Action |
|-------|-------------------|
| HIGH | "Continue current strategy. Consider increasing posting frequency to maximize momentum. Test new content formats to diversify growth." |
| MEDIUM | "Algorithm is responding — keep testing templates. Focus on replicating what worked in top-performing videos. Aim for consistency." |
| LOW | "Review content strategy. Analyze top-performing videos for patterns. Consider coaching session on hook optimization and content quality." |
| DROP RISK | "Needs immediate intervention. Schedule 1-on-1 coaching. Review if content aligns with platform best practices. Consider whether to continue investment." |

## 🛠️ Pre-filter Logic (Why It Matters)

不所有视频都参与评分。两类视频会被剔除：

### Warm-up Videos
```python
def is_warmup(video, idx):
    if idx >= 3: return False
    return video['duration'] <= 15  # 前 3 条 + 时长 ≤ 15s = warm-up
```
**为什么剔除**：新账号通常前几条是"养号"测试视频，不代表正式内容能力。

### Trend Videos
```python
TREND_KEYWORDS = ['trend', 'viral', 'dance', 'challenge', 'duet', 'stitch',
                  'pov', 'grwm', 'transition', 'asmr', 'storytime', ...]

def is_likely_trend(desc):
    if 关键词命中数 >= 2 and 没有 study 类关键词:
        return True
```
**为什么剔除**：Trend 视频靠平台流量红利，不代表 Creator 自己的内容能力——它告诉你的是"热点跟得快"，不是"能持续产出"。

## 📊 Real-World Performance

| Cohort | Total | HIGH | MED | LOW | DROP RISK |
|--------|-------|------|-----|-----|-----------|
| Spring Semester | 300+ | ~10% | ~25% | ~35% | ~30% |

→ 约 30% 被识别为 DROP RISK → 经 Coach 复核后辅助清退 ~100 位。

---

[← Back to README](../README.md)
