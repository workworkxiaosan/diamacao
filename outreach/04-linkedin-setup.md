# LinkedIn 機構主頁部署包

> 限制：建立 LinkedIn 機構主頁必須用負責人的個人帳號登入操作（LinkedIn 不開放 API 建頁）。以下為全部欄位的現成內容，登入後約 5 分鐘可建頁；建頁後把 URL 填回 content.json 即完成 sameAs 閉環。

## A. 建頁資料（建立頁面時逐欄複製）

- 入口：https://www.linkedin.com/company/setup/new/ （需先登入個人帳號）
- Page name：**Macao Digital Innovation Association (DIA)**
- Website：https://www.diamacao.com
- Industry：**Non-profit Organizations**
- Organization type：**Nonprofit**
- Logo：用 `assets/img/logo.png`（透明底 PNG）
- Cover image：用 `assets/img/og-cover.jpg`（1200×630）
- Tagline（120 字內）：
  `Digital leadership · Going global together · Setting sail from Macao`

### About（Description，直接複製）
```
The Macao Digital Innovation Association (DIA) is a non-profit association based in Macao SAR, China. We promote digital innovation and help enterprises go global through the China–Portuguese-speaking Countries platform, serving Portuguese-, Spanish- and French-speaking markets and Belt and Road partner countries.

Our Go-Global Support Program covers entity incorporation, compliance, cross-border settlement, market matchmaking, talent training, product certification and intellectual property support.

Official website (6 languages): https://www.diamacao.com
Contact: info@diamacao.com
```

- 語言補充：LinkedIn 允許為主頁添加多語言版本，可加葡語（Associação de Inovação Digital de Macau）與西語（Asociación de Innovación Digital de Macao）名稱與簡介。

## B. 建頁後的回填操作（全自動閉環）

1. 複製機構主頁 URL（形如 `https://www.linkedin.com/company/xxxx`）。
2. 在 `content.json` 的 `social.linkedin` 填入該 URL（目前為 `"#"`）。
3. 執行 `python3 build.py` → commit → push。
4. 自動生效：
   - 全站 6 語言首頁的 Organization JSON-LD 自動帶上 `sameAs`（Google 知識圖譜實體對齊；已實測：填入 URL 即輸出，為 `#` 時不輸出）。
   - 頁頭/頁尾/聯繫頁的 LinkedIn 圖標自動指向真實主頁。
   - Facebook/Instagram 日後開通同理填入 `social.facebook` / `social.instagram`。

## 完成記錄
- LinkedIn 主頁 URL：（待填）
