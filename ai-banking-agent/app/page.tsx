'use client';

import React, { useRef, useEffect } from 'react';
import { useChat } from '@ai-sdk/react';
import {
  Bot,
  User,
  Send,
  Sparkles,
  CreditCard,
  History,
  Calculator,
  ShieldCheck,
  Building2,
  ArrowRight,
  RefreshCw,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function BankingAssistantPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error, reload, setInput } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const quickPrompts = [
    { label: 'Check Balance (AC 1001)', prompt: 'What is the current balance and account status for account 1001?' },
    { label: 'Recent Transactions', prompt: 'Show the recent transaction history for account 1001.' },
    { label: 'Calculate Loan EMI', prompt: 'Calculate the monthly EMI for a ₹500,000 car loan at 8.5% interest for 3 years.' },
    { label: 'Simulate Transfer', prompt: 'Simulate transferring ₹2,500 from account 1001 to account 1002 for rent.' },
    { label: 'Card Lost / Limits', prompt: 'What are the daily ATM withdrawal limits and how can I block a lost debit card?' },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-4 py-3">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center font-bold text-slate-950 text-xl shadow-lg shadow-emerald-500/20">
              N
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white tracking-wide">NOVA BANK</span>
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  AI Copilot
                </span>
              </div>
              <p className="text-xs text-slate-400">Powered by Vercel AI SDK</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 font-medium">Core Banking System Online</span>
            </div>
            <a
              href="http://127.0.0.1:5000"
              target="_blank"
              rel="noreferrer"
              className="text-emerald-400 hover:text-emerald-300 transition-colors hidden sm:inline"
            >
              Open Flask App &rarr;
            </a>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-6 flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-24">
          {messages.length === 0 ? (
            <div className="my-auto py-12 flex flex-col items-center justify-center text-center">
              <div className="h-16 w-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mb-4 text-emerald-400">
                <Sparkles className="h-8 w-8" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Welcome to Nova Bank AI Copilot</h2>
              <p className="text-slate-400 max-w-md text-sm mb-8 leading-relaxed">
                Your intelligent financial copilot. Inquire about balances, calculate loan payments, simulate transactions, or explore bank policies in real time.
              </p>

              {/* Quick Prompts */}
              <div className="w-full max-w-2xl grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
                {quickPrompts.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(item.prompt)}
                    className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-850 transition-all text-sm group flex items-start justify-between"
                  >
                    <div>
                      <p className="font-medium text-slate-200 group-hover:text-emerald-300 transition-colors">
                        {item.label}
                      </p>
                      <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{item.prompt}</p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-emerald-400 ml-2 mt-0.5 shrink-0 transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => {
              const isUser = message.role === 'user';
              return (
                <div
                  key={message.id}
                  className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="h-8 w-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center shrink-0 mt-1">
                      <Bot className="h-4 w-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                      isUser
                        ? 'bg-emerald-600 text-white rounded-br-none'
                        : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                    }`}
                  >
                    {/* Render message parts or fallback content */}
                    {message.parts ? (
                      message.parts.map((part, index) => {
                        if (part.type === 'text') {
                          return <div key={index} className="whitespace-pre-wrap">{part.text}</div>;
                        }
                        if (part.type === 'tool-invocation') {
                          const call = part.toolInvocation;
                          return (
                            <div
                              key={index}
                              className="my-2 p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono"
                            >
                              <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1">
                                <CheckCircle2 className="h-3.5 w-3.5" />
                                <span>Tool: {call.toolName}</span>
                              </div>
                              {'result' in call ? (
                                <pre className="overflow-x-auto text-slate-300 p-2 bg-slate-900 rounded border border-slate-850">
                                  {JSON.stringify(call.result, null, 2)}
                                </pre>
                              ) : (
                                <div className="text-slate-400 italic">Executing query...</div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })
                    ) : (
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    )}
                  </div>

                  {isUser && (
                    <div className="h-8 w-8 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center shrink-0 mt-1">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="h-8 w-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center shrink-0 animate-pulse">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-slate-900 border border-slate-800 text-slate-400 rounded-2xl rounded-bl-none px-4 py-3 text-xs flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
                <span>Nova Bank Copilot is processing with banking tools...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-400" />
                <span>{error.message || 'An error occurred during communication.'}</span>
              </div>
              <button
                onClick={() => reload()}
                className="flex items-center gap-1 px-3 py-1 rounded bg-red-500/20 hover:bg-red-500/30 text-xs font-medium"
              >
                <RefreshCw className="h-3 w-3" /> Retry
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Fixed Bottom Input Bar */}
      <footer className="fixed bottom-0 left-0 right-0 bg-slate-950/90 backdrop-blur border-t border-slate-800 p-4">
        <div className="max-w-5xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (input.trim()) {
                handleSubmit(e);
              }
            }}
            className="flex items-center gap-2"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={input}
                onChange={handleInputChange}
                placeholder="Ask about account balances, EMI calculation, transfers, or card policies..."
                className="w-full bg-slate-900 text-slate-100 placeholder-slate-500 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-semibold px-5 py-3 rounded-xl flex items-center gap-2 text-sm transition-all shadow-lg shadow-emerald-500/20 shrink-0"
            >
              <span>Send</span>
              <Send className="h-4 w-4" />
            </button>
          </form>
          <p className="text-center text-[11px] text-slate-500 mt-2">
            Simulated banking environment. Tool operations are executed securely via Vercel AI SDK.
          </p>
        </div>
      </footer>
    </div>
  );
}
