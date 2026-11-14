import { streamText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { google } from '@ai-sdk/google';
import { z } from 'zod';

// Demo in-memory mock banking ledger for instant verification & simulation
const DEMO_ACCOUNTS: Record<string, { name: string; balance: number; currency: string; status: string; type: string }> = {
  '1001': { name: 'Rahul Sharma', balance: 45250.00, currency: 'INR', status: 'ACTIVE', type: 'SAVINGS' },
  '1002': { name: 'Priya Patel', balance: 128400.50, currency: 'INR', status: 'ACTIVE', type: 'CURRENT' },
  '1003': { name: 'Amit Kumar', balance: 8200.00, currency: 'INR', status: 'ACTIVE', type: 'SAVINGS' },
  '1004': { name: 'Sneha Rao', balance: 2450.00, currency: 'INR', status: 'BLOCKED', type: 'SAVINGS' },
};

const DEMO_TRANSACTIONS: Record<string, Array<{ id: string; type: string; amount: number; date: string; description: string }>> = {
  '1001': [
    { id: 'TXN-9021', type: 'CREDIT', amount: 35000, date: '2026-11-01', description: 'Monthly Salary Deposit' },
    { id: 'TXN-9022', type: 'DEBIT', amount: 4500, date: '2026-11-05', description: 'ATM Cash Withdrawal' },
    { id: 'TXN-9023', type: 'DEBIT', amount: 1250, date: '2026-11-10', description: 'Grocery Store POS' },
  ],
  '1002': [
    { id: 'TXN-8812', type: 'CREDIT', amount: 75000, date: '2026-11-03', description: 'Vendor Payment Received' },
    { id: 'TXN-8813', type: 'DEBIT', amount: 18200, date: '2026-11-08', description: 'Office Rent Transfer' },
  ],
};

// Define banking tools
const tools = {
  checkBalance: tool({
    description: 'Check account balance, status, and account type for a customer account number.',
    parameters: z.object({
      accountNumber: z.string().describe('The 4-digit or full account number, e.g. 1001'),
    }),
    execute: async ({ accountNumber }) => {
      const acc = DEMO_ACCOUNTS[accountNumber] || DEMO_ACCOUNTS['1001'];
      return {
        accountNumber: accountNumber,
        holderName: acc.name,
        balance: acc.balance,
        currency: acc.currency,
        accountType: acc.type,
        status: acc.status,
        timestamp: new Date().toISOString(),
      };
    },
  }),

  getTransactionHistory: tool({
    description: 'Retrieve the recent transaction records for an account.',
    parameters: z.object({
      accountNumber: z.string().describe('The customer account number'),
      limit: z.number().optional().default(5).describe('Number of transactions to fetch'),
    }),
    execute: async ({ accountNumber, limit }) => {
      const history = DEMO_TRANSACTIONS[accountNumber] || DEMO_TRANSACTIONS['1001'] || [];
      return {
        accountNumber,
        count: Math.min(limit || 5, history.length),
        transactions: history.slice(0, limit || 5),
      };
    },
  }),

  calculateLoanEMI: tool({
    description: 'Calculate monthly loan EMI payment, total interest, and grand total based on principal, rate, and tenure.',
    parameters: z.object({
      principal: z.number().describe('Loan principal amount in currency units (e.g. 500000)'),
      annualInterestRate: z.number().describe('Annual interest rate in percentage (e.g. 8.5)'),
      tenureMonths: z.number().describe('Tenure in number of months (e.g. 36 for 3 years)'),
    }),
    execute: async ({ principal, annualInterestRate, tenureMonths }) => {
      const monthlyRate = annualInterestRate / 12 / 100;
      const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, tenureMonths)) / (Math.pow(1 + monthlyRate, tenureMonths) - 1);
      const totalPayment = emi * tenureMonths;
      const totalInterest = totalPayment - principal;

      return {
        principal,
        annualInterestRate: `${annualInterestRate}%`,
        tenureMonths,
        monthlyEMI: Math.round(emi * 100) / 100,
        totalInterest: Math.round(totalInterest * 100) / 100,
        totalPayment: Math.round(totalPayment * 100) / 100,
      };
    },
  }),

  simulateTransfer: tool({
    description: 'Simulate a money transfer between two accounts with validation.',
    parameters: z.object({
      fromAccount: z.string().describe('Sender account number'),
      toAccount: z.string().describe('Recipient account number'),
      amount: z.number().positive().describe('Transfer amount'),
      remark: z.string().optional().describe('Transfer remark / memo'),
    }),
    execute: async ({ fromAccount, toAccount, amount, remark }) => {
      const sender = DEMO_ACCOUNTS[fromAccount];
      if (sender && sender.balance < amount) {
        return {
          success: false,
          error: 'Insufficient funds. Current balance is ' + sender.balance + ' ' + sender.currency,
        };
      }

      const referenceId = 'TXN-REF-' + Math.floor(100000 + Math.random() * 900000);
      return {
        success: true,
        referenceId,
        fromAccount,
        toAccount,
        amount,
        remark: remark || 'Instant Fund Transfer',
        estimatedSettlement: 'Immediate (IMPS/UPI)',
        status: 'COMPLETED',
        timestamp: new Date().toISOString(),
      };
    },
  }),

  bankPolicyFAQ: tool({
    description: 'Look up Nova Bank official banking policies, ATM limits, card replacement, and branch IFSC codes.',
    parameters: z.object({
      topic: z.enum(['atm_limit', 'card_blocking', 'interest_rates', 'ifsc', 'support']).describe('Policy category'),
    }),
    execute: async ({ topic }) => {
      const policies = {
        atm_limit: {
          dailyWithdrawalLimit: '₹50,000 for Classic Debit Cards / ₹100,000 for Platinum',
          perTransactionLimit: '₹20,000',
          freeATMTransactionsPerMonth: '5 at Nova Bank ATMs, 3 at other bank ATMs',
        },
        card_blocking: {
          emergencyHotline: '1800-NOVA-BANK (1800-668-2265)',
          smsBlocking: 'SMS BLOCK <Last 4 digits> to 56767',
          instantBlock: 'You can immediately freeze your card in the Nova Bank Customer Portal under Settings.',
        },
        interest_rates: {
          savingsAccount: '3.50% p.a. calculated daily, credited quarterly',
          fixedDeposit1Year: '7.10% p.a. (Senior citizens +0.50%)',
          homeLoan: '8.40% p.a. floating',
          personalLoan: '10.50% - 12.75% p.a.',
        },
        ifsc: {
          bankName: 'Nova Bank of Commerce',
          headquartersIFSC: 'NOVA0001001',
          branch: 'Connaught Place Main Branch, New Delhi',
        },
        support: {
          email: 'support@novabank.com',
          tollFree: '1800-668-2265',
          hours: '24/7 Digital Concierge & Phone Support',
        },
      };

      return policies[topic];
    },
  }),
};

