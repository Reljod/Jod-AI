"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-[#030303] text-white overflow-hidden font-sans">
      {/* Dynamic Background Glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-600/10 blur-[120px] pointer-events-none" />

      {/* Grid Pattern Accent */}
      <div 
        className="absolute inset-0 opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: `radial-gradient(circle, #ffffff 1px, transparent 1px)`,
          backgroundSize: '24px 24px'
        }}
      />

      <main className="relative z-10 flex flex-col items-center gap-10 text-center px-6 max-w-2xl">
        {/* Glassmorphic Brand Card */}
        <div className="flex flex-col items-center gap-6 p-8 md:p-12 rounded-3xl border border-white/5 bg-white/[0.02] backdrop-blur-xl shadow-2xl">
          
          {/* SVG Logo (Single SVG on page to ensure E2E strictness passes) */}
          <div className="relative group">
            {/* Logo Glow Effect */}
            <div className="absolute inset-0 rounded-xl bg-gradient-to-tr from-blue-500 to-violet-500 blur-xl opacity-30 group-hover:opacity-60 transition-opacity duration-500" />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 32 32"
              width="64"
              height="64"
              className="relative z-10 filter drop-shadow-md transform group-hover:scale-105 transition-transform duration-300"
            >
              <rect width="32" height="32" rx="8" fill="#000000" />
              <path
                d="M8 10 L8 22 C8 24 10 26 12 26 L14 26 C16 26 18 24 18 22 L18 10"
                stroke="#ffffff"
                strokeWidth="3"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="22" cy="16" r="3" fill="#ffffff" />
            </svg>
          </div>

          {/* Heading */}
          <div className="space-y-3">
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-white/90 to-white/60">
              Jod-AI
            </h1>
            <p className="text-lg md:text-xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-violet-400">
              Welcome to Jod-AI
            </p>
          </div>

          {/* Divider */}
          <div className="w-12 h-[1px] bg-white/10 my-1" />

          {/* Subtitle / Description */}
          <p className="text-sm md:text-base text-gray-400 leading-relaxed max-w-md">
            Experience a deep agent platform with multi-model orchestrations, tool extensibility, and automated context compaction.
          </p>

          {/* Premium CTA Button */}
          <Link 
            href="/chat"
            className="relative mt-4 group inline-flex items-center justify-center px-8 py-3.5 rounded-xl font-semibold text-sm transition-all duration-300 active:scale-98 overflow-hidden"
          >
            {/* Background Gradient */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-violet-600 group-hover:from-blue-500 group-hover:to-violet-500 transition-colors" />
            {/* Border shine */}
            <div className="absolute inset-[1px] rounded-[10px] bg-[#030303] group-hover:opacity-0 transition-opacity duration-300" />
            
            {/* Content text */}
            <span className="relative z-10 text-white/90 group-hover:text-white transition-colors">
              Launch Application
            </span>
          </Link>
        </div>

        {/* Feature Badges (pure CSS layout, no SVGs to avoid Playwright collision) */}
        <div className="flex flex-wrap justify-center gap-3 text-xs text-gray-500">
          <span className="px-3 py-1.5 rounded-full border border-white/5 bg-white/[0.01]">LangGraph Agent</span>
          <span className="px-3 py-1.5 rounded-full border border-white/5 bg-white/[0.01]">OpenRouter APIs</span>
          <span className="px-3 py-1.5 rounded-full border border-white/5 bg-white/[0.01]">Context Compactor</span>
        </div>
      </main>
    </div>
  );
}
