---
name: website-design-audit
description: Audits any website for design, copy, and UX issues. Use when user asks to audit, review, analyze or improve a website design, layout, copy, CTAs, headlines, or overall look. Screenshots every page via Microlink free API, sends to Claude vision, returns a full prioritized report with exact fixes.
metadata:
  openclaw:
    os: [linux]
---

# Website Design Audit

Full visual + copy audit using Microlink screenshots + vision model.

## How to Run

```bash
python3 {baseDir}/scripts/audit.py <URL>
```

## Output Format

### 🔴 Critical Fixes
### 🟡 Important Improvements
### 🟢 Nice to Have
### ✅ What's Working
### 💬 Suggested Headline
### 🎯 Suggested CTA

Always give exact replacement text, never vague suggestions.
