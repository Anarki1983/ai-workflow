> 正體中文翻譯版，內容以 [`README.md`](./README.md)（英文，本專案 `CLAUDE.md` 訂定的標準版本）為準；兩份不同步時，以英文版為主。

# ai-workflow

這個團隊共用的執行階段工程紀律，給 Claude Code + superpowers 用——會自動同步進每個協作者的全域 Claude Code 配置，不只是一份要你手動複製進各個專案的骨架。

## 這個 repo 在解決什麼問題

個人的 `~/.claude/CLAUDE.md`（每個開發者、每台機器各一份）可以放一條**決策階段**規則——某個開發者遇到新需求、新功能、行為變更時，動手改代碼之前想怎麼處理。這條規則實際內容是什麼、靠哪些 skill 或流程,因人而異;這個 repo 沒有立場預設每個協作者都裝了同一套。那條規則解決的是「要不要做、怎麼做」——但它是個人的，沒辦法原封不動變成團隊共用規則，不然會蓋掉每個人各自的偏好。

真正缺的是**團隊層級的執行階段**：決定做了、真的要動手（不管是人還是 AI）改 repo 時，一個改動該套哪個 superpowers skill（TDD？systematic-debugging？frontend-design？）、該叫哪個專職 agent、審查要多深、誰有權合併——這件事需要對每個協作者、每個專案都**一致**，不然「團隊共用標準」這件事本身就沒意義。

`skills/change-type-routing/` 和 `skills/team-review-pipeline/` 這兩個 skill 就是把這件事寫成方法。`skills/change-type-routing/` 是一套方法——不是抄好的表——用來幫專案盤點出「哪種改動該用哪個機制（skill/agent/check）」。`skills/team-review-pipeline/` 管的是同一個執行階段的另一個軸：不是「哪個機制處理這個改動」，而是在 AI 主導大部分實作的團隊裡，「審查要多深、誰有權合併」。它組合既有的 superpowers skill，不另外發明機制：superpowers:test-driven-development 和 superpowers:verification-before-completion 決定「測試通過」算不算數；superpowers:using-git-worktrees 隔離併發中的工作；superpowers:writing-plans／executing-plans 把大改動拆成一個 task 一個 PR；superpowers:finishing-a-development-branch 負責合併後的清理。它的 review-depth 例外清單、多模型審查觸發條件、3 輪 review-loop 上限，都應該落地成專案自己 change-type-routing 表裡的橫切規則。

**目前進度**——review-depth 例外清單涵蓋 authN/authZ、金流、資料遷移、密鑰／基礎設施設定、未鎖定版本的新依賴，以及（自我指涉地）改動專案自己的 skill 檔案或 `CLAUDE.md`；針對正式環境事故有一條 break-glass 路徑，但永遠不能跳過例外清單審查與人類合併這道閘，只能跳過隔離跟可選的人工測試審查。`skills/team-review-pipeline/pressure-scenarios.md` 現在有 7 個情境，全部都各自拿 fresh subagent 實際跑過一次，通過。

## 同步機制怎麼運作

每位協作者跑這一次：

```
bash scripts/install.sh
```

這個一次性步驟會：備份 `~/.claude/settings.json`、把它的 `SessionStart` hook 指向 `scripts/sync.sh`、在協作者個人的 `~/.claude/CLAUDE.md` 加一行 `@<這個repo的路徑>/CLAUDE.md`（那份檔案裡其他內容完全不動）。從此之後，**每次 session 啟動**都會重跑 `scripts/sync.sh`，它會：

1. `git pull` 這個 repo。
2. 把 `skills/*`、`agents/*` 底下每個子目錄 symlink 進協作者全域的 `~/.claude/skills/`、`~/.claude/agents/`——如果該路徑已經有東西、而且不是這個 repo 建的 symlink，就跳過並警告，絕不覆蓋。
3. 對照 `scripts/third-party-plugins.json`（見下）核對第三方 plugin——缺的就裝，版本對不上就警告，絕不強制改版本。

這讓已經裝好的協作者能自我修復：repo 加了新 skill，大家下次開 session 就會自動拿到，不用手動重新同步。唯一沒辦法解決的，是全新協作者的第一次安裝——沒人能強制他跑 `scripts/install.sh`，因為在他跑之前什麼機制都還沒生效；這是一個文件化的 onboarding 步驟，不是機制。

**還留在專案層級、沒有全域化的部分**：`change-type-routing` 產出的**那張表**——某個專案針對自己目錄結構產出的實際路由表——還是留在那個專案自己的 `CLAUDE.md` 裡，因為那份內容本來就是專案專屬的。全域化的只有「產出那張表的方法（skill 本身）」。

**信任模型，講清楚**：`scripts/sync.sh`、`scripts/install.sh` 是會在每個協作者機器上無人看管自動執行的程式碼，而且透過 `git pull` 自我更新。誰能合併 `scripts/` 的改動，誰就能在每個協作者的機器上、下次 session 執行任意程式碼。這正是為什麼這個 repo 自己的 `CLAUDE.md` 把 `scripts/*` 的變更風險列得比一般 skill 內容更高——見它的橫切規則。

## 保持第三方 plugin 版本一致

`scripts/third-party-plugins.json` 釘住這個團隊談好的每個外部 plugin（superpowers、mattpocock-skills 等）的確切版本。`scripts/sync.sh` 每次 session 都會檢查：完全沒裝就自動裝；裝了但版本不對就警告（落後或超前都會報），不強制改版本——因為 `claude plugin` 這支 CLI 沒有能強制裝回指定版本的參數。要改動釘住的版本，是對這份檔案的一次刻意、需要審查的編輯，不是例行更新——審查標準見 `CLAUDE.md` 的分類表。

## 給這個團隊以外的專案或人

如果你不在這個團隊的同步設定裡——單純想評估這個 repo，或想改給別的團隊用——底層的 skill 手動複製一樣能用：把 `skills/change-type-routing/SKILL.md`（連同 `pressure-scenarios.md`）複製進某個專案的 `.claude/skills/change-type-routing/`，在那裡叫這個 skill，跟著它的盤點步驟產出那個專案自己的路由表（參考 `examples/spelldungeon.md` 的實例）。這樣複製出去的檔案不會自動跟這個 repo 同步，本來就預期會分岔成那個專案自己的具體版本。

## 這個 repo 自己的規範

這個 repo 對自己套用了同一套方法：根目錄的 `CLAUDE.md` 就是這個 repo 自己的 change-type-routing 表（skill 內容、agent 定義、pressure-scenario 檔案、worked examples、同步／安裝腳本、頂層文件），外加橫切規則把治理檔案跟同步腳本的改動列為這裡風險最高的兩類——腳本又比治理檔案更高，因為腳本會無人看管地執行，文字只會被讀。
