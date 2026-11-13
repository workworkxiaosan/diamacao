# 國際互鏈外聯部署包

> 原則：友鏈必須對方同意，**在對方確認前不得將其列入官網合作夥伴頁**（避免不實陳述）。以下為目標清單與四語言外聯信模板。

## A. 目標機構清單（按優先級）

### 澳門高校（地緣優勢，最易落地）
| 機構 | 官網 | 切入點 |
|---|---|---|
| 澳門大學 | https://www.um.edu.mo | 科技學院／社會科學學院，產學研合作 |
| 澳門科技大學 | https://www.must.edu.mo | 可持續發展研究所、數字經濟研究 |
| 澳門理工大學 | https://www.mpu.edu.mo | 中葡平台、語言與翻譯合作 |
| 聖若瑟大學 | https://www.usj.edu.mo | 葡語國家網絡、商學院 |

### 葡語國家
| 機構 | 官網 | 切入點 |
|---|---|---|
| 科英布拉大學（葡萄牙） | https://www.uc.pt | 歷史名校，中葡研究 |
| 里斯本大學（葡萄牙） | https://www.ulisboa.pt | 經濟管理學院 ISEG |
| 葡萄牙天主教大學 | https://www.ucp.pt | 商學院國際網絡 |
| 聖保羅大學（巴西） | https://www5.usp.br | 拉美最大高校，中巴科技合作 |

### 西語國家／一帶一路
| 機構 | 官網 | 切入點 |
|---|---|---|
| 薩拉曼卡大學（西班牙） | https://www.usal.es | 西語世界學術樞紐 |
| 對外經濟貿易大學（北京） | https://www.uibe.edu.cn | 出海研究、已有京澳合作基礎 |

## B. 外聯信模板（四語言，填 [對方機構名] 即可發送）

主旨建議（en）：Partnership and reciprocal link proposal — Macao Digital Innovation Association (DIA)

### English
```
Dear [Institution] team,

I am writing on behalf of the Macao Digital Innovation Association (DIA), a non-profit association in Macao SAR (https://www.diamacao.com). We help enterprises go global through the China–Portuguese-speaking Countries platform, with a focus on Portuguese-, Spanish- and French-speaking markets.

We would like to propose a reciprocal link between our websites (partners/resources pages) and to explore cooperation on research and enterprise matchmaking. We would be glad to feature [Institution] on our partners page upon your confirmation.

Best regards,
Macao Digital Innovation Association
info@diamacao.com
```

### Português
```
Exmos. Senhores da [Instituição],

Escrevemos em nome da Associação de Inovação Digital de Macau (DIA), associação sem fins lucrativos sediada em Macau (https://www.diamacao.com), que apoia a internacionalização das empresas através da plataforma sino-lusófona.

Gostaríamos de propor uma ligação recíproca entre os nossos sítios web (páginas de parceiros) e explorar cooperação em investigação e emparelhamento empresarial. Teremos todo o gosto em apresentar a [Instituição] na nossa página de parceiros após a vossa confirmação.

Com os melhores cumprimentos,
Associação de Inovação Digital de Macau
info@diamacao.com
```

### Español
```
Estimado equipo de [Institución]:

Les escribimos en nombre de la Asociación de Innovación Digital de Macao (DIA), asociación sin ánimo de lucro de Macao (https://www.diamacao.com), dedicada a la internacionalización de empresas a través de la plataforma sino-lusófona.

Nos gustaría proponer un enlace recíproco entre nuestros sitios web (páginas de socios) y explorar la cooperación en investigación y contactos empresariales. Estaremos encantados de presentar a [Institución] en nuestra página de socios una vez recibida su confirmación.

Atentamente,
Asociación de Innovación Digital de Macao
info@diamacao.com
```

### Français
```
Madame, Monsieur,

Au nom de l'Association d'Innovation Numérique de Macao (DIA), association à but non lucratif basée à Macao (https://www.diamacao.com), qui accompagne l'internationalisation des entreprises via la plateforme sino-lusophone.

Nous vous proposons un échange de liens entre nos sites (pages partenaires) et une réflexion commune sur la recherche et la mise en relation d'entreprises. Nous serions heureux de présenter [Institution] sur notre page partenaires dès votre confirmation.

Cordialement,
Association d'Innovation Numérique de Macao
info@diamacao.com
```

## C. 對方同意後的落地操作
1. 在 content.json 的 partners 數組新增該機構（6 語言名稱/簡介、href 官網），LOGO 放 assets/img/partners/partner{N}.webp。
2. python3 build.py → commit → push（詳見 AGENTS.md 更新流程）。
3. 回覆對方我方頁面鏈接，請其在「合作機構」頁掛出 https://www.diamacao.com 。

## 完成記錄
- 已聯繫／已同意機構：（待填）
