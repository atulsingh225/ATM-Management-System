# Vercel Agent Setup Guide

This guide details how to configure and utilize **Vercel Agent**—the platform-level AI assistant built directly into Vercel—for automated code review, security vulnerability scanning, and incident investigation.

---

## 1. What Vercel Agent Does

Vercel Agent connects directly to your repository and deployments to provide:
- **Automated Code Review:** Multi-step reasoning across PRs to detect logic bugs, performance regressions, and style issues.
- **Security Review:** Scans every commit and PR for security vulnerabilities, secrets, and misconfigurations, reporting findings directly as GitHub checks and in the Vercel **Vulnerabilities** dashboard.
- **Incident Investigation:** Analyzes runtime errors, 5xx anomalies, and latency spikes using deployment logs and telemetry.
- **Interactive Chat & Slack Integration:** Query system status, logs, and proposed actions directly from the Vercel dashboard or Slack.

---

## 2. Enabling Vercel Agent on Your Project

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click the **Agent** icon in the top right navigation bar.
3. Select your linked project (`ATM-Management-System`).
4. Under **Settings & Integrations**, enable:
   - **Code Review:** Automatically analyzes pull requests.
   - **Security Review:** Enables vulnerability audits on every push.
   - **Slack Notifications (Optional):** Connect your Slack workspace to receive investigation alerts and run debugging queries via `@vercel` in channels.

---

## 3. Triggering Reviews on Pull Requests

- **Automatic:** When a new pull request is opened or updated, Vercel Agent automatically begins review.
- **Manual Comment Trigger:** You can trigger a review at any time by commenting on any PR:
  ```markdown
  @vercel please review this PR for security vulnerabilities and banking logic errors
  ```
- **Investigation Trigger:** If a deployment fails or throws an exception, open the deployment details and click **Investigate with Agent** for root-cause diagnosis.
