# ai-workflow

個人的「執行階段路由」方法骨架，給任何以 Claude Code + superpowers 為主的專案用。

## 這個 repo 在解決什麼問題

家目錄 `~/.claude/CLAUDE.md` 已經有一條**決策階段**規則：遇到新需求、新功能、
行為變更時，先在 brainstorming／grill-with-docs／plan mode 三者間選一個，
再往下走。那條規則解決的是「要不要做、怎麼做」。

它沒解決的是**執行階段**：決定完、真的要動手改 repo 時，一個改動到底該套
哪個 superpowers skill（TDD？systematic-debugging？frontend-design？）、
該叫哪個專職 agent、改完要跑哪支 check 腳本——這件事因專案而異，
放在家目錄規則裡太空泛，每次臨場想又容易漏掉或不一致。

`skills/change-type-routing/` 就是補這一塊的方法：不是一張抄好的表，
而是「怎麼幫任意專案盤點出屬於它自己的那張表」。

## 怎麼用在新專案

1. 把 `skills/change-type-routing/SKILL.md` 複製進新專案的 `.claude/skills/change-type-routing/`
   （Claude Code 只認得專案層級或使用者層級 `~/.claude/skills/` 裡的 skill，
   放在這個 repo 裡本身不會被任何 session 自動載入）。
2. 在那個專案裡叫這個 skill，跟著它的盤點步驟產出這個專案自己的路由表，
   通常直接寫進該專案的 `CLAUDE.md`，或另外開一個專案專屬的路由 skill
   （做法可以參考 `examples/spelldungeon.md`——那是 SpellDungeon 專案套用出來的實例）。
3. 專案有既有的專職 agent（`.claude/agents/*.md`）時，先確認它的內容是不是還對得上
   現在的 repo 結構——不要把過期的檔案路徑或已作廢的設計原樣搬進新的路由表。

## 這個 repo 本身怎麼保持新鮮

`~/.claude/settings.json` 有一個全域 `SessionStart` hook，每次開 Claude Code
session 前會 `git pull` 這個 repo（本機路徑 `~/projects/ai-workflow`）。
失敗（離線、還沒設 remote）只會印一行警告，不會擋住 session 啟動——
這是錦上添花的新鮮度機制，不是關鍵路徑。

複製到某個專案裡的 skill 檔案**不會**跟著這個 repo 自動同步——那是特定專案
已經套用出來的具體版本，本來就會偏離通用骨架，需要更新時手動比對再複製。
