#!/usr/bin/env python3
"""
Code Review Script
Uses OpenRouter API to review code changes
"""

import os
import sys
import json
import urllib.request

MODEL = os.environ.get("MODEL", "minimax/minimax-m2.5")
MAX_TOKENS = 300
MAX_DIFF_LINES = 500

def load_diff(path="diff.txt"):
    try:
        with open(path) as f:
            diff = f.read()
        lines = diff.split("\n")
        if len(lines) > MAX_DIFF_LINES:
            diff = "\n".join(lines[:MAX_DIFF_LINES])
            diff += f"\n\n... (truncated, {len(lines) - MAX_DIFF_LINES} more lines)"
        return diff
    except FileNotFoundError:
        return ""

def call_api(api_key, diff):
    system_prompt = """You are a senior code reviewer. Review the following code changes.
Focus on: bugs, security, code style, performance. Keep concise (max 100 words)."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Review this code:\n\n{diff}"}
    ]

    data = {"model": MODEL, "messages": messages, "max_tokens": MAX_TOKENS}

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(data).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com",
            "X-Title": "CodeReview"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())
            return result.get("choices", [{}])[0].get("message", {}).get("content", "REVIEW_FAILED_NO_CONTENT")
    except Exception as e:
        return f"REVIEW_SYSTEM_FAILURE: {e}"

def main():
    api_key = os.environ.get("KEY", "")
    if not api_key:
        print("MISSING_API_KEY - Secret OPENROUTER_API_KEY not accessible in repo settings")
        sys.exit(1)
    
    diff = load_diff()
    if not diff:
        print("NO_CHANGES_TO_REVIEW")
        sys.exit(0)
    
    review = call_api(api_key, diff)
    print(review)

if __name__ == "__main__":
    main()
