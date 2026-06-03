"""
Campus Ambassador Scoring · 校园大使潜力评分模型

8-dimensional scoring + 4-level classification + recommended actions.

Usage:
    python scoring.py --videos sample_data.csv --output results.json
    python scoring.py --videos data.csv --accounts accounts.csv --output results.json

Required columns in videos CSV:
    account, create_time, play_count, digg_count, comment_count,
    share_count, duration, desc, page_url

Optional columns in accounts CSV (for grouping/mapping):
    tt_handle, creator_id, coach_id
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================================
# Pre-filter: Identify Warm-up and Trend videos (excluded from scoring)
# ============================================================================

TREND_KEYWORDS = [
    'trend', 'trending', 'viral', 'dance', 'challenge',
    'duet', 'stitch', 'pov', 'grwm', 'get ready with me',
    'transition', 'outfit', 'ootd', 'makeup', 'haul',
    'asmr', 'mukbang', 'storytime', 'day in my life',
    'morning routine', 'night routine', 'what i eat',
]

# Domain-specific keywords (replace with your own product/category words)
DOMAIN_KEYWORDS = [
    'study', 'math', 'exam', 'homework', 'gpa', 'college', 'school',
    'university', 'learn', 'tutor', 'grade', 'test', 'quiz', 'midterm',
    'final', 'assignment', 'class', 'lecture', 'note', 'textbook',
    'problem', 'equation', 'formula', 'calculate', 'answer',
]


def is_likely_trend(desc: str) -> bool:
    """A video is 'trend' if it hits >=2 trend keywords AND no domain keywords."""
    if pd.isna(desc):
        return False
    desc_lower = str(desc).lower()
    trend_score = sum(1 for kw in TREND_KEYWORDS if kw in desc_lower)
    has_domain = any(kw in desc_lower for kw in DOMAIN_KEYWORDS)
    return trend_score >= 2 and not has_domain


def is_warmup(idx: int, duration: float) -> bool:
    """First 3 videos with duration <= 15s are considered warm-up."""
    return idx < 3 and duration <= 15


# ============================================================================
# Phase Detection
# ============================================================================

def detect_phase(n_valid: int) -> str:
    """Phase determines how strict the scoring should be for this ambassador."""
    if n_valid <= 10:
        return 'Early Validation'
    elif n_valid <= 20:
        return 'Mid Validation'
    else:
        return 'Potential Validation'


# ============================================================================
# Core Scoring (8 dimensions, 0-100)
# ============================================================================

def compute_score(valid_videos: pd.DataFrame) -> tuple[int, list[str]]:
    """
    Returns (score, list of reason strings).
    See docs/03-scoring-model.md for full design rationale.
    """
    if len(valid_videos) == 0:
        return 0, ['No valid videos after filtering']

    views = valid_videos['play_count'].values
    n_valid = len(views)
    max_views = int(np.max(views))
    median_views = int(np.median(views))
    views_5k = int(np.sum(views >= 5000))
    views_10k = int(np.sum(views >= 10000))
    views_100k = int(np.sum(views >= 100000))
    rate_10k = views_10k / n_valid

    early = valid_videos.head(min(5, n_valid))['play_count'].values
    early_has_5k = bool(np.any(early >= 5000))
    early_has_10k = bool(np.any(early >= 10000))
    early_has_100k = bool(np.any(early >= 100000))

    score = 0
    reasons = []

    # Dim 1: 100K+ breakouts (strongest signal)
    if views_100k > 0:
        score += 40
        reasons.append(f'{views_100k} video(s) broke 100K — strong breakout signal')

    # Dim 2: 10K+ count
    if views_10k > 0:
        score += 20
        reasons.append(f'{views_10k} video(s) reached 10K+')

    # Dim 3: 5K+ count
    if views_5k > 0:
        score += 10
        reasons.append(f'{views_5k} video(s) reached 5K+')

    # Dim 4: 10K+ hit rate (consistency)
    if rate_10k >= 0.30:
        score += 10
        reasons.append(f'10K rate {rate_10k:.0%} — consistent algorithm response')
    elif rate_10k >= 0.15:
        score += 5
        reasons.append(f'10K rate {rate_10k:.0%}')

    # Dim 5: Median views (content quality baseline)
    if median_views >= 10000:
        score += 10
        reasons.append(f'Median views {median_views:,} is very strong')
    elif median_views >= 5000:
        score += 7
        reasons.append(f'Median views {median_views:,} is solid')
    elif median_views >= 2000:
        score += 4
        reasons.append(f'Median views {median_views:,} is moderate')
    elif median_views >= 1000:
        score += 2

    # Dim 6: Early breakout (within first 5 videos)
    if early_has_100k:
        score += 10
        reasons.append('Early breakout with 100K+ in first 5 videos')
    elif early_has_10k:
        score += 6
        reasons.append('Algorithm responded early with 10K+ in first 5 videos')
    elif early_has_5k:
        score += 3
        reasons.append('Some early traction with 5K+ in first 5 videos')

    # Dim 7: Negative score for posting many videos without breakthrough
    if n_valid >= 10 and max_views < 5000:
        score -= 10
        reasons.append(
            f'{n_valid} valid videos but max views only {max_views:,} — weak signal'
        )
    if n_valid >= 20 and max_views < 10000:
        score -= 10
        reasons.append(
            f'{n_valid} videos with no 10K breakout — concerning'
        )

    return max(0, min(100, score)), reasons


# ============================================================================
# Level Assignment + Phase Protection
# ============================================================================

LEVEL_THRESHOLDS = [
    (70, 'HIGH'),
    (45, 'MEDIUM'),
    (25, 'LOW'),
    (0,  'DROP RISK'),
]

RECOMMENDED_ACTIONS = {
    'HIGH': 'Continue current strategy. Consider increasing posting frequency to maximize momentum. Test new content formats to diversify growth.',
    'MEDIUM': 'Algorithm is responding — keep testing templates. Focus on replicating what worked in top-performing videos. Aim for consistency.',
    'LOW': 'Review content strategy. Analyze top-performing videos for patterns. Consider coaching session on hook optimization and content quality.',
    'DROP RISK': 'Needs immediate intervention. Schedule 1-on-1 coaching. Review if content aligns with platform best practices. Consider whether to continue investment.',
}


def assign_level(score: int) -> str:
    for threshold, level in LEVEL_THRESHOLDS:
        if score >= threshold:
            return level
    return 'DROP RISK'


def apply_phase_protection(level: str, score: int, phase: str,
                           n_valid: int, max_views: int,
                           early_has_5k: bool) -> tuple[str, int, str | None]:
    """
    Early Validation accounts get a buffer — don't kill new ambassadors prematurely.
    Returns (level, score, extra_reason).
    """
    if phase == 'Early Validation' and n_valid <= 5 and level in ('LOW', 'DROP RISK'):
        if max_views >= 2000 or early_has_5k:
            return 'LOW', max(score, 25), (
                'Too early to judge — limited data but some positive signal'
            )
    return level, score, None


# ============================================================================
# Per-Account Analysis
# ============================================================================

def analyze_account(account: str, videos: pd.DataFrame) -> dict:
    videos = videos.sort_values('create_time', ascending=True).reset_index(drop=True)
    total = len(videos)

    if total == 0:
        return {'account': account, 'total_videos': 0, 'potential_level': 'N/A'}

    # Pre-filter: identify warm-up and trend videos
    warmup_idx = {i for i, v in videos.iterrows()
                  if is_warmup(i, v['duration'])}
    trend_idx = {i for i, v in videos.iterrows()
                 if i not in warmup_idx and is_likely_trend(v['desc'])}
    excluded = warmup_idx | trend_idx
    valid_videos = videos[~videos.index.isin(excluded)]
    n_valid = len(valid_videos)

    phase = detect_phase(n_valid)

    if n_valid == 0:
        return {
            'account': account,
            'total_videos': total,
            'warmup_count': len(warmup_idx),
            'trend_count': len(trend_idx),
            'valid_count': 0,
            'phase': phase,
            'potential_score': 0,
            'potential_level': 'DROP RISK',
            'reason': 'No valid videos found after filtering trend/warm-up',
            'recommended_action': RECOMMENDED_ACTIONS['DROP RISK'],
        }

    score, reasons = compute_score(valid_videos)
    level = assign_level(score)

    # Apply phase protection for new ambassadors
    early = valid_videos.head(min(5, n_valid))['play_count'].values
    early_has_5k = bool(np.any(early >= 5000))
    max_views = int(np.max(valid_videos['play_count'].values))
    level, score, extra_reason = apply_phase_protection(
        level, score, phase, n_valid, max_views, early_has_5k
    )
    if extra_reason:
        reasons.append(extra_reason)

    return {
        'account': account,
        'total_videos': total,
        'warmup_count': len(warmup_idx),
        'trend_count': len(trend_idx),
        'valid_count': n_valid,
        'max_views': max_views,
        'median_views': int(np.median(valid_videos['play_count'].values)),
        'views_5k': int(np.sum(valid_videos['play_count'].values >= 5000)),
        'views_10k': int(np.sum(valid_videos['play_count'].values >= 10000)),
        'views_100k': int(np.sum(valid_videos['play_count'].values >= 100000)),
        'phase': phase,
        'potential_score': score,
        'potential_level': level,
        'reason': '; '.join(reasons) if reasons else 'Insufficient data',
        'recommended_action': RECOMMENDED_ACTIONS[level],
        'first_post_date': videos['create_time'].min().strftime('%Y-%m-%d'),
        'last_post_date': videos['create_time'].max().strftime('%Y-%m-%d'),
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Score campus ambassadors by their video performance.'
    )
    parser.add_argument('--videos', required=True,
                        help='Path to videos CSV (columns: account, create_time, play_count, ...)')
    parser.add_argument('--output', default='results.json',
                        help='Output JSON path')
    args = parser.parse_args()

    videos_path = Path(args.videos)
    if not videos_path.exists():
        print(f'Error: {videos_path} not found', file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(videos_path)
    df['create_time'] = pd.to_datetime(df['create_time'])

    results = []
    for account, group in df.groupby('account'):
        results.append(analyze_account(account, group))

    # Sort by potential_score descending
    results.sort(key=lambda x: x.get('potential_score', -1), reverse=True)

    with open(args.output, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    # Summary
    print(f'Total accounts scored: {len(results)}')
    levels = pd.Series([r['potential_level'] for r in results]).value_counts()
    print('\nLevel distribution:')
    print(levels.to_string())
    print(f'\nResults written to: {args.output}')


if __name__ == '__main__':
    main()
