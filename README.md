# 🏦 Nova Bank — Modern ATM & Core Banking Management System

[![Live Website](https://img.shields.io/badge/Live_Website-novabank07.vercel.app-00e599?style=for-the-badge&logo=vercel&logoColor=black)](https://novabank07.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=for-the-badge&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed_on-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://novabank07.vercel.app)

A secure, full-stack ATM and Core Banking Management System featuring a **Customer Banking Portal**, an **Admin Control Panel**, and an intelligent **AI Banking Copilot** powered by Next.js and the Vercel AI SDK.

---

## 🌐 Live Website & Demo

Experience the live application deployed on Vercel:

- 🚀 **Live Banking Application:** **[https://novabank07.vercel.app](https://novabank07.vercel.app)**

---

## 🌟 Key Features

### 👤 1. Customer Banking Portal
- **Secure PIN Authentication:** Account number and 4-digit PIN authentication with session management.
- **Balance Inquiry & Account Insights:** Real-time ledger balances and account status tracking.
- **Cash Deposit & Withdrawal:** Instant validation, daily limits, and ATM cash distribution logic.
- **Fund Transfers (P2P):** Seamless inter-account transfers with immediate settlement.
- **Transaction History & Receipts:** Mini statements and printable transaction receipts with reference IDs.
- **Customer Registration & KYC:** Self-registration workflow (`PENDING` &rarr; `ACTIVE`).

### 🛡️ 2. Admin Control Center
- **Customer Lifecycle Management:** Filter accounts by status (`ALL`, `PENDING`, `ACTIVE`, `BLOCKED`, `CLOSED`, `REJECTED`).
- **KYC Review Pipeline:** One-click approval, activation, suspension, or closure of customer accounts.
- **Customer Account Editor:** Update customer credentials, contact details, account types, and limits.
- **System-Wide Transaction Ledger:** Audit log of all deposits, withdrawals, and transfers with timestamps and IDs.
- **Real-Time Analytics:** Live dashboard cards for total customers, active deposits, pending verifications, and transaction volume.

### 🤖 3. Nova Bank AI Copilot (Vercel AI SDK)
- **Interactive Banking Assistant:** Located in `/ai-banking-agent`, built with Next.js 14 and Vercel AI SDK.
- **Integrated Banking Tools:**
  - `checkBalance`: Instantly queries account balance and status.
  - `getTransactionHistory`: Retrieves recent transaction statements.
  - `calculateLoanEMI`: Computes monthly EMI, total interest, and grand total for loans.
  - `simulateTransfer`: Simulates instant funds transfers with validation.
  - `bankPolicyFAQ`: Provides bank policies on ATM limits, card blocking, and IFSC codes.
- **Real-Time Streaming:** Part-aware tool invocation rendering and streaming tokens.

---

## 📁 Project Structure

```
ATM-Management-System/
├── .github/
│   └── workflows/
│       └── vercel-agent.yml        # Vercel Agent PR review & security workflow
├── ai-banking-agent/               # Next.js + Vercel AI SDK banking copilot
│   ├── app/
│   │   ├── api/chat/route.ts       # Streaming AI route with banking tools
│   │   ├── globals.css             # Dark-mode styling
│   │   ├── layout.tsx              # Root HTML & metadata
│   │   └── page.tsx                # Chat UI with tool cards
│   ├── package.json
│   ├── tsconfig.json
│   └── vercel.json
├── api/
│   └── index.py                    # Vercel Serverless WSGI entrypoint
├── docs/
│   └── VERCEL_AGENT_SETUP.md       # Vercel Agent configuration guide
├── static/
│   └── style.css                   # Midnight-navy premium banking styles
├── templates/                      # Jinja2 template components
│   ├── admin_customer_edit.html    # Customer details editor
│   ├── admin_customer_transactions.html # Single-customer transaction view
│   ├── admin_customers.html        # Customer management with status tabs
│   ├── admin_dashboard.html        # Admin analytics & overview
│   ├── admin_login.html            # Owner portal login
│   ├── admin_transactions.html     # System-wide transaction logs
│   ├── base.html                   # Master layout with top navigation
│   ├── change_pin.html             # Customer PIN change
│   ├── dashboard.html              # Customer home & quick actions
│   ├── error.html                  # Error handling page
│   ├── history.html                # Customer mini statement
│   ├── login.html                  # Customer login & landing
│   ├── profile.html                # Customer profile details
│   ├── receipt.html                # Transaction receipt
│   ├── register.html               # Customer self-registration
│   ├── register_success.html       # Customer registration confirmation
│   └── transaction.html            # Deposit & withdrawal form
├── tests/
│   ├── test_admin_customer_edit.py # Admin editing tests
│   └── test_dashboard_flows.py     # Banking workflow tests
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── app.py                          # Main Flask core banking application
├── atm.db                          # SQLite database
├── init_db.py                      # Database initialization script
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment configuration
└── README.md
```

---

## 🚀 Local Development Guide

### 1. Flask Core Banking App

```bash
# Clone the repository
git clone https://github.com/atulsingh225/ATM-Management-System.git
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
Open **`http://127.0.0.1:5000`** in your browser.

---

### 2. Next.js AI Banking Copilot

```bash
cd ai-banking-agent

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Run development server
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 👨‍💻 Developed By

<div align="center">

### **Atul Singh**  
*Full Stack Developer | Software Engineer | AI & Cloud Enthusiast*

[![Live Website](https://img.shields.io/badge/Live_Website-novabank07.vercel.app-00e599?style=for-the-badge&logo=vercel&logoColor=black)](https://novabank07.vercel.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Atul_Singh-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/atul-singh-26b439362)
[![GitHub](https://img.shields.io/badge/GitHub-atulsingh225-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/atulsingh225)
[![LeetCode](https://img.shields.io/badge/LeetCode-atulsingh225-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/u/atulsingh225)
[![Instagram](https://img.shields.io/badge/Instagram-@atulsinghrajput__07-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://instagram.com/atulsinghrajput_07)
[![Email](https://img.shields.io/badge/Email-atulsingh782188@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:atulsingh782188@gmail.com)

---

### 🔗 Connect With Me

| Platform | Profile URL / ID |
| :--- | :--- |
| 🌐 **Live Website** | [novabank07.vercel.app](https://novabank07.vercel.app) |
| 💼 **LinkedIn** | [linkedin.com/in/atul-singh-26b439362](https://www.linkedin.com/in/atul-singh-26b439362) |
| 🐙 **GitHub** | [github.com/atulsingh225](https://github.com/atulsingh225) (`@atulsingh225`) |
| 🧩 **LeetCode** | [leetcode.com/u/atulsingh225](https://leetcode.com/u/atulsingh225) (`@atulsingh225`) |
| 📸 **Instagram** | [instagram.com/atulsinghrajput_07](https://instagram.com/atulsinghrajput_07) (`@atulsinghrajput_07`) |
| 📧 **Email** | [atulsingh782188@gmail.com](mailto:atulsingh782188@gmail.com) |

</div>

---

## 📜 License
This project is licensed under the **MIT License**.
