#!/usr/bin/env bash
# Rejects AI-tool watermarks in commit messages, staged changes, PR ranges and PR text.
#
# Usage:
#   bash scripts/check-ai-watermark.sh --msg <commit-msg-file>   # used by .githooks/commit-msg
#   bash scripts/check-ai-watermark.sh --staged                  # used by .githooks/pre-commit
#   bash scripts/check-ai-watermark.sh --range origin/develop..HEAD
#   bash scripts/check-ai-watermark.sh --text "<PR title and body>"
set -uo pipefail

# Text that must never appear in commits, code or PRs (case-insensitive, extended regex)
CONTENT_PATTERN='co-authored-by:.*(claude|anthropic|copilot|chatgpt|openai|gemini|cursor|codeium|windsurf|aider|devin)|generated (with|by) .*(claude|chatgpt|copilot|cursor|gemini|codeium|windsurf)|generated (with|by) (an )?ai([^a-z]|$)|noreply@anthropic\.com|claude\.com/claude-code|claude\.ai/code|🤖 generated|as an ai (language )?model|here.s the (updated|modified|complete|full) (code|file)|rest of (the )?(code|file) (remains )?unchanged'

# AI tool folders / config files that must never be committed
PATH_PATTERN='(^|/)(\.claude|\.cursor|\.windsurf|\.continue|\.codeium|\.copilot|\.gemini|\.aider[^/]*)(/|$)|(^|/)(CLAUDE\.md|CLAUDE\.local\.md|GEMINI\.md|AGENTS\.md|\.cursorrules|\.windsurfrules|copilot-instructions\.md)$'

# Files that legitimately contain the patterns above (the rules themselves)
EXCLUDES=(
  ':(exclude)scripts/check-ai-watermark.sh'
  ':(exclude)IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md'
  ':(exclude)IMPLEMENTATION_PLANS/AI_EXECUTION_INSTRUCTIONS.md'
  ':(exclude).gitignore'
)

RED=$'\033[31m'; GREEN=$'\033[32m'; RESET=$'\033[0m'
found=0

report() {
  echo "${RED}✖ AI watermark found ($1):${RESET}"
  sed 's/^/    /'
  found=1
}

# Checks take the text as $2 (not stdin) so `found` is set in this shell, not in a pipeline subshell.
check_text() {  # $1 = label, $2 = text
  local hits
  hits=$(grep -inE "$CONTENT_PATTERN" <<<"$2" || true)
  if [[ -n "$hits" ]]; then report "$1" <<<"$hits"; fi
}

check_paths() {  # $1 = label, $2 = file list
  local hits
  hits=$(grep -E "$PATH_PATTERN" <<<"$2" || true)
  if [[ -n "$hits" ]]; then report "$1 — AI tool files must not be committed" <<<"$hits"; fi
}

added_lines() { grep -E '^\+' | grep -vE '^\+\+\+ ' || true; }

case "${1:-}" in
  --msg)
    # ignore comment lines git adds to the message template
    check_text "commit message" "$(grep -vE '^#' "$2")"
    ;;
  --staged)
    check_paths "staged files" "$(git diff --cached --name-only --diff-filter=ACMR)"
    check_text "staged changes" "$(git diff --cached -U0 --no-color -- . "${EXCLUDES[@]}" | added_lines)"
    ;;
  --range)
    range="$2"
    if [[ "$range" == *...* ]]; then log_range="${range/.../..}"; diff_range="$range"
    else log_range="$range"; diff_range="${range/../...}"; fi
    check_text "commit messages in $log_range" "$(git log --format='%H%n%B' "$log_range")"
    check_paths "files in $diff_range" "$(git diff --name-only --diff-filter=ACMR "$diff_range")"
    check_text "changes in $diff_range" "$(git diff -U0 --no-color "$diff_range" -- . "${EXCLUDES[@]}" | added_lines)"
    ;;
  --text)
    check_text "PR title/description" "$2"
    ;;
  *)
    echo "usage: $0 --msg <file> | --staged | --range <A..B> | --text <string>"
    exit 2
    ;;
esac

if [[ $found -ne 0 ]]; then
  echo
  echo "ลบลายน้ำ AI ออกก่อน (ดู IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md §9)"
  echo "  - commit ล่าสุด:  git commit --amend"
  echo "  - หลาย commit:    git rebase -i origin/develop  (เลือก reword/edit)"
  echo "  - ไฟล์ AI tool:   git rm -r --cached <path>"
  exit 1
fi
echo "${GREEN}✔ no AI watermark${RESET}"
