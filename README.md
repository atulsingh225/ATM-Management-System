# 🏦 Nova Bank — Modern ATM & Core Banking Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=for-the-badge&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Vercel AI SDK](https://img.shields.io/badge/Vercel_AI_SDK-4.x-black?style=for-the-badge&logo=vercel&logoColor=white)](https://sdk.vercel.ai)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed_on-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

A full-stack, secure ATM and Core Banking Management System featuring a **Customer Banking Portal**, an **Admin Control Panel**, and an intelligent **AI Banking Copilot** powered by Next.js and the Vercel AI SDK.

---

## 🌟 Key Highlights & Features

### 👤 1. Customer Banking Portal
- **Secure PIN Authentication:** Card/Account number and 4-digit PIN login with automatic session timeout.
- **Balance Inquiry & Account Insights:** Real-time ledger balances, account type, and account status tracking.
- **Cash Deposit & Withdrawal:** Instant validation, daily limit enforcement, and ATM currency notes distribution simulation.
- **Fund Transfers (P2P):** Seamless inter-account transfers with immediate settlement and transaction remarks.
- **Mini Statements & Receipts:** Downloadable and printable receipts for ATM transactions with reference IDs.
- **Account Registration & KYC:** Customer onboarding with automated status workflow (`PENDING` &rarr; `ACTIVE`).

### 🛡️ 2. Admin & Owner Control Center
- **Customer Lifecycle Management:** Filter accounts by status (`ALL`, `PENDING`, `ACTIVE`, `BLOCKED`, `CLOSED`, `REJECTED`).
- **KYC Review Pipeline:** One-click approval, suspension, or rejection of pending customer applications.
- **Customer Account Editor:** Update customer credentials, contact details, account types, and limits.
- **Global Transaction Ledger:** Full audit trails of all system-wide deposits, withdrawals, and transfers with date, amount, and reference IDs.
- **Real-Time Analytics:** Live stat cards for total customers, active deposits, pending verifications, and daily transaction volume.

### 🤖 3. Nova Bank AI Copilot (Vercel AI SDK)
- **Interactive Financial Assistant:** Located in `/ai-banking-agent`, built on Next.js 14 and Vercel AI SDK.
- **Automated Banking Tools:**
  - `checkBalance`: Instantly queries customer balance and status.
  - `getTransactionHistory`: Retrieves detailed statement records.
  - `calculateLoanEMI`: Computes monthly EMI, total interest, and grand total for loans.
  - `simulateTransfer`: Validates balance and simulates instant UPI/IMPS transfers.
  - `bankPolicyFAQ`: Retrieves bank policies on ATM limits, lost card hotlisting, and IFSC codes.
- **Real-Time Streaming:** High-performance token streaming UI with part-aware tool call rendering.

### ☁️ 4. Cloud & Vercel Native Architecture
- **Serverless Ready:** Built with `api/index.py` and dynamic database mounting (`/tmp/atm.db`) to adhere to Vercel's ephemeral read-only serverless filesystem.
- **Automated CI/CD:** GitHub Actions workflow (`.github/workflows/vercel-agent.yml`) for automated pull request code reviews and security scanning.

---

## 📁 Project Architecture

