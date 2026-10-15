#!/usr/bin/env python3
"""
DIA 澳門數字創新協會官網靜態站生成器（自 MFTEDA 架構遷移）
讀取 content.json，輸出多語言靜態 HTML 到 dist/。

用法:
    python3 build.py

更新網站內容 = 改 content.json → 重新執行 python3 build.py。
"""
import json, html, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
C = json.load(open(os.path.join(ROOT, 'content.json'), encoding='utf-8'))
I18N = C['i18n']
LANGS = [l['code'] for l in C['languages']]
DEFAULT = C['default_lang']
PAGES = ['index', 'about', 'members', 'news', 'policy', 'services', 'partners', 'contact']

def esc(s): return html.escape(str(s), quote=True)

def t(lang, *keys):
    d = I18N[lang]
    for k in keys: d = d[k]
    return d

# ---------------- URL 規則 ----------------
# 默認語言 zh-TW 放根目錄，其他語言在 /zh-CN/ /en/ /pt/ 子目錄
def page_href(page, target_lang, current_lang):
    if target_lang == DEFAULT:
        target = 'index.html' if page == 'index' else f'{page}.html'
    else:
        target = f'{target_lang}/' + ('index.html' if page == 'index' else f'{page}.html')
    prefix = '../' if current_lang != DEFAULT else ''
    return prefix + target

def asset(path, current_lang):
    prefix = '../' if current_lang != DEFAULT else ''
    return prefix + 'assets/' + path

def abs_url(page, lang):
    base = C.get('site_url', 'https://www.diamacao.com').rstrip('/')
    name = 'index.html' if page == 'index' else f'{page}.html'
    path = name if lang == DEFAULT else f'{lang}/{name}'
    return f'{base}/{path}'

# ---------------- SVG 圖標 ----------------
def icon(name, cls=''):
    P = {
        'trending': '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
        'globe': '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        'mail': '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        'calendar': '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        'arrow': '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
        'menu': '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
        'close': '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        'check': '<polyline points="20 6 9 17 4 12"/>',
        'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        'flag': '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
        'cpu': '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
        'coins': '<circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/><path d="m16.71 13.88.7.71-2.82 2.82"/>',
        'leaf': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
        'plane': '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
        'landmark': '<line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
        'network': '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>',
        'ship': '<path d="M2 20c1.4 0 2.8-.7 4-1.4 1.2.7 2.6 1.4 4 1.4s2.8-.7 4-1.4c1.2.7 2.6 1.4 4 1.4 1.4 0 2.8-.7 4-1.4V10l-8-4-8 4v1"/><path d="M6 12v8"/><path d="M18 12v8"/><path d="m2 10 10-5 10 5"/>',
        'sparkles': '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1 1.275-1.275L12 3Z"/>',
        'handshake': '<path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 1 0 3-3 6.18 6.18 0 0 0-8.14-.68l-3 3a5.79 5.79 0 0 0-7.06.87l-.47.28a2 2 0 1 1-3 3 3.74 3.74 0 0 0 2.06 1.57"/>',
        'file': '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
        'eye': '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
        'chart': '<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/>',
        'book': '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
        'award': '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
        'building': '<rect x="4" y="2" width="16" height="20" rx="2"/><line x1="9" y1="22" x2="9" y2="18"/><line x1="15" y1="22" x2="15" y2="18"/><line x1="8" y1="6" x2="10" y2="6"/><line x1="14" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="10" y2="10"/><line x1="14" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="10" y2="14"/><line x1="14" y1="14" x2="16" y2="14"/>',
        'pin': '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
        'search': '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        'pause': '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>',
        'link': '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
        'facebook': '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
        'linkedin': '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
        'instagram': '<rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>',
    }
    c = f' class="{cls}"' if cls else ''
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>')

SOCIAL = [('facebook', 'Facebook'), ('linkedin', 'LinkedIn'), ('instagram', 'Instagram')]

