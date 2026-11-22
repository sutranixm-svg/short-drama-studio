#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "正在安装元一AI短剧多智能体团队（1主4子）..."

# 1. 链接到 Claude Code 全局技能与子Agent目录
if [ -d "$HOME/.claude" ] || [ "${1:-}" = "--claude" ]; then
  mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents"
  for skill_dir in "$REPO_ROOT"/skills/*; do
    [ -d "$skill_dir" ] && ln -sfn "$skill_dir" "$HOME/.claude/skills/$(basename "$skill_dir")"
  done
  for agent_file in "$REPO_ROOT"/.claude/agents/*.md; do
    [ -f "$agent_file" ] && ln -sfn "$agent_file" "$HOME/.claude/agents/$(basename "$agent_file")"
  done
  echo "[OK] 已注册 6 个 Skill 与 5 个独立 Bot 到 ~/.claude/"
fi

# 2. 链接到 OpenClaw 全局技能目录
if [ -d "$HOME/.openclaw" ] || [ "${1:-}" = "--openclaw" ]; then
  mkdir -p "$HOME/.openclaw/skills"
  for skill_dir in "$REPO_ROOT"/skills/*; do
    [ -d "$skill_dir" ] && ln -sfn "$skill_dir" "$HOME/.openclaw/skills/$(basename "$skill_dir")"
  done
  echo "[OK] 已注册 6 个 Skill 到 ~/.openclaw/skills/"
fi

echo "安装完成！请在你的 Bot 中输入：初始化短剧团队"