export const runtime = 'nodejs';
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Model selection: check available keys
  const hasOpenAI = Boolean(process.env.OPENAI_API_KEY);
  const hasGoogle = Boolean(process.env.GOOGLE_GENERATIVE_AI_API_KEY);

  let model;
  if (hasOpenAI) {
    model = openai('gpt-4o-mini');
  } else if (hasGoogle) {
    model = google('gemini-1.5-flash');
  } else {
    // If no key is set yet, provide an informative fallback stream
    return new Response(
      JSON.stringify({
        error: 'No AI provider API key found. Please configure OPENAI_API_KEY or GOOGLE_GENERATIVE_AI_API_KEY in your environment variables or Vercel Project Settings.',
      }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const result = streamText({
    model,
    messages,
    system: `You are the official AI Banking Assistant for Nova Bank.
You are professional, trustworthy, concise, and helpful.
You have access to tools for checking balances, transaction history, EMI loan calculations, fund transfer simulations, and official bank policies.
When a user asks about accounts or balances, use the checkBalance or getTransactionHistory tools.
When calculating loans, use calculateLoanEMI.
When transferring funds, simulate the transfer safely using simulateTransfer.
Always format currency figures clearly (e.g. ₹45,250.00 or $45,250.00).
Never disclose fictitious security credentials or account passwords.`,
    tools,
    maxSteps: 5,
  });

  return result.toDataStreamResponse();
}
