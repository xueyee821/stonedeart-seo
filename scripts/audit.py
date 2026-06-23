import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

SITE = 'sc-domain:stonedeart.com.my'
GA4_PROPERTY_ID = os.environ.get('GA4_PROPERTY_ID', '')
SERVICE_ACCOUNT_JSON = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '')

SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/analytics.readonly',
]


def get_credentials():
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(SERVICE_ACCOUNT_JSON)
        tmp_path = f.name
    creds = service_account.Credentials.from_service_account_file(tmp_path, scopes=SCOPES)
    os.unlink(tmp_path)
    return creds


def fetch_gsc(creds):
    service = build('searchconsole', 'v1', credentials=creds)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=28)

    result = service.searchanalytics().query(
        siteUrl=SITE,
        body={
            'startDate': str(start_date),
            'endDate': str(end_date),
            'dimensions': ['query'],
            'rowLimit': 50,
            'orderBy': [{'fieldName': 'clicks', 'sortOrder': 'DESCENDING'}],
        }
    ).execute()

    totals = service.searchanalytics().query(
        siteUrl=SITE,
        body={
            'startDate': str(start_date),
            'endDate': str(end_date),
            'dimensions': [],
        }
    ).execute()

    rows = result.get('rows', [])
    total_row = totals.get('rows', [{}])[0] if totals.get('rows') else {}

    return {
        'total_clicks': round(total_row.get('clicks', 0)),
        'total_impressions': round(total_row.get('impressions', 0)),
        'avg_ctr': round(total_row.get('ctr', 0) * 100, 2),
        'avg_position': round(total_row.get('position', 0), 1),
        'top_keywords': [
            {
                'query': r['keys'][0],
                'clicks': round(r.get('clicks', 0)),
                'impressions': round(r.get('impressions', 0)),
                'ctr': round(r.get('ctr', 0) * 100, 2),
                'position': round(r.get('position', 0), 1),
            }
            for r in rows[:20]
        ],
        'period': f'{start_date} ~ {end_date}',
    }


def fetch_ga4(creds):
    if not GA4_PROPERTY_ID:
        return {}
    client = BetaAnalyticsDataClient(credentials=creds)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=28)

    request = RunReportRequest(
        property=GA4_PROPERTY_ID,
        date_ranges=[DateRange(start_date=str(start_date), end_date=str(end_date))],
        metrics=[
            Metric(name='sessions'),
            Metric(name='totalUsers'),
            Metric(name='bounceRate'),
            Metric(name='averageSessionDuration'),
        ],
        dimensions=[Dimension(name='sessionDefaultChannelGroup')],
    )
    response = client.run_report(request)

    channels = []
    for row in response.rows:
        channels.append({
            'channel': row.dimension_values[0].value,
            'sessions': int(row.metric_values[0].value),
            'users': int(row.metric_values[1].value),
        })

    totals = {m.name: m.value for m in response.totals[0].metric_values} if response.totals else {}

    return {
        'total_sessions': int(totals.get('sessions', 0)),
        'total_users': int(totals.get('totalUsers', 0)),
        'bounce_rate': round(float(totals.get('bounceRate', 0)) * 100, 1),
        'avg_session_duration': round(float(totals.get('averageSessionDuration', 0))),
        'channels': sorted(channels, key=lambda x: x['sessions'], reverse=True)[:8],
    }


def main():
    data = {'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'gsc': {}, 'ga4': {}}

    if SERVICE_ACCOUNT_JSON:
        creds = get_credentials()
        try:
            data['gsc'] = fetch_gsc(creds)
            print('GSC OK')
        except Exception as e:
            print(f'GSC error: {e}')
        try:
            data['ga4'] = fetch_ga4(creds)
            print('GA4 OK')
        except Exception as e:
            print(f'GA4 error: {e}')
    else:
        print('No service account — skipping API calls')

    os.makedirs('data', exist_ok=True)
    with open('data/audit.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Saved data/audit.json')


if __name__ == '__main__':
    main()
