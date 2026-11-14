# Nova Bank AI Copilot (Vercel AI SDK)

Intelligent banking copilot built with **Next.js 14**, **Vercel AI SDK**, **Tailwind CSS**, and multi-model support (**OpenAI** & **Google Gemini**).

---

## Features

- **Live Streaming Responses:** Real-time token streaming with `streamText` and `@ai-sdk/react`.
- **Integrated Banking Tools:**
  - `checkBalance`: Instantly query account status and balance.
  - `getTransactionHistory`: Inspect recent deposits, withdrawals, and transfers.
  - `calculateLoanEMI`: High-precision EMI calculator for personal, home, or auto loans.
  - `simulateTransfer`: Safely test funds transfer between customer accounts.
  - `bankPolicyFAQ`: Look up official ATM daily limits, card freeze hotlines, and IFSC codes.
- **Midnight-Navy Design:** Matches the Nova Bank aesthetic with emerald accents and glassmorphic navigation.

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
# or
pnpm install
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```
Add your API key:
- `OPENAI_API_KEY` or
- `GOOGLE_GENERATIVE_AI_API_KEY`

### 3. Run Locally
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to interact with the banking copilot.

---

## Deploy to Vercel

```bash
vercel
```
Set `OPENAI_API_KEY` or `GOOGLE_GENERATIVE_AI_API_KEY` in your Vercel Project Environment Variables.
