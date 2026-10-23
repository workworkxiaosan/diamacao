#!/usr/bin/env python3
"""DIA 官網（www.diamacao.com）健康與安全監控，僅用標準庫。

用法：python3 monitor.py
輸出逐項 OK/WARN/FAIL 報告；有 FAIL 時 exit 1，否則 exit 0。
供每日定時巡查（cron）與人工複查使用。
"""
import datetime
import socket
import ssl
import sys
import urllib.request
import urllib.error

BASE = "https://www.diamacao.com"
HOSTS = ["www.diamacao.com", "diamacao.com"]
GITHUB_IPS = {
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153",
}
PAGES = [
    "/", "/about.html", "/members.html", "/news.html", "/policy.html",
    "/services.html", "/partners.html", "/contact.html",
    "/zh-CN/", "/en/", "/pt/", "/fr/", "/sitemap.xml", "/robots.txt",
]
HOME_MARKERS = ["澳門數字創新協會", "數字引領", "首批經澳門出海對接企業"]
CERT_WARN_DAYS = 30
TIMEOUT = 20
UA = {"User-Agent": "DIA-Site-Monitor/1.0 (+https://www.diamacao.com)"}

results = []


def report(level, name, detail):
    results.append((level, name, detail))
    print(f"[{level:4}] {name}: {detail}")


def check_dns():
    for host in HOSTS:
        try:
            infos = socket.getaddrinfo(host, 443, socket.AF_INET)
            ips = {i[4][0] for i in infos}
            if ips and ips <= GITHUB_IPS:
                report("OK", f"DNS {host}", " -> ".join(sorted(ips)))
            else:
                report("FAIL", f"DNS {host}", f"解析到非 GitHub Pages 地址：{sorted(ips)}")
        except OSError as e:
            report("FAIL", f"DNS {host}", f"解析失敗：{e}")


def check_tls():
    for host in HOSTS:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as tls:
                    cert = tls.getpeercert()
                    exp = ssl.cert_time_to_seconds(cert["notAfter"])
                    days = int((exp - datetime.datetime.now().timestamp()) // 86400)
                    issuer = dict(x[0] for x in cert["issuer"])
                    level = "OK" if days >= CERT_WARN_DAYS else "WARN"
                    report(level, f"TLS {host}",
                           f"驗證通過，{days} 天後到期（簽發者 {issuer.get('organizationName', '?')}）")
        except (OSError, ssl.SSLError) as e:
            report("FAIL", f"TLS {host}", f"證書驗證/連線失敗：{e}")


def fetch(url, method="GET"):
    req = urllib.request.Request(url, headers=UA, method=method)
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def check_pages():
    for path in PAGES:
        url = BASE + path
        try:
            with fetch(url) as resp:
                if resp.status == 200:
                    report("OK", f"頁面 {path}", "HTTP 200")
                else:
                    report("FAIL", f"頁面 {path}", f"HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            report("FAIL", f"頁面 {path}", f"HTTP {e.code}")
        except (urllib.error.URLError, OSError) as e:
            report("FAIL", f"頁面 {path}", f"請求失敗：{e}")


def check_content():
    try:
        with fetch(BASE + "/") as resp:
            html = resp.read().decode("utf-8", "replace")
        missing = [m for m in HOME_MARKERS if m not in html]
        if missing:
            report("FAIL", "首頁內容完整性", f"缺少標記 {missing}，疑似篡改或部署異常")
        else:
            report("OK", "首頁內容完整性", "關鍵內容標記齊全")
    except (urllib.error.URLError, OSError) as e:
        report("FAIL", "首頁內容完整性", f"無法檢查：{e}")


def check_apex_redirect():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    try:
        req = urllib.request.Request("https://diamacao.com/", headers=UA, method="HEAD")
        with opener.open(req, timeout=TIMEOUT) as resp:
            status, location = resp.status, resp.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        status, location = e.code, e.headers.get("Location", "")
    except (urllib.error.URLError, OSError) as e:
        report("FAIL", "裸域跳轉", f"請求失敗：{e}")
        return
    if status in (301, 308) and location.startswith(BASE):
        report("OK", "裸域跳轉", f"HTTP {status} -> {location}")
    else:
        report("WARN", "裸域跳轉", f"HTTP {status} Location={location or '無'}，請複查")


def check_headers():
    try:
        with fetch(BASE + "/", method="HEAD") as resp:
            hsts = resp.headers.get("Strict-Transport-Security")
        if hsts:
            report("OK", "安全標頭 HSTS", hsts)
        else:
            report("WARN", "安全標頭 HSTS",
                   "GitHub Pages 不支援自訂安全標頭（HSTS/CSP 需前置 CDN 才能啟用），維持觀察")
    except (urllib.error.URLError, OSError) as e:
        report("FAIL", "安全標頭", f"無法檢查：{e}")


def main():
    print(f"=== DIA 官網巡查 {datetime.datetime.now().isoformat(timespec='seconds')} ===")
    check_dns()
    check_tls()
    check_apex_redirect()
    check_pages()
    check_content()
    check_headers()
    fails = sum(1 for r in results if r[0] == "FAIL")
    warns = sum(1 for r in results if r[0] == "WARN")
    print(f"=== 結果：{len(results)} 項檢查，FAIL {fails}，WARN {warns} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
