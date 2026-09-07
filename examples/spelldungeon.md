# 範例：SpellDungeon 套用出來的路由表

這是 `skills/change-type-routing/` 的方法在一個實際專案（SpellDungeon，
一個沒有框架、沒有後端的靜態網站文字遊戲）上套用出來的結果，收在
該專案的 `.claude/skills/spelldungeon-workflow/SKILL.md`，`CLAUDE.md`
只留一句指過去。拿來當「產出應該長什麼樣子」的參考，不是拿來照抄——
目錄結構跟既有工具鏈換一個專案就不一樣。

## 盤點出的分類

SpellDungeon 的目錄邊界剛好對應規則核心／設定值／規格文件／呈現層／
美術資產／規則文件本身，共 6 類，加 1 條橫切規則：

| 改動類型 | 動到的目錄 | 對應機制 |
|---|---|---|
| 規格書改動 | `doc/gdd2/*.md` | domain-modeling skill |
| 數值改動 | `config/*.json` | 專案自己的平衡方法論（見下） |
| 規則核心改動 | `src/*.mjs` | superpowers:test-driven-development ＋ `npm run check:rules` |
| 呈現／編排改動 | `web/*.mjs` | `npm run check:layout`／`check:flow`，必要時 frontend-design |
| 美術資產改動 | `art-src/`、`assets/art` | 既有美術管線（`npm run art`），不套 superpowers |
| 規則文件改動 | `CLAUDE.md`、`docs/adr` | domain-modeling／ADR 格式 |
| （橫切）任何 bug | 不分目錄 | superpowers:systematic-debugging，優先於其他列 |

## 既有專職 agent 過期的那個岔路

盤點時發現這個專案有一個 `.claude/agents/balance-analyst.md`，但它是重建前
舊版遊戲的產物：裡面寫死的路徑指向已經不存在的舊規格夾與舊後端，
具體的不變量數字也是舊版設計的產物。這正是 `change-type-routing`
skill 裡提到「既有 agent 要不要吸收」那個分岔——問了專案擁有者，
選的是「抽出耐用的方法論（模擬方法論、玩家模型分類、交付格式），
具體數字全部捨棄改指向現在的規格書與設定檔，agent 檔案本體刪除，
之後改用通用 agent 帶著這段方法論做分析」。這代表這個專案現在
沒有 `balance-analyst` 這個可以直接派工的專職 subagent type 了——
這是明確權衡過、可以接受的取捨，不是意外流失的功能。
