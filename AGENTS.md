# DIA 官網（www.diamacao.com）

澳門數字創新協會官方網站（Macao Digital Innovation Association / Associação de Inovação Digital de Macau），靜態多語言站（繁中/簡中/en/pt），托管於 GitHub Pages，域名 DNS 在 Hostinger。架構自 MFTEDA 官網（mfteda.org）遷移，品牌藍 #257ADB 科技風（參考 GTIA）。

## 結構

- `content.json` — 全部網站內容的唯一母本（4 語言、新聞、出海政策、架構成員、夥伴鏈接）。**更新內容只改這裡**。
- `build.py` — 讀 `content.json` 生成靜態頁面到 `dist/`（含 `dist/CNAME` = www.diamacao.com）。語言目錄：繁中在根目錄，其他在 `zh-CN/`、`en/`、`pt/`。
- `make_assets.py` — 由 `assets/img/src-logo.png`（新版純藍線稿透明底 LOGO）生成 logo 變體/favicon/hero-bg/og-cover（一次性，換 LOGO 才需重跑）。
- `make_hero_video.py` — 生成首頁 hero 10s 無縫循環動態背景（白底淺色版科幻電路：走線+流動光脈衝+漂移粒子+掃描帶，T=10s 周期化保證首尾銜接）：輸出 `hero-loop.mp4`（H.264）/`hero-loop.webm`（VP9），並把首幀覆蓋 `hero-bg.webp` 作 poster/降級圖。**注意執行順序：先 make_assets.py 後 make_hero_video.py**（後者覆蓋 hero-bg.webp）；依賴 ffmpeg。hero 為白底黑字（`.hero` color 深藍黑，`.hero-video` z-index 0，`::before` 白紗罩 z-index 1，內容 z-index 2；`.hero .btn-glass` 已適配淺底；main.js 尊重 prefers-reduced-motion 暫停播放）。
- `assets/` — 源頭樣式/腳本/圖片，`build.py` 會拷貝進 `dist/`。`logo-mark.png` 為芯片圖標（頁頭/hero），`logo.png` 為含中英文名全版，`og-cover.jpg` 為社交分享圖（1200×630，深藍底，由 make_assets.py 生成）；成員頭像在 `assets/img/members/{president,chair}.webp`（480×480 正方形，圓形裁切顯示 `.member-photo`）。
- `dist/` — 生成物，**不要手改**，已被 .gitignore 忽略。自動生成 `robots.txt`、`sitemap.xml`（含 4 語言 hreflang）、`404.html`。

## 更新流程

1. 改 `content.json`：
   - 加新聞 = 在 `news` 數組加一條（`date/slug/category/title/excerpt/source/body` 4 語言，`source.url` 為原文媒體鏈接），詳情頁 `news/{slug}.html` 自動生成，列表與首頁「最新動態」按 date 降序自動更新。
   - 加出海政策 = 在 `policies` 數組加一條（`date/region/issuer/title/summary/url` 4 語言），region 四選一：`national`（國家政策）、`gba`（大灣區與橫琴）、`macao`（澳門平台）、`global`（重點海外市場）。
   - 架構成員 = `members` 數組（`initial/name/role/bio` 4 語言，`initial` 為頭像單字；可選 `photo` 指向 `assets/img/members/*.webp`，有照片則顯示圓形真人頭像）；組織機關三會描述在 `org` 數組（源自律章程，勿隨意改動）。成員頁無「名單陸續公佈」備註（2026-10-16 按用戶指示刪除，勿加回）。協會宗旨（about.purpose，2026-10-16 更新）：「秉持愛國愛澳精神，推動數字經濟發展與多元產業融合；『聚人才、促轉化、育新智、聯世界』；主動服務國家『國際循環』發展大局，助力中華民族偉大復興。」
   - 合作夥伴 = `partners` 數組；LOGO 放 `assets/img/partners/partner{N}.webp`（N=順序號，無 LOGO 自動只顯示文字卡）。
2. `python3 build.py`。
3. `git add -A && git commit -m "..." && git push`。
4. GitHub Actions 自動構建部署（`.github/workflows/deploy.yml`），約 1 分鐘後線上生效。

## 關鍵事實

- 頁面共 8 個（`PAGES`）：index/about/members/news/policy/services/partners/contact。無 research/projects/publications/insights（與 MFTEDA 不同）；社評類稿件可作 `news` 條目（category 如「社評」）。
- `services` 頁（2026-10-15 新增，出海護航）：內容在 content.json 頂層 `escort` 對象（s1 行業數據帶 / s2 澳門前中後台 / s3 出海之難流程鏈+痛點卡 / s4 一站式護航三大服務+六大支撐+海易通達支持信息），全部 4 語言；樣式 `.escort-*` 在 style.css 尾部；首頁有宣傳帶 `.escort-band`（i18n home.escort*）。支持單位聯繫方式（韓女士電話、nexmatrixs.com）寫在 `escort.s4.support`。
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
- 關聯站點：MFTEDA（mfteda.org）互列合作夥伴。萬裡金騰集團、澳門橋霍頓原列合作夥伴，2026-10-15 按用戶指示從 DIA 官網移除（僅 DIA 站，MFTEDA 站不動）。
- 合作夥伴 10 家（2026-10-15 更新）：中西創新學院（即「澳門中西學院」法定名，mmc.edu.mo，校徽 partner1.webp 複用自 MFTEDA partner11）、MFTEDA（partner2.webp）、南航科技（廣東橫琴）（無獨立官網 href=#）、海易通達（nexmatrixs.com）、Bonjour Brand、澳門直播協會、科伊思（杭州）人工智能（用戶原寫「科伊斯」，工商登記為「科伊思」，coios-ai.com）、Beroni Group Limited（貝羅尼集團，beronigroup.com）、中盛國際實業（zhongshengindustry.com；官網稱 1999 年成立但香港註冊處顯示同名公司 2023 年註冊，存疑待對方確認）、中光集團（長春）（教育投資集團，無官網 href=#）。
- LOGO（2026-10-15 換新版）：純藍線稿透明底（白色全部不保留），源圖固化於 `assets/img/src-logo.png`；make_assets.py 的 trim/拆分掃描均按 alpha 通道，cutout() 僅適用舊版白底圖（新圖勿調用，會侵蝕半透明線稿）；換 LOGO 時替換 src-logo.png 重跑 make_assets.py 即可（生成 logo.png/logo-mark.png/favicon/hero-bg/og-cover）。
