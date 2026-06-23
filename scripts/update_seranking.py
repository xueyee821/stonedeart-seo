"""
用法：python3 scripts/update_seranking.py /path/to/audit.pdf
从 SE Ranking 导出的 PDF 提取数据并更新 data/seranking.json + docs/index.html
"""
import sys
import json
import re
import datetime
import os

def parse_pdf(path):
    try:
        import pdfplumber
    except ImportError:
        print('请先安装：pip install pdfplumber')
        sys.exit(1)

    text = ''
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ''

    data = {
        'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'health_score': 0,
        'total_issues': 0,
        'errors': 0,
        'warnings': 0,
        'notices': 0,
        'pages_crawled': 0,
        'urls_found': 0,
        'issues': {},
    }

    m = re.search(r'Health Score[:\s]+(\d+)', text)
    if m:
        data['health_score'] = int(m.group(1))

    m = re.search(r'Pages crawled[:\s]+(\d+)', text, re.IGNORECASE)
    if m:
        data['pages_crawled'] = int(m.group(1))

    m = re.search(r'Errors[:\s]+(\d+)', text, re.IGNORECASE)
    if m:
        data['errors'] = int(m.group(1))

    m = re.search(r'Warnings[:\s]+(\d+)', text, re.IGNORECASE)
    if m:
        data['warnings'] = int(m.group(1))

    m = re.search(r'Notices[:\s]+(\d+)', text, re.IGNORECASE)
    if m:
        data['notices'] = int(m.group(1))

    data['total_issues'] = data['errors'] + data['warnings'] + data['notices']
    return data


def main():
    if len(sys.argv) < 2:
        print('用法：python3 scripts/update_seranking.py /path/to/audit.pdf')
        sys.exit(1)

    pdf_path = sys.argv[1]
    data = parse_pdf(pdf_path)

    os.makedirs('data', exist_ok=True)
    with open('data/seranking.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Updated data/seranking.json — Health Score: {data["health_score"]}')

    os.system('python3 scripts/generate_dashboard.py')


if __name__ == '__main__':
    main()
