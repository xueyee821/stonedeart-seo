import json, os, datetime

BRAND_NAME = 'Stone De Art'
BRAND_DOMAIN = 'stonedeart.com.my'

def load_json(path, default=None):
    try:
        with open(path) as f: return json.load(f)
    except: return default or {}

def fmt(n):
    if n is None or n == 0: return '—'
    return f'{int(n):,}'

def sc(score):
    if not score: return '#94a3b8','#94a3b822','待更新'
    if score >= 80: return '#16a34a','#16a34a22','良好'
    if score >= 60: return '#f59e0b','#f59e0b22','需改善'
    return '#ef4444','#ef444422','严重'

def kw_status(pos):
    if pos <= 3: return '#dcfce7','#16a34a','保持'
    if pos <= 10: return '#fef9c3','#f59e0b','优化'
    if pos <= 20: return '#fef2f2','#ef4444','大机会'
    return '#fef2f2','#ef4444','排名太低'

def bounce_color(rate):
    if rate < 40: return '#16a34a'
    if rate < 70: return '#f59e0b'
    return '#ef4444'

def generate():
    audit = load_json('data/audit.json')
    sr    = load_json('data/seranking.json')
    gsc   = audit.get('gsc', {})
    ga4   = audit.get('ga4', {})
    updated = audit.get('updated_at', datetime.datetime.now().strftime('%Y-%m-%d'))

    # ── scores ──────────────────────────────────────────────
    scores = [
        ('技术 SEO',  60, 'technical'),
        ('Schema',   20, 'schema'),
        ('内容质量',  65, 'content'),
        ('页面优化',  45, 'onpage'),
        ('性能',      55, 'perf'),
        ('AI 可见度', 35, 'ai'),
        ('图片',      50, 'img'),
    ]
    overall = round(sum(s for _,s,_ in scores) / len(scores))

    score_cards = ''
    for label, val, _ in scores:
        col, bg, lbl = sc(val)
        score_cards += f'''<div style="background:white;border-radius:10px;padding:14px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06);">
        <div style="font-size:26px;font-weight:800;color:{col};">{val}</div>
        <div style="font-size:11px;font-weight:600;color:#555;margin:2px 0;">{label}</div>
        <div style="font-size:10px;color:{col};background:{bg};padding:1px 6px;border-radius:4px;display:inline-block;">{lbl}</div>
        <div style="margin-top:8px;"><div style="background:#e5e7eb;border-radius:4px;height:6px;"><div style="background:{col};width:{val}%;height:6px;border-radius:4px;"></div></div></div>
    </div>'''

    # ── issues ───────────────────────────────────────────────
    issues = {
        '页面优化': {
            'color': '#ef4444',
            'items': [
                ('❌','首页有 6 个 H1 标签','严重','#ef4444','30分钟','WordPress 编辑器 → 保留 1 个 H1，其余全改 H2'),
                ('❌','全站核心页面无 Meta Description','严重','#ef4444','1小时','Rank Math → 每页填写 140-160 字独特描述'),
                ('❌','首页 16 张图片无 alt 文字','高','#f59e0b','45分钟','WordPress 媒体库 → 逐一填写含关键词的 alt'),
                ('❌','Contact 页无 Google Maps Embed','高','#f59e0b','15分钟','Google Maps → 分享 → 嵌入地图 → 复制 iframe → 粘贴'),
            ]
        },
        'Schema': {
            'color': '#3b82f6',
            'items': [
                ('❌','全站无 LocalBusiness Schema','严重','#ef4444','10分钟','Rank Math → Schema → 新增 LocalBusiness，type 选 HomeAndConstructionBusiness'),
                ('❌','全站无 BreadcrumbList Schema','严重','#ef4444','5分钟','Rank Math → 全局设置 → Breadcrumbs → 启用'),
                ('❌','博文无 Article Schema','高','#f59e0b','5分钟','Rank Math → 内容类型设置 → 博文 → 启用 Article schema'),
                ('❌','无 Organization Schema','高','#f59e0b','10分钟','Rank Math → General Settings → Knowledge Graph → 填写品牌信息'),
            ]
        },
        'AI 可见度': {
            'color': '#8b5cf6',
            'items': [
                ('❌','无 /llms.txt 文件','高','#f59e0b','15分钟','在网站根目录创建 /llms.txt，填入品牌简介和核心页面链接'),
                ('❌','AI 爬虫访问未明确授权','严重','#ef4444','10分钟','robots.txt 确认允许 GPTBot、ClaudeBot、GoogleOther'),
            ]
        },
        '本地 SEO': {
            'color': '#f59e0b',
            'items': [
                ('❌','Contact 页无 Google Maps Embed','严重','#ef4444','15分钟','嵌入 Google Maps iframe 提升本地排名信号'),
                ('❌','无 Google Business Profile 验证','高','#f59e0b','1小时','前往 business.google.com 认领并验证石材店 GBP'),
            ]
        },
        '内容': {
            'color': '#10b981',
            'items': [
                ('❌','重复博文 URL（两篇高度相似）','高','#f59e0b','30分钟','/which-stone-fits-your-lifestyle-practical-guide/ → 301 重定向至完整版'),
                ('❌','石材类型页描述雷同','中','#6b7280','2小时','为每种石材（Marble/Granite/Quartzite）写独特价值主张'),
                ('❌','无隐私政策页面','中','#6b7280','30分钟','添加 Privacy Policy 页（PDPA 合规要求）'),
            ]
        },
        '性能': {
            'color': '#6366f1',
            'items': [
                ('❌','页面性能未经 PageSpeed 测试','高','#f59e0b','30分钟','前往 pagespeed.web.dev 测试，目标 LCP < 2.5s'),
                ('❌','大量图片可能未压缩','中','#6b7280','1小时','用 Smush 或 ShortPixel 插件批量压缩现有图片'),
            ]
        },
    }

    total_issues = sum(len(v['items']) for v in issues.values())
    fixed = 0
    pct = round(fixed / total_issues * 100) if total_issues else 0
    quick_wins = [item for cat in issues.values() for item in cat['items'] if '分钟' in item[4] and int(item[4].replace('分钟','')) <= 15]

    # quick wins HTML
    qw_html = ''
    for _,title,_,_,time,fix in quick_wins:
        qw_html += f'''<div style="display:flex;align-items:flex-start;gap:10px;background:white;border-radius:8px;padding:10px 12px;margin-bottom:6px;box-shadow:0 1px 2px rgba(0,0,0,.05);">
        <span style="background:#f59e0b;color:white;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;">⚡</span>
        <div style="flex:1;">
            <div style="font-size:12px;font-weight:600;">{title}</div>
            <div style="font-size:11px;color:#888;margin-top:2px;">{fix}</div>
        </div>
        <span style="font-size:11px;color:#888;flex-shrink:0;white-space:nowrap;">{time}</span>
    </div>'''

    # checklist HTML
    checklist_html = ''
    for cat, data in issues.items():
        fixed_in_cat = sum(1 for i in data['items'] if i[0] == '✅')
        total_in_cat = len(data['items'])
        rows = ''
        for icon,title,pri,pcol,time,fix in data['items']:
            done_style = 'opacity:0.6;' if icon == '✅' else ''
            title_style = 'text-decoration:line-through;color:#999;' if icon == '✅' else ''
            rows += f'''<tr style="border-bottom:1px solid #f3f4f6;{done_style}">
            <td style="padding:8px 10px;font-size:12px;">{icon}</td>
            <td style="padding:8px 10px;font-size:12px;{title_style}">{title}</td>
            <td style="padding:8px 10px;text-align:center;"><span style="background:{pcol}22;color:{pcol};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">{pri}</span></td>
            <td style="padding:8px 10px;font-size:11px;color:#888;">{time}</td>
            <td style="padding:8px 10px;font-size:11px;color:#555;max-width:200px;">{fix}</td>
        </tr>'''
        checklist_html += f'''<div style="margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="background:{data['color']};color:white;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700;">{cat}</span>
            <span style="font-size:12px;color:#888;">{fixed_in_cat}/{total_in_cat} 已修复</span>
        </div>
        <div style="background:white;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06);">
        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:#f8fafc;border-bottom:2px solid #e5e7eb;">
                <th style="padding:7px 10px;font-size:11px;color:#888;text-align:left;width:30px;"></th>
                <th style="padding:7px 10px;font-size:11px;color:#888;text-align:left;">问题</th>
                <th style="padding:7px 10px;font-size:11px;color:#888;text-align:center;width:60px;">优先级</th>
                <th style="padding:7px 10px;font-size:11px;color:#888;text-align:left;width:70px;">工时</th>
                <th style="padding:7px 10px;font-size:11px;color:#888;text-align:left;">修复方法</th>
            </tr>
            {rows}
        </table></div></div>'''

    # GSC keywords
    kw_rows = ''
    for kw in gsc.get('top_keywords', []):
        pos = kw['position']
        bg, col, lbl = kw_status(pos)
        kw_rows += f'''<tr style="border-bottom:1px solid #f3f4f6;">
        <td style="padding:7px 8px;font-size:12px;">{kw['query']}</td>
        <td style="text-align:center;padding:7px 8px;font-size:12px;">{fmt(kw['impressions'])}</td>
        <td style="text-align:center;padding:7px 8px;font-size:12px;font-weight:700;color:{'#16a34a' if kw['clicks']>5 else '#f59e0b' if kw['clicks']>0 else '#ef4444'};">{fmt(kw['clicks'])}</td>
        <td style="text-align:center;padding:7px 8px;font-size:12px;color:{'#16a34a' if pos<=3 else '#f59e0b' if pos<=10 else '#ef4444'};font-weight:700;">#{pos}</td>
        <td style="text-align:center;padding:7px 8px;font-size:12px;">{kw['ctr']}%</td>
        <td style="text-align:center;padding:7px 8px;"><span style="background:{bg};color:{col};padding:2px 6px;border-radius:4px;font-size:11px;">{lbl}</span></td>
    </tr>'''
    if not kw_rows:
        kw_rows = '<tr><td colspan="6" style="padding:20px;text-align:center;color:#94a3b8;font-size:12px;">GSC 数据每周一自动更新</td></tr>'

    # GA4 channels
    total_sessions = ga4.get('total_sessions', 0)
    ch_html = ''
    for ch in ga4.get('channels', []):
        pct_bar = round(ch['sessions'] / total_sessions * 100) if total_sessions else 0
        is_organic = 'Organic' in ch['channel']
        ch_html += f'''<div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;">
            <span style="font-weight:600;color:{'#16a34a' if is_organic else 'inherit'};">{ch['channel']}{'⭐' if is_organic else ''}</span>
            <span style="color:#888;">{fmt(ch['sessions'])} 次</span>
        </div>
        <div style="background:#e5e7eb;border-radius:4px;height:8px;"><div style="background:{'#16a34a' if is_organic else '#94a3b8'};width:{pct_bar}%;height:8px;border-radius:4px;"></div></div>
    </div>'''
    if not ch_html:
        ch_html = '<div style="text-align:center;color:#94a3b8;padding:20px;font-size:12px;">GA4 数据每周一自动更新</div>'

    # SE Ranking score
    sr_score = sr.get('health_score', 0)
    sr_col, _, sr_lbl = sc(sr_score)

    overall_col = '#ef4444' if overall < 50 else '#f59e0b' if overall < 70 else '#16a34a'

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Stone De Art SEO Dashboard</title>
<style>
  * {{ box-sizing:border-box;margin:0;padding:0; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f1f5f9;color:#1a1a1a; }}
  .wrap {{ max-width:960px;margin:0 auto;padding:20px 16px; }}
  .card {{ background:white;border-radius:12px;padding:20px;margin-bottom:14px;box-shadow:0 1px 3px rgba(0,0,0,.07); }}
  h2 {{ font-size:14px;font-weight:700;margin-bottom:14px;color:#1a1a1a; }}
  .g2 {{ display:grid;grid-template-columns:1fr 1fr;gap:14px; }}
  .g4 {{ display:grid;grid-template-columns:repeat(4,1fr);gap:10px; }}
  .g7 {{ display:grid;grid-template-columns:repeat(7,1fr);gap:8px; }}
  table {{ width:100%;border-collapse:collapse; }}
  th {{ font-size:11px;color:#888;font-weight:600;padding:6px 8px;text-align:left;border-bottom:2px solid #f3f4f6; }}
  .tag {{ padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600; }}
  @media(max-width:640px){{.g2,.g4,.g7{{grid-template-columns:1fr 1fr;}}}}
</style>
</head>
<body>
<div class="wrap">

<!-- Header -->
<div class="card" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;background:linear-gradient(135deg,#1e293b,#334155);color:white;">
  <div>
    <div style="font-size:20px;font-weight:800;">Stone De Art SEO Dashboard</div>
    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">{BRAND_DOMAIN} · 更新：{updated} · 每周一自动刷新 · 统计：过去28天</div>
  </div>
  <div style="text-align:center;background:rgba(255,255,255,.1);border-radius:12px;padding:12px 20px;">
    <div style="font-size:40px;font-weight:800;color:{overall_col};">{overall}</div>
    <div style="font-size:12px;color:#94a3b8;">/ 100 SEO 总评分</div>
  </div>
</div>

<!-- Progress Bar -->
<div class="card" style="padding:16px 20px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font-size:13px;font-weight:700;">修复进度</span>
    <span style="font-size:13px;color:#888;">{fixed} / {total_issues} 已完成 ({pct}%)</span>
  </div>
  <div style="background:#e5e7eb;border-radius:4px;height:12px;"><div style="background:#16a34a;width:{max(pct,2)}%;height:12px;border-radius:4px;transition:width 0.3s;"></div></div>
  <div style="display:flex;gap:16px;margin-top:10px;font-size:11px;color:#888;">
    <span>✅ {fixed} 已修复</span>
    <span>❌ {total_issues - fixed} 待修复</span>
    <span>⚡ {len(quick_wins)} 个15分钟内快速修复</span>
  </div>
</div>

<!-- Score Cards -->
<div class="g7" style="margin-bottom:14px;">{score_cards}</div>

<!-- Quick Wins -->
<div class="card">
  <h2>⚡ 快速修复（每项15分钟内完成）</h2>
  {qw_html}
</div>

<!-- GSC + GA4 -->
<div class="g2">
  <div class="card">
    <h2>搜索表现（Google Search Console）</h2>
    <div class="g4" style="margin-bottom:14px;">
      <div style="text-align:center;background:#f8fafc;border-radius:8px;padding:10px;">
        <div style="font-size:22px;font-weight:800;color:#4f46e5;">{fmt(gsc.get('total_clicks'))}</div>
        <div style="font-size:11px;color:#888;">总点击</div>
      </div>
      <div style="text-align:center;background:#f8fafc;border-radius:8px;padding:10px;">
        <div style="font-size:22px;font-weight:800;color:#4f46e5;">{fmt(gsc.get('total_impressions'))}</div>
        <div style="font-size:11px;color:#888;">总曝光</div>
      </div>
      <div style="text-align:center;background:#f8fafc;border-radius:8px;padding:10px;">
        <div style="font-size:22px;font-weight:800;color:#ef4444;">{f"{gsc.get('avg_ctr','—')}%" if gsc.get('avg_ctr') else '—'}</div>
        <div style="font-size:11px;color:#888;">平均CTR</div>
      </div>
      <div style="text-align:center;background:#f8fafc;border-radius:8px;padding:10px;">
        <div style="font-size:22px;font-weight:800;color:#f59e0b;">{"#"+str(gsc.get('avg_position','—')) if gsc.get('avg_position') else '—'}</div>
        <div style="font-size:11px;color:#888;">平均排名</div>
      </div>
    </div>
    <h2 style="font-size:12px;color:#888;margin-bottom:8px;">关键词机会</h2>
    <table>
      <tr><th>关键词</th><th style="text-align:center;">曝光</th><th style="text-align:center;">点击</th><th style="text-align:center;">排名</th><th style="text-align:center;">CTR</th><th style="text-align:center;">状态</th></tr>
      {kw_rows}
    </table>
  </div>
  <div class="card">
    <h2>网站流量（Google Analytics 4）</h2>
    <div style="text-align:center;margin-bottom:14px;">
      <div style="font-size:32px;font-weight:800;color:#4f46e5;">{fmt(total_sessions)}</div>
      <div style="font-size:12px;color:#888;">总访问次数（28天）</div>
    </div>
    {ch_html}
    {'<div style="background:#dcfce7;border-radius:8px;padding:8px 12px;margin:10px 0;font-size:12px;color:#16a34a;">💡 自然搜索访客质量最高，是 SEO 投入的核心回报</div>' if ga4.get('channels') else ''}
    <div style="margin-top:16px;">
      <h2 style="font-size:12px;color:#888;margin-bottom:8px;">技术健康分（SE Ranking）</h2>
      <div style="display:flex;align-items:center;gap:16px;">
        <div style="font-size:36px;font-weight:800;color:{sr_col};">{sr_score or '—'}</div>
        <div style="font-size:12px;color:#888;">
          <div>{sr_lbl} · 更新：{sr.get('updated_at','待上传 PDF')}</div>
          <div style="margin-top:3px;">错误 <span style="color:#ef4444;font-weight:700;">{sr.get('errors',0)}</span> · 警告 <span style="color:#f59e0b;font-weight:700;">{sr.get('warnings',0)}</span> · 提示 {sr.get('notices',0)}</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Full Checklist -->
<div class="card">
  <h2>📋 完整问题清单 & 修复指引</h2>
  <div style="background:#fef9c3;border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:12px;color:#92400e;">
    ⚠️ 优先修复「严重」和「高」优先级问题，这些对排名影响最大。每修复一项，下周 dashboard 会自动更新状态。
  </div>
  {checklist_html}
</div>

</div>
</body>
</html>'''

    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Generated docs/index.html')

if __name__ == '__main__':
    generate()
