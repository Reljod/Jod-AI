export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center min-h-screen bg-background">
      <main className="flex flex-col items-center gap-8 text-center">
        <div className="flex items-center gap-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 32 32"
            width="48"
            height="48"
          >
            <rect width="32" height="32" rx="6" fill="#000000" />
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
          <h1 className="text-4xl font-bold tracking-tight">Jod-AI</h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-md">
          Building the future of AI
        </p>
      </main>
    </div>
  );
}