```
ATM-Management-System/
├── .github/
│   └── workflows/
│       └── vercel-agent.yml        # Vercel Agent PR review & security workflow
├── ai-banking-agent/               # Next.js + Vercel AI SDK banking copilot
│   ├── app/
│   │   ├── api/chat/route.ts       # AI streaming route with banking tools
│   │   ├── globals.css             # Tailwind dark-mode styles
│   │   ├── layout.tsx              # Root HTML & fonts
│   │   └── page.tsx                # Interactive chat UI with tool cards
│   ├── package.json
│   ├── tsconfig.json
│   └── vercel.json
├── api/
│   └── index.py                    # Vercel Serverless WSGI entrypoint
├── database/
│   ├── atm.db                      # SQLite relational database
│   └── setup_db.py                 # Schema migration & seed data
├── docs/
│   └── VERCEL_AGENT_SETUP.md       # Vercel Agent configuration guide
├── static/
│   ├── css/
│   │   └── style.css               # Midnight-navy premium banking theme
│   └── js/
│       └── main.js                 # Client-side validation & UI handlers
├── templates/                      # Jinja2 template components
│   ├── admin_customers.html        # Customer management with status tabs
│   ├── admin_customer_edit.html    # Customer details editor
│   ├── admin_dashboard.html        # Admin analytics & overview
│   ├── admin_login.html            # Owner portal login
│   ├── admin_transactions.html     # System-wide transaction logs
│   ├── base.html                   # Master layout with top navigation
│   ├── customer_dashboard.html     # Customer home & quick actions
│   ├── deposit.html                # Deposit workflow
│   ├── fast_cash.html              # 1-click ATM cash withdrawal
│   ├── index.html                  # Customer login & landing
│   ├── mini_statement.html         # Transaction history statement
│   ├── receipt.html                # Transaction receipt
│   ├── register.html               # Customer self-registration
│   ├── transfer.html               # Inter-account transfer
│   └── withdraw.html               # Custom withdrawal
├── .gitignore
├── app.py                          # Main Flask core banking application
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment configuration
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ (for AI Copilot)
- Git

### 1. Clone & Set Up Flask Core Banking App

```bash
# Clone the repository
git clone https://github.com/atulsingh456/ATM-Management-System.git
cd ATM-Management-System

# Create and activate virtual environment
python -m venv .venv

# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```
Open your browser at **`http://127.0.0.1:5000`**.

#### Default Demo Credentials:
- **Customer Portal:** Account `1001` | PIN `1234`
- **Admin Portal:** Username `admin` | Password `admin123` (`http://127.0.0.1:5000/admin/login`)

---

### 2. Run the Next.js AI Banking Copilot

```bash
cd ai-banking-agent

# Install dependencies
npm install

# Copy environment template and configure keys
cp .env.example .env.local

# Run Next.js development server
npm run dev
```
Open your browser at **`http://localhost:3000`**.

---

## 🌐 Deploy to Vercel

### Deploy Core Flask Banking System
```bash
vercel
```
*Vercel detects `vercel.json` and compiles `api/index.py` with `@vercel/python` automatically.*

### Deploy AI Banking Copilot
```bash
cd ai-banking-agent
vercel
```
Set `OPENAI_API_KEY` or `GOOGLE_GENERATIVE_AI_API_KEY` in your Vercel Project Settings.

---

## 👨‍💻 Developed By

<div align="center">

### **Atul Singh**  
*Full Stack Developer | Software Engineer | AI & Cloud Enthusiast*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Atul_Singh-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/atulsingh456)
[![GitHub](https://img.shields.io/badge/GitHub-atulsingh456-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/atulsingh456)
[![LeetCode](https://img.shields.io/badge/LeetCode-atulsingh456-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/u/atulsingh456)
[![Instagram](https://img.shields.io/badge/Instagram-@atulsingh456-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://instagram.com/atulsingh456)
[![Email](https://img.shields.io/badge/Email-atulsingh456@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:atulsingh456@gmail.com)

---

### 🔗 Connect With Me

| Platform | Profile URL / ID |
| :--- | :--- |
| 💼 **LinkedIn** | [linkedin.com/in/atulsingh456](https://www.linkedin.com/in/atulsingh456) |
| 🐙 **GitHub** | [github.com/atulsingh456](https://github.com/atulsingh456) (`@atulsingh456`) |
| 🧩 **LeetCode** | [leetcode.com/u/atulsingh456](https://leetcode.com/u/atulsingh456) (`@atulsingh456`) |
| 📸 **Instagram** | [instagram.com/atulsingh456](https://instagram.com/atulsingh456) (`@atulsingh456`) |
| 📧 **Email** | [atulsingh456@gmail.com](mailto:atulsingh456@gmail.com) |

</div>

---

## 📜 License
This project is licensed under the **MIT License**. Feel free to use and customize it for educational and commercial banking implementations.