# ---------------- 頁頭 / 頁尾 ----------------
def header(page, lang, pre=''):
    nav = I18N[lang]['nav']
    logo = pre + asset('img/logo-mark.png', lang)
    hp = lambda p: pre + page_href(p, lang, lang)
    links = ''.join(
        f'<a href="{hp(p)}" class="{"active" if p == page else ""}">{esc(nav[p if p != "index" else "home"])}</a>'
        for p in PAGES)
    lang_btn_label = next(l['label'] for l in C['languages'] if l['code'] == lang)
    lang_items = ''.join(
        f'<a href="{pre + page_href(page, l["code"], lang)}" class="{"current" if l["code"] == lang else ""}">{l["flag"]} {esc(l["label"])}</a>'
        for l in C['languages'])
    mlinks = ''.join(
        f'<a href="{hp(p)}" class="mnav {"active" if p == page else ""}">{esc(nav[p if p != "index" else "home"])}</a>'
        for p in PAGES)
    return f'''<header class="site-header">
  <div class="container-institutional">
    <a href="{hp('index')}" class="logo-link"><img src="{logo}" alt="DIA Logo"><span class="logo-word"><b>{esc(C['site_name'])}</b><span>{esc(C['site_name_en'])}</span></span></a>
    <nav class="main-nav">{links}</nav>
    <div class="header-actions">
      <div class="lang-switch">
        <button type="button" aria-haspopup="true">{icon('globe')}{esc(lang_btn_label)}</button>
        <div class="dropdown">{lang_items}</div>
      </div>
      <button class="menu-toggle" id="menu-toggle" aria-label="Menu">{icon('menu')}</button>
    </div>
  </div>
</header>
<div class="panel-overlay" id="panel-overlay"></div>
<aside class="mobile-panel" id="mobile-panel">
  <div style="display:flex;justify-content:flex-end;margin-bottom:1rem;">
    <button class="menu-toggle" onclick="document.getElementById('mobile-panel').classList.remove('open');document.getElementById('panel-overlay').classList.remove('open');" aria-label="Close">{icon('close')}</button>
  </div>
  {mlinks}
  <div class="lang-switch" style="margin-top:1rem;">
    <button type="button" aria-haspopup="true">{icon('globe')}{esc(lang_btn_label)}</button>
    <div class="dropdown" style="position:static;box-shadow:none;border:none;display:block;">{lang_items}</div>
  </div>
</aside>'''

def footer(lang, pre=''):
    nav = I18N[lang]['nav']
    ft = I18N[lang]['footer']
    logo = pre + asset('img/logo-mark.png', lang)
    hp = lambda p: pre + page_href(p, lang, lang)
    social = ''.join(f'<a href="{C["social"][s]}" aria-label="{label}">{icon(s)}</a>' for s, label in SOCIAL)
    return f'''<footer class="site-footer">
  <div class="container-institutional section-spacing">
    <div class="footer-grid">
      <div class="footer-col">
        <img src="{logo}" alt="DIA Logo" style="height:3.5rem;width:auto;margin-bottom:1rem;">
        <p class="desc">{esc(ft['description'])}</p>
        <div class="social-row">{social}</div>
      </div>
      <div class="footer-col">
        <h4>{esc(ft['quickLinks'])}</h4>
        <ul>
          <li><a href="{hp('index')}">{esc(nav['home'])}</a></li>
          <li><a href="{hp('about')}">{esc(nav['about'])}</a></li>
          <li><a href="{hp('members')}">{esc(nav['members'])}</a></li>
          <li><a href="{hp('partners')}">{esc(nav['partners'])}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{esc(ft['updates'])}</h4>
        <ul>
          <li><a href="{hp('news')}">{esc(nav['news'])}</a></li>
          <li><a href="{hp('policy')}">{esc(nav['policy'])}</a></li>
          <li><a href="{hp('services')}">{esc(nav['services'])}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{esc(ft['contactTitle'])}</h4>
        <ul>
          <li><span>{esc(C['address'][lang])}</span></li>
          <li><a href="mailto:{C['email']}">{C['email']}</a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom container-institutional">
    <span>© {C.get('year', 2026)} {esc(C['site_name'])} · {esc(C['site_name_en'])}. {esc(ft['allRightsReserved'])}</span>
    <a href="mailto:{C['email']}">{C['email']}</a>
  </div>
</footer>'''

