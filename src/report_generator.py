"""
HTML Report Generator · 把评分结果转成 Coach 团队可读的 HTML 报告

Usage:
    python report_generator.py --input results.json --output report.html
"""

import argparse
import html
import json
from pathlib import Path


LEVEL_COLORS = {
    'HIGH': '#10b981',       # green
    'MEDIUM': '#f59e0b',     # amber
    'LOW': '#f97316',        # orange
    'DROP RISK': '#ef4444',  # red
    'N/A': '#9ca3af',
}

LEVEL_EMOJI = {
    'HIGH': '🟢',
    'MEDIUM': '🟡',
    'LOW': '🟠',
    'DROP RISK': '🔴',
    'N/A': '⚪️',
}


def render_card(result: dict) -> str:
    level = result.get('potential_level', 'N/A')
    color = LEVEL_COLORS.get(level, '#9ca3af')
    emoji = LEVEL_EMOJI.get(level, '⚪️')
    account = html.escape(str(result.get('account', '?')))
    score = result.get('potential_score', 0)
    phase = html.escape(str(result.get('phase', 'N/A')))
    reason = html.escape(str(result.get('reason', '')))
    action = html.escape(str(result.get('recommended_action', '')))
    n_valid = result.get('valid_count', 0)
    max_v = result.get('max_views', 0)
    median_v = result.get('median_views', 0)
    v_10k = result.get('views_10k', 0)
    v_100k = result.get('views_100k', 0)

    return f"""
    <div class="card" style="border-left-color: {color};">
      <div class="card-header">
        <h3>{emoji} @{account}</h3>
        <div class="badges">
          <span class="badge" style="background: {color};">{level}</span>
          <span class="badge gray">Score: {score}</span>
          <span class="badge gray">{phase}</span>
        </div>
      </div>
      <div class="metrics">
        <div class="metric"><span class="label">Valid Videos</span><span class="value">{n_valid}</span></div>
        <div class="metric"><span class="label">Max Views</span><span class="value">{max_v:,}</span></div>
        <div class="metric"><span class="label">Median</span><span class="value">{median_v:,}</span></div>
        <div class="metric"><span class="label">10K+</span><span class="value">{v_10k}</span></div>
        <div class="metric"><span class="label">100K+</span><span class="value">{v_100k}</span></div>
      </div>
      <div class="reason"><strong>Why:</strong> {reason}</div>
      <div class="action"><strong>Action:</strong> {action}</div>
    </div>
    """


def render_report(results: list[dict], title: str = 'Ambassador Scoring Report') -> str:
    cards_html = '\n'.join(render_card(r) for r in results)

    level_counts = {}
    for r in results:
        lvl = r.get('potential_level', 'N/A')
        level_counts[lvl] = level_counts.get(lvl, 0) + 1
    summary_html = ' · '.join(
        f'{LEVEL_EMOJI.get(lvl, "")} {lvl}: <strong>{count}</strong>'
        for lvl, count in sorted(level_counts.items())
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f9fafb; color: #1f2937; max-width: 1200px;
    margin: 0 auto; padding: 32px 24px;
  }}
  h1 {{ font-size: 28px; margin-bottom: 8px; }}
  .summary {{ color: #6b7280; margin-bottom: 32px; font-size: 14px; }}
  .card {{
    background: white; border-radius: 12px; padding: 20px;
    margin-bottom: 16px; border-left: 4px solid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
  .card-header h3 {{ margin: 0; font-size: 18px; }}
  .badges {{ display: flex; gap: 8px; }}
  .badge {{
    padding: 4px 10px; border-radius: 12px; color: white;
    font-size: 12px; font-weight: 600;
  }}
  .badge.gray {{ background: #6b7280; }}
  .metrics {{ display: flex; gap: 24px; margin: 12px 0; flex-wrap: wrap; }}
  .metric {{ display: flex; flex-direction: column; }}
  .metric .label {{ font-size: 11px; color: #6b7280; text-transform: uppercase; }}
  .metric .value {{ font-size: 16px; font-weight: 600; color: #1f2937; }}
  .reason, .action {{ margin: 8px 0; font-size: 13px; color: #4b5563; }}
  .action {{ color: #1f2937; }}
</style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="summary">Total: <strong>{len(results)}</strong> · {summary_html}</div>
  {cards_html}
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description='Generate HTML report from scoring results JSON.')
    parser.add_argument('--input', required=True, help='Path to scoring results JSON')
    parser.add_argument('--output', default='report.html', help='Output HTML path')
    parser.add_argument('--title', default='Ambassador Scoring Report', help='Report title')
    args = parser.parse_args()

    with open(args.input) as f:
        results = json.load(f)

    html_str = render_report(results, args.title)
    Path(args.output).write_text(html_str)
    print(f'Report written to: {args.output} ({len(results)} ambassadors)')


if __name__ == '__main__':
    main()
