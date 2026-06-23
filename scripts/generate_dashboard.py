import json
import os
import datetime

BRAND_NAME = 'Stone De Art SEO Dashboard'
BRAND_DOMAIN = 'stonedeart.com.my'


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def fmt_num(n):
    if n is None:
        return '—'
    return f'{int(n):,}'


def generate():
    audit = load_json('data/audit.json')
    seranking = load_json('data/seranking.json')
    gsc = audit.get('gsc', {})
    ga4 = audit.get('ga4', {})
    updated = audit.get('updated_at', '—')

    keywords_rows = ''
    for kw in gsc.get('top_keywords', []):
        keywords_rows += f"""
        <tr>
          <td>{kw['query']}</td>
          <td>{fmt_num(kw['clicks'])}</td>
          <td>{fmt_num(kw['impressions'])}</td>
          <td>{kw['ctr']}%</td>
          <td>{kw['position']}</td>
        </tr>"""

    channels_rows = ''
    for ch in ga4.get('channels', []):
        channels_rows += f"""
        <tr>
          <td>{ch['channel']}</td>
          <td>{fmt_num(ch['sessions'])}</td>
          <td>{fmt_num(ch['users'])}</td>
        </tr>"""

    sr_issues = ''
    for issue, detail in seranking.get('issues', {}).items():
        if isinstance(detail, dict):
            sr_issues += f'<li><strong>{issue}</strong>: {detail.get("count", "")} {detail.get("note", "")}</li>'

    health_score = seranking.get('health_score', 0)
    score_color = '#22c55e' if health_score >= 80 else '#f59e0b' if health_score >= 60 else '#ef4444'

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{BRAND_NAME}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #1e293b; }}
  header {{ background: #1e293b; color: white; padding: 1.5rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
  header h1 {{ font-size: 1.25rem; font-weight: 600; }}
  header span {{ font-size: 0.8rem; opacity: 0.6; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; padding: 1.5rem 2rem 0; }}
  .card {{ background: white; border-radius: 12px; padding: 1.25rem 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .card .label {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: .05em; margin-bottom: .5rem; }}
  .card .value {{ font-size: 1.8rem; font-weight: 700; color: #1e293b; }}
  .card .sub {{ font-size: 0.75rem; color: #94a3b8; margin-top: .25rem; }}
  .section {{ margin: 1.5rem 2rem; background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.08); overflow: hidden; }}
  .section h2 {{ padding: 1rem 1.5rem; font-size: 0.9rem; font-weight: 600; border-bottom: 1px solid #f1f5f9; color: #475569; text-transform: uppercase; letter-spacing: .05em; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ background: #f8fafc; padding: .6rem 1rem; text-align: left; font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: .04em; font-weight: 500; }}
  td {{ padding: .6rem 1rem; font-size: 0.85rem; border-top: 1px solid #f1f5f9; }}
  tr:hover td {{ background: #f8fafc; }}
  .score-ring {{ display: flex; align-items: center; gap: 1rem; padding: 1.5rem; }}
  .score-num {{ font-size: 3rem; font-weight: 800; color: {score_color}; }}
  .score-meta {{ font-size: 0.8rem; color: #64748b; }}
  .issues {{ padding: 1rem 1.5rem; }}
  .issues li {{ font-size: 0.85rem; margin-bottom: .4rem; color: #475569; }}
  .period {{ font-size: 0.75rem; color: #94a3b8; padding: .5rem 1.5rem 1rem; }}
  footer {{ text-align: center; padding: 2rem; font-size: 0.75rem; color: #94a3b8; }}
</style>
</head>
<body>
<header>
  <h1>📊 {BRAND_NAME}</h1>
  <span>最后更新：{updated}</span>
</header>

<div class="grid">
  <div class="card">
    <div class="label">点击次数 (28天)</div>
    <div class="value">{fmt_num(gsc.get('total_clicks'))}</div>
    <div class="sub">Google Search Console</div>
  </div>
  <div class="card">
    <div class="label">曝光次数 (28天)</div>
    <div class="value">{fmt_num(gsc.get('total_impressions'))}</div>
    <div class="sub">Google Search Console</div>
  </div>
  <div class="card">
    <div class="label">平均点击率</div>
    <div class="value">{gsc.get('avg_ctr', '—')}%</div>
    <div class="sub">CTR</div>
  </div>
  <div class="card">
    <div class="label">平均排名</div>
    <div class="value">{gsc.get('avg_position', '—')}</div>
    <div class="sub">Search Position</div>
  </div>
  <div class="card">
    <div class="label">会话数 (28天)</div>
    <div class="value">{fmt_num(ga4.get('total_sessions'))}</div>
    <div class="sub">Google Analytics</div>
  </div>
  <div class="card">
    <div class="label">用户数 (28天)</div>
    <div class="value">{fmt_num(ga4.get('total_users'))}</div>
    <div class="sub">Google Analytics</div>
  </div>
</div>

<div class="section">
  <h2>🔑 搜索关键词 Top 20（28天）</h2>
  <p class="period">数据周期：{gsc.get('period', '—')}</p>
  <table>
    <thead><tr><th>关键词</th><th>点击</th><th>曝光</th><th>CTR</th><th>排名</th></tr></thead>
    <tbody>{keywords_rows if keywords_rows else '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:2rem">连接 GSC 后自动显示数据</td></tr>'}</tbody>
  </table>
</div>

<div class="section">
  <h2>📈 流量来源渠道（28天）</h2>
  <table>
    <thead><tr><th>渠道</th><th>会话数</th><th>用户数</th></tr></thead>
    <tbody>{channels_rows if channels_rows else '<tr><td colspan="3" style="text-align:center;color:#94a3b8;padding:2rem">连接 GA4 后自动显示数据</td></tr>'}</tbody>
  </table>
</div>

<div class="section">
  <h2>🛠 技术健康分（SE Ranking）</h2>
  <div class="score-ring">
    <div class="score-num">{health_score or '—'}</div>
    <div class="score-meta">
      <div>上传时间：{seranking.get('updated_at', '待更新')}</div>
      <div>已爬取页面：{fmt_num(seranking.get('pages_crawled'))}</div>
      <div>错误 {seranking.get('errors', 0)} · 警告 {seranking.get('warnings', 0)} · 提示 {seranking.get('notices', 0)}</div>
    </div>
  </div>
  {'<ul class="issues">' + sr_issues + '</ul>' if sr_issues else '<p class="period">运行 update_seranking.py 后显示技术问题列表</p>'}
</div>

<footer>{BRAND_DOMAIN} · 数据来源：Google Search Console、Google Analytics 4、SE Ranking · 每周一自动更新</footer>
</body>
</html>"""

    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Generated docs/index.html')


if __name__ == '__main__':
    generate()
