# Stone De Art SEO Dashboard

每周一自动更新的 SEO 监控 dashboard。

**公开访问：** https://xueyee821.github.io/stonedeart-seo/

数据来源：Google Search Console + GA4 + SE Ranking

## 手动更新 SE Ranking

```bash
pip install pdfplumber
python3 scripts/update_seranking.py /path/to/audit.pdf
git add data/ docs/index.html
git commit -m "Update SE Ranking"
git push
```
