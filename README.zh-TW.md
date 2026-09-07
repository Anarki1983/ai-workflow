> 正體中文翻譯版，內容以 [`README.md`](./README.md)（英文，本專案 `CLAUDE.md` 訂定的標準版本）為準；兩份不同步時，以英文版為主。

# ai-workflow

個人的「執行階段路由」方法骨架，給任何以 Claude Code + superpowers 為主的專案用。

## 這個 repo 在解決什麼問題

家目錄的 `~/.claude/CLAUDE.md` 已經有一條**決策階段**規則：遇到新需求、新功能、行為變更時，先在 brainstorming／grill-with-docs／plan mode 三者間選一個，再往下走。那條規則解決的是「要不要做、怎麼做」。

它沒解決的是**執行階段**：決定完、真的要動手改 repo 時，一個改動到底該套哪個 superpowers skill（TDD？systematic-debugging？frontend-design？）、該叫哪個專職 agent、改完要跑哪支 check 腳本——這件事因專案而異，放在家目錄規則裡太空泛，每次臨場想又容易漏掉或不一致。

`skills/change-type-routing/` 就是補這一塊的方法：不是一張抄好的表，而是「怎麼幫任意專案盤點出屬於它自己的那張表」。

第二個 skill `skills/team-review-pipeline/` 管的是同一個執行階段的另一個軸：不是「哪個機制處理這個改動」，而是在 AI 主導大部分實作的團隊裡，「審查要多深、誰有權合併」。它沒有另外發明機制，而是把既有的 superpowers skill 組合成一條 pipeline：superpowers:test-driven-development 和 superpowers:verification-before-completion 決定「測試通過」算不算數（下面「只審查測試」的預設，只有在測試是 test-first 寫的、而且有真的跑過的驗證輸出時才成立，不是靠宣稱）；superpowers:using-git-worktrees 隔離併發中的工作；superpowers:writing-plans／executing-plans 把大改動拆成一個 task 一個 PR；superpowers:finishing-a-development-branch 負責合併後的清理。它的 review-depth 例外清單、多模型審查觸發條件、3 輪 review-loop 上限，都應該落地成專案自己 change-type-routing 表裡的橫切規則，而不是另開一份文件維護。

**目前進度**——review-depth 例外清單涵蓋 authN/authZ、金流、資料遷移、密鑰／基礎設施設定、未鎖定版本的新依賴，以及（自我指涉地）改動專案自己的 skill 檔案或 `CLAUDE.md`；針對正式環境事故有一條 break-glass 路徑，但永遠不能跳過例外清單審查與人類合併這道閘，只能跳過隔離跟可選的人工測試審查。`skills/team-review-pipeline/pressure-scenarios.md` 現在有 6 個情境——前 3 個（deadline 壓力下的例外清單變更、卡住的審查迴圈、把 AI approve 誤當合併授權）都各自拿 fresh subagent 實際跑過一次，通過；因應 test-first、驗證證據、事故壓力這三條新規則新增的 3 個情境，目前寫好了但**還沒實際跑過**。

## 怎麼用在新專案

1. 把 `skills/change-type-routing/SKILL.md`（連同 `pressure-scenarios.md`）複製進新專案的 `.claude/skills/change-type-routing/`（Claude Code 只認得專案層級或使用者層級 `~/.claude/skills/` 裡的 skill，放在這個 repo 裡本身不會被任何 session 自動載入）。
2. 在那個專案裡叫這個 skill，跟著它的盤點步驟產出這個專案自己的路由表，通常直接寫進該專案的 `CLAUDE.md`，或另外開一個專案專屬的路由 skill（做法可以參考 `examples/spelldungeon.md`——那是 SpellDungeon 專案套用出來的實例）。
3. 專案有既有的專職 agent（`.claude/agents/*.md`）時，先確認它的內容是不是還對得上現在的 repo 結構——不要把過期的檔案路徑或已作廢的設計原樣搬進新的路由表。

## 這個 repo 自己的規範

這個 repo 對自己套用了同一套方法：根目錄的 `CLAUDE.md` 就是這個 repo 自己的 change-type-routing 表（skill 內容、pressure-scenario 檔案、worked examples、頂層文件），外加一條橫切規則——任何動到 `SKILL.md` 或 `CLAUDE.md` 本身的改動，在這裡是風險最高的一類，因為這些檔案被複製出去之後就會變成別的專案的治理規則。

## 這個 repo 本身怎麼保持新鮮

`~/.claude/settings.json` 有一個全域 `SessionStart` hook，每次開 Claude Code session 前會 `git pull` 這個 repo（本機路徑 `~/projects/ai-workflow`）。失敗（離線、還沒設 remote）只會印一行警告，不會擋住 session 啟動——這是錦上添花的新鮮度機制，不是關鍵路徑。

複製到某個專案裡的 skill 檔案**不會**跟著這個 repo 自動同步——那是特定專案已經套用出來的具體版本，本來就會偏離通用骨架，需要更新時手動比對再複製。
