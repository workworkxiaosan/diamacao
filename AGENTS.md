# DIA 官網（www.diamacao.com）

澳門數字創新協會官方網站（Macao Digital Innovation Association / Associação de Inovação Digital de Macau），靜態多語言站（繁中/簡中/en/pt），托管於 GitHub Pages，域名 DNS 在 Hostinger。架構自 MFTEDA 官網（mfteda.org）遷移，品牌藍 #257ADB 科技風（參考 GTIA）。

## 結構

- `content.json` — 全部網站內容的唯一母本（4 語言、新聞、出海政策、架構成員、夥伴鏈接）。**更新內容只改這裡**。
- `build.py` — 讀 `content.json` 生成靜態頁面到 `dist/`（含 `dist/CNAME` = www.diamacao.com）。語言目錄：繁中在根目錄，其他在 `zh-CN/`、`en/`、`pt/`。
- `make_assets.py` — 由原始 LOGO 生成 logo 變體/favicon/hero-bg/og-cover（一次性，換 LOGO 才需重跑；LOGO 源圖路徑寫在腳本頂部 SRC）。
- `assets/` — 源頭樣式/腳本/圖片，`build.py` 會拷貝進 `dist/`。`logo-mark.png` 為芯片圖標（頁頭/hero），`logo.png` 為含中英文名全版，`hero-bg.webp` 為深藍電路紋背景，`og-cover.jpg` 為社交分享圖（1200×630）。
- `dist/` — 生成物，**不要手改**，已被 .gitignore 忽略。自動生成 `robots.txt`、`sitemap.xml`（含 4 語言 hreflang）、`404.html`。

## 更新流程

1. 改 `content.json`：
   - 加新聞 = 在 `news` 數組加一條（`date/slug/category/title/excerpt/source/body` 4 語言，`source.url` 為原文媒體鏈接），詳情頁 `news/{slug}.html` 自動生成，列表與首頁「最新動態」按 date 降序自動更新。
   - 加出海政策 = 在 `policies` 數組加一條（`date/region/issuer/title/summary/url` 4 語言），region 四選一：`national`（國家政策）、`gba`（大灣區與橫琴）、`macao`（澳門平台）、`global`（重點海外市場）。
   - 架構成員 = `members` 數組（`initial/name/role/bio` 4 語言，`initial` 為頭像單字）；組織機關三會描述在 `org` 數組（源自律章程，勿隨意改動）。
   - 合作夥伴 = `partners` 數組；LOGO 放 `assets/img/partners/partner{N}.webp`（N=順序號，無 LOGO 自動只顯示文字卡）。
2. `python3 build.py`。
3. `git add -A && git commit -m "..." && git push`。
4. GitHub Actions 自動構建部署（`.github/workflows/deploy.yml`），約 1 分鐘後線上生效。

## 關鍵事實

- 頁面共 7 個（`PAGES`）：index/about/members/news/policy/partners/contact。無 research/projects/publications/insights（與 MFTEDA 不同）；社評類稿件可作 `news` 條目（category 如「社評」）。
- 協會事實（源自《澳門特區公報》2026-02-25 第8期第二組）：2026-02-06 經認證文書設立（私人公證員周成俊，存檔編號 3/2026）；葡文名 Associação de Inovação Digital de Macau，英文名 Macao Digital Innovation Association；會址澳門何老桂巷5號；非牟利團體；組織機關 = 會員大會/理事會/監事會（任期三年）。**成立日期與註冊/刊憲信息僅存檔於此內部文檔，官網一律不顯示**（用戶 2026-10-15 指示：content.json 不得出現成立日期、公報/公證相關內容，每週 cron 更新也不得收錄此類新聞）。
- 已核實成員：會長黃家倫（澳門立法會議員、澳門直播協會創會會長）、理事長楊誠（澳門財經科技與教育發展學會會長、國際研學旅遊產業發展協會（澳門）會長、澳門博士智庫副理事長）。其他理監事成員名單待公佈後補入 `members`。
- 新聞目前 3 條（2026-04-15 京澳通洽會、2026-04-15 海淀區代表團訪招商局、2026-05-28 巴黎簽約），全部附媒體原文鏈接；政策 10 條（國家3/大灣區2/澳門3/海外市場2），URL 均已核實。**2026 年 6–10 月暫無協會公開報道**，有內部通稿時補入。首頁數據帶首格為「6 重點工作領域」（對應 focus_cards 六項，勿改回成立年份）。
- 每頁自動帶 canonical / Open Graph / Twitter Card 標籤，首頁帶 Organization JSON-LD。`site_url` = https://www.diamacao.com（換域名時改它 + build.py 的 CNAME/robots）。
- 域名 `diamacao.com`：A 記錄指向 GitHub Pages（185.199.108.153/109.153/110.153/111.153），`www` CNAME → workworkxiaosan.github.io；DNS 在 Hostinger（API 管理，域名 2029-10-14 到期）。
- GitHub 倉庫：`workworkxiaosan/diamacao`。
- 默認語言繁中在根路徑（如 `/about.html`）。
- 聯繫郵箱 `info@diamacao.com` 為佔位（Hostinger 郵局開通後可直接使用；社交鏈接 FB/LinkedIn/IG 暫為 `#`，待協會官方賬號開通後填入 `social`）。
- 聯繫表單為前端演示，未接後端；如需真正收集留言可接 Formspree 等服務。
- 繁簡校對規範：繁體用港澳寫法（「平台/了解/群體」的 台/了/群 均為正字，勿改作 臺/瞭/羣）；機構名按語言版本書寫（zh-CN 頁 og:site_name 用簡體「澳门数字创新协会」）。
- 排序：news 與 policies 均按 date 降序，首頁各取前 3。
- 關聯站點：萬裡金騰集團（wljtgroup.com，同架構）、MFTEDA（mfteda.org）、橋霍頓（bridgeholdengroup.com）已互列合作夥伴。