def page_shell(page, lang, title, description, body, depth=0, url_path=None, og_image=None):
    pre = '../' * depth
    css = pre + asset('css/style.css', lang)
    js = pre + asset('js/main.js', lang)
    lang_links = ''.join(
        f'<link rel="alternate" hreflang="{l}" href="{abs_url(url_path or page, l)}">'
        for l in LANGS)
    canonical = abs_url(url_path or page, lang)
    site_url = C.get('site_url', 'https://www.diamacao.com').rstrip('/')
    og_image = og_image or (site_url + '/assets/img/og-cover.jpg')
    og_locale = {'zh-TW': 'zh_TW', 'zh-CN': 'zh_CN', 'en': 'en_US', 'pt': 'pt_PT'}[lang]
    site_name = {'zh-TW': C['site_name'], 'zh-CN': '澳门数字创新协会', 'en': C['site_name_en'], 'pt': C['site_name_pt']}[lang]
    jsonld = ''
    if page == 'index':
        jsonld = f'''<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Organization","name":"{site_name}","alternateName":"{C['site_name_en']}","url":"{site_url}","logo":"{site_url}/assets/img/logo.png","email":"{C['email']}","address":{{"@type":"PostalAddress","streetAddress":"{esc(C['address'][lang])}","addressCountry":"MO"}}}}
  </script>'''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} - {esc(site_name)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="{'website' if page == 'index' else 'article'}">
  <meta property="og:site_name" content="DIA · {esc(site_name)}">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" type="image/png" href="{pre + asset('img/favicon.png', lang)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css}">
  <noscript><style>.reveal{{opacity:1 !important;transform:none !important;}}</style></noscript>
  {lang_links}
  {jsonld}
</head>
<body>
{header(page, lang, pre)}
<main>
{body}
</main>
{footer(lang, pre)}
<script src="{js}" defer></script>
</body>
</html>'''

def page_hero(lang, section):
    return f'''<section class="page-hero">
  <div class="container-institutional">
    <div class="reveal">
      <h1 class="institutional-heading">{esc(t(lang, section, 'title'))}</h1>
      <p class="sub text-muted-foreground">{esc(t(lang, section, 'subtitle'))}</p>
    </div>
  </div>
</section>'''

def news_card(lang, a):
    ins = I18N[lang]['news']
    return f'''
      <div class="institutional-card insight-card reveal">
        <div class="insight-meta">
          <span class="badge">{esc(a['category'][lang])}</span>
          <span class="date">{icon('calendar')}{a['date']}</span>
          <span class="source">{esc(a['source']['name'][lang])}</span>
        </div>
        <h3>{esc(a['title'][lang])}</h3>
        <p>{esc(a['excerpt'][lang])}</p>
        <a class="read-more" href="news/{a['slug']}.html">{esc(ins['readMore'])}{icon('arrow')}</a>
      </div>'''

def policy_card(lang, p):
    more = t(lang, 'policy', 'learnMore')
    return f'''
      <div class="institutional-card insight-card reveal">
        <div class="insight-meta">
          <span class="badge">{esc(p['issuer'][lang])}</span>
          <span class="date">{icon('calendar')}{p['date']}</span>
        </div>
        <h3>{esc(p['title'][lang])}</h3>
        <p>{esc(p['summary'][lang])}</p>
        <a class="read-more" href="{p['url']}" target="_blank" rel="noopener">{esc(more)}{icon('arrow')}</a>
      </div>'''

# ---------------- 首頁 ----------------
def render_index(lang):
    hero = I18N[lang]['hero']
    home = I18N[lang]['home']
    cards = ''
    for card in C['focus_cards']:
        cards += f'''<div class="institutional-card text-center reveal">
        <div class="icon-badge">{icon(card['icon'])}</div>
        <h3 style="font-size:1.375rem;font-weight:600;margin-bottom:1rem;">{esc(card['title'][lang])}</h3>
        <p class="text-muted-foreground" style="line-height:1.625;">{esc(card['description'][lang])}</p>
      </div>'''
    stats = ''
    for s in C['stats']:
        stats += f'''<div class="reveal"><div class="num">{esc(s['num'])}</div><div class="lbl">{esc(s['label'][lang])}</div></div>'''
    latest_news = ''.join(news_card(lang, a) for a in sorted(C['news'], key=lambda x: x['date'], reverse=True)[:3])
    latest_policies = ''.join(policy_card(lang, p) for p in sorted(C['policies'], key=lambda x: x['date'], reverse=True)[:3])
    body = f'''
<section class="hero" style="background-image:url('{asset('img/hero-bg.webp', lang)}')">
  <div class="container-institutional">
    <div class="reveal">
      <img class="hero-logo" src="{asset('img/logo-mark.png', lang)}" alt="{esc(C['site_name'])}">
      <h1>{esc(hero['headline'])}</h1>
      <p class="sub">{esc(hero['subtitle'])}</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="{page_href('about', lang, lang)}">{esc(hero['cta1'])}{icon('arrow')}</a>
        <a class="btn btn-secondary" href="{page_href('policy', lang, lang)}">{esc(hero['cta2'])}</a>
        <a class="btn btn-glass" href="{page_href('contact', lang, lang)}">{esc(hero['cta3'])}</a>
      </div>
    </div>
  </div>
</section>
<section class="stats-band section-spacing" style="padding-top:3rem;padding-bottom:3rem;">
  <div class="container-institutional">
    <div class="stats-grid">{stats}</div>
  </div>
</section>
<section class="section-spacing">
  <div class="container-institutional">
    <div class="text-center mb-16 reveal">
      <h2 class="institutional-subheading mb-4">{esc(home['focusTitle'])}</h2>
      <p class="text-lg text-muted-foreground max-w-2 mx-auto" style="font-size:1.125rem;">{esc(home['focusSub'])}</p>
    </div>
    <div class="grid grid-3">{cards}</div>
  </div>
</section>
<section class="section-spacing escort-band">
  <div class="container-institutional text-center reveal">
    <h2 class="institutional-subheading mb-4">{esc(home['escortTitle'])}</h2>
    <p class="lead">{esc(home['escortLead'])}</p>
    <a class="btn btn-white" href="{page_href('services', lang, lang)}">{esc(home['escortCta'])}{icon('arrow')}</a>
  </div>
</section>
<section class="section-spacing bg-muted-50">
  <div class="container-institutional">
    <div class="text-center mb-16 reveal">
      <h2 class="institutional-subheading mb-4">{esc(home['newsTitle'])}</h2>
      <a class="read-more" href="{page_href('news', lang, lang)}">{esc(home['viewAll'])}{icon('arrow')}</a>
    </div>
    <div class="grid grid-3">{latest_news}</div>
  </div>
</section>
<section class="section-spacing">
  <div class="container-institutional">
    <div class="text-center mb-16 reveal">
      <h2 class="institutional-subheading mb-4">{esc(home['policyTitle'])}</h2>
      <a class="read-more" href="{page_href('policy', lang, lang)}">{esc(home['viewAll'])}{icon('arrow')}</a>
    </div>
    <div class="grid grid-3">{latest_policies}</div>
  </div>
</section>
<section class="section-spacing cta-band">
  <div class="container-institutional">
    <div class="reveal">
      <h2 class="institutional-subheading mb-6">{esc(home['ctaBandTitle'])}</h2>
      <p class="lead">{esc(home['ctaBandLead'])}</p>
      <a class="btn btn-white" href="{page_href('contact', lang, lang)}">{esc(t(lang, 'nav', 'contact'))}{icon('arrow')}</a>
    </div>
  </div>
</section>'''
    return page_shell('index', lang, t(lang, 'nav', 'home'), hero['subtitle'], body)

# ---------------- 關於我們 ----------------
def render_about(lang):
    ab = I18N[lang]['about']
    paras = ''.join(f'<p>{esc(p)}</p>' for p in ab['purpose'])
    objectives = ''.join(f'''
      <div class="obj-item reveal">
        <div class="icon-badge xs">{icon('check')}</div>
        <p>{esc(ab[f'objective{i}'])}</p>
      </div>''' for i in range(1, 5))
    areas_icons = ['cpu', 'plane', 'handshake', 'users', 'globe', 'chart']
    areas = ''.join(f'''
      <div class="institutional-card focus-item reveal">
        <div class="icon-badge xs">{icon(areas_icons[i])}</div>
        <span class="label">{esc(ab[f'area{i+1}'])}</span>
      </div>''' for i in range(6))
    body = page_hero(lang, 'about') + f'''
<section class="section-spacing">
  <div class="container-institutional">
    <div class="max-w-5 mx-auto reveal">
      <div class="purpose-card">
        <h2>{esc(ab['purposeTitle'])}</h2>
        <div>{paras}</div>
      </div>
    </div>
  </div>
</section>
<section class="section-spacing bg-muted-50">
  <div class="container-institutional">
    <div class="grid grid-2 max-w-6 mx-auto mb-16">
      <div class="institutional-card no-border shadow-md reveal">
        <div class="icon-badge sm">{icon('eye')}</div>
        <h3 style="font-size:1.5rem;font-weight:600;margin-bottom:.5rem;">{esc(ab['visionTitle'])}</h3>
        <p class="text-lg text-muted-foreground" style="line-height:1.75;">{esc(ab['visionText'])}</p>
      </div>
      <div class="institutional-card no-border shadow-md reveal">
        <div class="icon-badge sm secondary">{icon('flag')}</div>
        <h3 style="font-size:1.5rem;font-weight:600;margin-bottom:.5rem;">{esc(ab['missionTitle'])}</h3>
        <p class="text-lg text-muted-foreground" style="line-height:1.75;">{esc(ab['missionText'])}</p>
      </div>
    </div>
    <div class="max-w-5 mx-auto">
      <h3 style="font-size:1.5rem;font-weight:600;text-align:center;margin-bottom:2rem;">{esc(ab['objectivesTitle'])}</h3>
      <div class="grid grid-2">{objectives}</div>
    </div>
  </div>
</section>
<section class="section-spacing">
  <div class="container-institutional">
    <h2 class="institutional-subheading text-center mb-12 reveal">{esc(ab['areasTitle'])}</h2>
    <div class="grid grid-3 max-w-5 mx-auto">{areas}</div>
  </div>
</section>'''
    return page_shell('about', lang, ab['title'], ab['subtitle'], body)

# ---------------- 架構成員 ----------------
def render_members(lang):
    mb = I18N[lang]['members']
    leaders = ''
    for m in C['members']:
        leaders += f'''
      <div class="institutional-card member-card reveal">
        <div class="member-avatar">{esc(m['initial'])}</div>
        <h3>{esc(m['name'][lang])}</h3>
        <div class="member-role">{esc(m['role'][lang])}</div>
        <p class="member-bio">{esc(m['bio'][lang])}</p>
      </div>'''
    orgs = ''
    for o in C['org']:
        orgs += f'''
      <div class="institutional-card org-item reveal">
        <div class="icon-badge sm">{icon(o['icon'])}</div>
        <div>
          <h3>{esc(o['title'][lang])}</h3>
          <p>{esc(o['desc'][lang])}</p>
        </div>
      </div>'''
    body = page_hero(lang, 'members') + f'''
<section class="section-spacing">
  <div class="container-institutional">
    <h2 class="institutional-subheading text-center mb-12 reveal">{esc(mb['leadersTitle'])}</h2>
    <div class="grid grid-2 max-w-5 mx-auto">{leaders}</div>
    <p class="text-center text-muted-foreground mt-8 reveal" style="max-width:44rem;margin-left:auto;margin-right:auto;">{esc(mb['note'])}</p>
  </div>
</section>
<section class="section-spacing bg-muted-50">
  <div class="container-institutional">
    <h2 class="institutional-subheading text-center mb-12 reveal">{esc(mb['orgTitle'])}</h2>
    <div class="grid grid-3">{orgs}</div>
  </div>
</section>'''
    return page_shell('members', lang, mb['title'], mb['subtitle'], body)

# ---------------- 新聞動態 ----------------
def render_news(lang):
    nw = I18N[lang]['news']
    cards = ''.join(news_card(lang, a) for a in sorted(C['news'], key=lambda x: x['date'], reverse=True))
    body = page_hero(lang, 'news') + f'''
<section class="section-spacing">
  <div class="container-institutional">
    <div class="grid grid-3">{cards}</div>
  </div>
</section>'''
    return page_shell('news', lang, nw['title'], nw['subtitle'], body)

def render_news_article(lang, a):
    nw = I18N[lang]['news']
    body_html = ''.join(
        f'<p style="line-height:1.875;margin-bottom:1.25rem;color:hsl(var(--foreground));">{esc(para)}</p>'
        for para in a['body'][lang])
    src_name = a['source']['name'][lang]
    quoted = f'《{src_name}》' if lang.startswith('zh') else src_name
    source_html = f'''<div class="article-source">
        {esc(nw['sourcePrefix'])} <a href="{esc(a['source']['url'])}" target="_blank" rel="noopener">{esc(quoted)}</a>
      </div>'''
    body = f'''
<section class="page-hero">
  <div class="container-institutional">
    <div class="reveal max-w-5 mx-auto">
      <div class="insight-meta" style="justify-content:center;">
        <span class="badge">{esc(a['category'][lang])}</span>
        <span class="date">{icon('calendar')}{a['date']}</span>
        <span class="source">{esc(a['source']['name'][lang])}</span>
      </div>
      <h1 class="institutional-heading" style="font-size:clamp(1.75rem,3.5vw,2.5rem);">{esc(a['title'][lang])}</h1>
    </div>
  </div>
</section>
<section class="section-spacing" style="padding-top:0;">
  <div class="container-institutional">
    <div class="max-w-5 mx-auto institutional-card" style="padding:clamp(1.5rem,4vw,3rem);">
      <div>{body_html}</div>
      {source_html}
      <div style="margin-top:2.5rem;padding-top:1.5rem;border-top:1px solid hsl(var(--border));">
        <a class="read-more" href="../news.html">{icon('arrow')} {esc(nw['backToNews'])}</a>
      </div>
    </div>
  </div>
</section>'''
    return page_shell('news', lang, a['title'][lang], a['excerpt'][lang], body,
                      depth=1, url_path=f'news/{a["slug"]}')

# ---------------- 出海政策 ----------------
def render_policy(lang):
    pl = I18N[lang]['policy']
    sections_html = ''
    for i, region in enumerate(('national', 'gba', 'macao', 'global')):
        cards = ''.join(policy_card(lang, p) for p in sorted((x for x in C['policies'] if x['region'] == region), key=lambda x: x['date'], reverse=True))
        sections_html += f'''
<section class="section-spacing{' bg-muted-50' if i % 2 else ''}">
  <div class="container-institutional">
    <h2 class="institutional-subheading text-center mb-12 reveal">{esc(pl['regions'][region])}</h2>
    <div class="grid grid-3">{cards}
    </div>
  </div>
</section>'''
    body = page_hero(lang, 'policy') + sections_html
    return page_shell('policy', lang, pl['title'], pl['subtitle'], body)

# ---------------- 出海護航 ----------------
def render_services(lang):
    sv = I18N[lang]['services']
    E = C['escort']
    stats = ''.join(f'''
      <div class="escort-stat reveal">
        <div class="escort-stat-num">{esc(s['num'][lang])}</div>
        <p>{esc(s['text'][lang])}</p>
      </div>''' for s in E['s1']['stats'])
    circles = ''.join(f'''
      <div class="escort-circle reveal"><b>{esc(c['k'][lang])}</b><span>{esc(c['v'][lang])}</span></div>''' for c in E['s2']['circles'])
    tiers = ''.join(f'''
      <div class="escort-tier reveal">
        <span class="escort-tier-k">{esc(tr['k'][lang])}</span>
        <p>{esc(tr['v'][lang])}</p>
      </div>''' for tr in E['s2']['tiers'])
    steps = ''
    for i, st in enumerate(E['s3']['flow']):
        if i:
            steps += f'<div class="escort-flow-arrow">{icon("arrow")}</div>'
        state = esc(E['s3']['present' if st['present'] else 'absent'][lang])
        steps += f'''
      <div class="escort-flow-step{' on' if st['present'] else ''} reveal">
        <b>{esc(st['k'][lang])}</b><span>{state}</span>
      </div>'''
    pain_icons = ['search', 'shield', 'pause', 'link']
    pains = ''.join(f'''
      <div class="institutional-card escort-pain reveal">
        <div class="icon-badge xs">{icon(pain_icons[i])}</div>
        <div>
          <h3>{esc(p['title'][lang])}</h3>
          <p>{esc(p['desc'][lang])}</p>
        </div>
      </div>''' for i, p in enumerate(E['s3']['pains']))
    svc_icons = ['globe', 'users', 'sparkles']
    svcs = ''.join(f'''
      <div class="institutional-card escort-svc reveal">
        <div class="icon-badge">{icon(svc_icons[i])}</div>
        <h3>{esc(s['title'][lang])}</h3>
        <div class="escort-svc-sub">{esc(s['sub'][lang])}</div>
        <p class="text-muted-foreground">{esc(s['desc'][lang])}</p>
      </div>''' for i, s in enumerate(E['s4']['services']))
    chips = ''.join(f'<span class="escort-chip reveal">{esc(s[lang])}</span>' for s in E['s4']['supports'])
    sup = E['s4']['support']
    phones = ' / '.join(sup['phones'])
    def section(sec, muted):
        return f'''
<section class="section-spacing{' bg-muted-50' if muted else ''}">
  <div class="container-institutional">
    <h2 class="institutional-subheading text-center mb-6 reveal">{esc(sec['title'][lang])}</h2>
    <p class="escort-lead reveal">{esc(sec['lead'][lang])}</p>
    {{BODY}}
    <div class="escort-tagline reveal">{esc(sec['tagline'][lang])}</div>
  </div>
</section>'''
    s1 = section(E['s1'], False).replace('{BODY}', f'<div class="escort-stats max-w-5 mx-auto">{stats}</div>')
    s2 = section(E['s2'], True).replace('{BODY}', f'<div class="escort-circles">{circles}</div><div class="escort-tiers max-w-5 mx-auto">{tiers}</div>')
    s3 = section(E['s3'], False).replace('{BODY}', f'<div class="escort-flow">{steps}</div><div class="grid grid-2 max-w-5 mx-auto">{pains}</div>')
    s4_body = (f'<div class="grid grid-3">{svcs}</div>'
               f'<h3 class="escort-supports-title reveal">{esc(E["s4"]["supportsTitle"][lang])}</h3>'
               f'<div class="escort-chips">{chips}</div>'
               f'''<div class="escort-support-note reveal">
      <p>{esc(sup['note'][lang])}</p>
      <p class="escort-support-contact">{esc(sup['contactLabel'][lang])}：{esc(sup['person'][lang])} {phones} · {esc(sup['siteLabel'][lang])}: <a href="{sup['siteUrl']}" target="_blank" rel="noopener">{sup['site']}</a></p>
    </div>''')
    s4 = section(E['s4'], True).replace('{BODY}', s4_body)
    body = page_hero(lang, 'services') + s1 + s2 + s3 + s4
    return page_shell('services', lang, sv['title'], sv['subtitle'], body)

# ---------------- 合作夥伴 ----------------
def render_partners(lang):
    pt = I18N[lang]['partners']
    cards = ''
    for i, p in enumerate(C['partners'], 1):
        logo_path = os.path.join(ROOT, 'assets', 'img', 'partners', f'partner{i}.webp')
        logo_html = ''
        if os.path.exists(logo_path):
            logo_html = (f'<div class="partner-logo">'
                         f'<img src="{asset(f"img/partners/partner{i}.webp", lang)}" alt="{esc(p["name"][lang])}" loading="lazy">'
                         f'</div>')
        cards += f'''
      <a class="institutional-card partner-card reveal" href="{p['href']}"{' target="_blank" rel="noopener"' if p['href'] != '#' else ''} style="display:flex;">
        {logo_html}
        <h3>{esc(p['name'][lang])}</h3>
        <p class="pdesc">{esc(p['desc'][lang])}</p>
      </a>'''
    body = page_hero(lang, 'partners') + f'''
<section class="section-spacing">
  <div class="container-institutional">
    <div class="grid grid-3">{cards}</div>
  </div>
</section>'''
    return page_shell('partners', lang, pt['title'], pt['subtitle'], body)

# ---------------- 聯繫我們 ----------------
def render_contact(lang):
    ct = I18N[lang]['contact']
    social = ''.join(f'<a href="{C["social"][s]}" aria-label="{label}">{icon(s)}</a>' for s, label in SOCIAL)
    inquiry_opts = ''.join(f'<option value="{k}">{esc(v)}</option>' for k, v in ct['inquiryTypes'].items())
    err_req, err_email, submitting = esc(ct['errorRequired']), esc(ct['errorEmail']), esc(ct['submitting'])
    body = page_hero(lang, 'contact') + f'''
<section class="section-spacing">
  <div class="container-institutional">
    <div class="contact-grid">
      <div class="institutional-card reveal">
        <div class="contact-info">
          <h3>{esc(ct['orgName'])}</h3>
          <div class="info-row">
            <div class="label">{icon('pin')}<span>{esc(ct['addressLabel'])}</span></div>
            <span class="v">{esc(C['address'][lang])}</span>
          </div>
          <div class="info-row">
            <div class="label">{icon('mail')}<span>{esc(ct['email'])}</span></div>
            <a href="mailto:{C['email']}">{C['email']}</a>
          </div>
          <div class="info-row">
            <span style="font-weight:500;color:hsl(var(--muted-foreground));display:block;margin-bottom:.75rem;">{esc(ct['followUs'])}</span>
            <div class="social-row">{social}</div>
          </div>
        </div>
      </div>
      <div class="institutional-card reveal" data-tabs>
        <div class="tabs">
          <button type="button" data-tab="contact" class="active">{esc(ct['contactForm'])}</button>
          <button type="button" data-tab="cooperation">{esc(ct['cooperationForm'])}</button>
        </div>
        <form class="ajax-form tab-pane active" data-pane="contact" data-err-required="{err_req}" data-err-email="{err_email}" data-submitting="{submitting}" novalidate>
          <div class="form-group">
            <label for="c-name">{esc(ct['name'])}</label>
            <input id="c-name" name="name" type="text" placeholder="{esc(ct['namePlaceholder'])}" required>
            <p class="err-msg" data-for="name"></p>
          </div>
          <div class="form-group">
            <label for="c-email">{esc(ct['emailLabel'])}</label>
            <input id="c-email" name="email" type="email" placeholder="{esc(ct['emailPlaceholder'])}" required>
            <p class="err-msg" data-for="email"></p>
          </div>
          <div class="form-group">
            <label for="c-message">{esc(ct['message'])}</label>
            <textarea id="c-message" name="message" placeholder="{esc(ct['messagePlaceholder'])}" required></textarea>
            <p class="err-msg" data-for="message"></p>
          </div>
          <button type="submit" class="btn btn-primary">{esc(ct['submit'])}</button>
          <div class="form-toast">{icon('check')}{esc(ct['successMessage'])}</div>
        </form>
        <form class="ajax-form tab-pane" data-pane="cooperation" data-err-required="{err_req}" data-err-email="{err_email}" data-submitting="{submitting}" novalidate>
          <div class="form-group">
            <label for="o-org">{esc(ct['organization'])}</label>
            <input id="o-org" name="organization" type="text" placeholder="{esc(ct['organizationPlaceholder'])}" required>
            <p class="err-msg" data-for="organization"></p>
          </div>
          <div class="form-group">
            <label for="o-type">{esc(ct['inquiryType'])}</label>
            <select id="o-type" name="inquiryType" required>
              <option value="">{esc(ct['inquiryTypePlaceholder'])}</option>
              {inquiry_opts}
            </select>
            <p class="err-msg" data-for="inquiryType"></p>
          </div>
          <div class="form-group">
            <label for="o-email">{esc(ct['emailLabel'])}</label>
            <input id="o-email" name="email" type="email" placeholder="{esc(ct['emailPlaceholder'])}" required>
            <p class="err-msg" data-for="email"></p>
          </div>
          <div class="form-group">
            <label for="o-message">{esc(ct['message'])}</label>
            <textarea id="o-message" name="message" placeholder="{esc(ct['messagePlaceholder'])}" required></textarea>
            <p class="err-msg" data-for="message"></p>
          </div>
          <button type="submit" class="btn btn-primary">{esc(ct['submit'])}</button>
          <div class="form-toast">{icon('check')}{esc(ct['successMessage'])}</div>
        </form>
      </div>
    </div>
  </div>
</section>'''
    return page_shell('contact', lang, ct['title'], ct['subtitle'], body)

# ---------------- 構建 ----------------
RENDERERS = {'index': render_index, 'about': render_about, 'members': render_members,
             'news': render_news, 'policy': render_policy, 'services': render_services,
             'partners': render_partners, 'contact': render_contact}

def build():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(DIST, 'assets'))
    with open(os.path.join(DIST, 'CNAME'), 'w') as f:
        f.write('www.diamacao.com\n')

    with open(os.path.join(DIST, 'robots.txt'), 'w') as f:
        f.write('User-agent: *\nAllow: /\n\nSitemap: https://www.diamacao.com/sitemap.xml\n')

    not_found_body = f'''
<section class="page-hero">
  <div class="container-institutional">
    <div class="reveal">
      <h1 class="institutional-heading">404</h1>
      <p class="sub text-muted-foreground">{esc({'zh-TW': '頁面不存在或已被移動', 'zh-CN': '页面不存在或已被移动', 'en': 'The page you are looking for does not exist or has been moved.', 'pt': 'A página que procura não existe ou foi movida.'}[DEFAULT])}</p>
      <div class="cta-row" style="margin-top:2rem;display:flex;justify-content:center;">
        <a class="btn btn-primary" href="index.html">{esc({'zh-TW': '返回首頁', 'zh-CN': '返回首页', 'en': 'Back to Home', 'pt': 'Voltar ao Início'}[DEFAULT])}{icon('arrow')}</a>
      </div>
    </div>
  </div>
</section>'''
    with open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8') as f:
        f.write(page_shell('index', DEFAULT, '404', 'Page not found', not_found_body))

    count = 2
    urls = []
    for lang in LANGS:
        outdir = DIST if lang == DEFAULT else os.path.join(DIST, lang)
        os.makedirs(outdir, exist_ok=True)
        for page in PAGES:
            html_out = RENDERERS[page](lang)
            name = 'index.html' if page == 'index' else f'{page}.html'
            with open(os.path.join(outdir, name), 'w', encoding='utf-8') as f:
                f.write(html_out)
            urls.append((page, lang))
            count += 1
        for a in C['news']:
            ndir = os.path.join(outdir, 'news')
            os.makedirs(ndir, exist_ok=True)
            with open(os.path.join(ndir, f'{a["slug"]}.html'), 'w', encoding='utf-8') as f:
                f.write(render_news_article(lang, a))
            urls.append((f'news/{a["slug"]}', lang))
            count += 1

    xhtml = 'xmlns:xhtml="http://www.w3.org/1999/xhtml"'
    items = []
    for page, lang in urls:
        loc = abs_url(page, lang)
        alts = ''.join(
            f'\n      <xhtml:link rel="alternate" hreflang="{l}" href="{abs_url(page, l)}"/>'
            for l in LANGS)
        items.append(f'''  <url>
      <loc>{loc}</loc>{alts}
      <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(page, DEFAULT)}"/>
  </url>''')
    with open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" {xhtml}>\n'
                + '\n'.join(items) + '\n</urlset>\n')
    print(f'OK: generated {count} files -> {DIST}')

if __name__ == '__main__':
    build()
