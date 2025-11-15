import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a3a2e] via-[#0f2922] to-[#0a1f1a]">
      {/* Navigation */}
      <nav className="bg-[#1a1a1a] shadow-lg border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center gap-3">
              {/* Clock Logo Icon */}
              <div className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6l4 2"/>
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white uppercase tracking-tight leading-tight">
                  SMART CONTRACTS
                  <br />
                  <span className="text-lg">ESCROW</span>
                </h1>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-white hover:text-[#00ff00] transition-colors font-medium">
                Home
              </Link>
              <Link href="#about" className="text-white hover:text-[#00ff00] transition-colors font-medium flex items-center gap-1">
                About
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </Link>
              <Link href="#service-providers" className="text-white hover:text-[#00ff00] transition-colors font-medium">
                Service Providers
              </Link>
              <Link href="#faq" className="text-white hover:text-[#00ff00] transition-colors font-medium flex items-center gap-1">
                FAQ
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </Link>
              <Link href="/contact" className="text-white hover:text-[#00ff00] transition-colors font-medium">
                Contact Us
              </Link>
              <Link href="/dashboard/buyer" className="bg-[#00ff00] text-black hover:bg-[#00dd00] px-6 py-2.5 rounded font-bold transition-all">
                Client Area
              </Link>
            </div>
            <div className="flex md:hidden items-center gap-2">
              <Link href="/auth/login" className="text-white text-sm">Login</Link>
              <Link href="/dashboard/buyer" className="bg-[#00ff00] text-black px-4 py-2 rounded text-sm font-semibold">
                Client Area
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[600px] flex items-center py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="max-w-7xl mx-auto w-full grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="text-left z-10">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4">
              Smart Contracts Escrow
            </h2>
            <p className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#00ff00] mb-6">
              the safest way to buy and sell
            </p>
            <p className="text-lg text-gray-300 mb-8 max-w-2xl leading-relaxed">
              Smart Contracts Escrow protects both buyers and sellers by holding funds securely until work is delivered and approved. Whether you&apos;re a freelancer, small business, or client, our escrow platform ensures safe, transparent, and fair payments across Africa.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                href="/auth/register" 
                className="bg-[#00ff00] text-black hover:bg-[#00dd00] px-8 py-4 rounded font-semibold transition-all text-center text-lg border-2 border-[#00ff00]"
              >
                Transact Now
              </Link>
              <Link 
                href="#how-it-works" 
                className="bg-transparent text-white hover:bg-white/10 px-8 py-4 rounded font-semibold transition-all text-center text-lg border-2 border-white flex items-center justify-center gap-2"
              >
                <span>→</span>
                Learn How It Works
              </Link>
            </div>
          </div>

          {/* Right Image - Padlock */}
          <div className="relative hidden lg:flex justify-center items-center">
            <div className="relative w-full max-w-lg h-[500px] flex items-center justify-center">
              {/* Realistic Padlock Illustration */}
              <div className="relative">
                {/* Chain link left */}
                <div className="absolute -left-24 top-32 w-16 h-16 border-8 border-gray-500 rounded-full opacity-40 transform rotate-12"></div>
                
                {/* Main padlock body */}
                <svg className="w-80 h-auto" viewBox="0 0 300 400" fill="none">
                  {/* Shackle - darker metallic */}
                  <path 
                    d="M100 120 L100 70 Q100 20 150 20 Q200 20 200 70 L200 120" 
                    stroke="#4a5568" 
                    strokeWidth="24" 
                    fill="none"
                    strokeLinecap="round"
                    opacity="0.9"
                  />
                  {/* Shackle highlight */}
                  <path 
                    d="M105 120 L105 75 Q105 30 150 30 Q195 30 195 75 L195 120" 
                    stroke="#718096" 
                    strokeWidth="8" 
                    fill="none"
                    strokeLinecap="round"
                    opacity="0.5"
                  />
                  
                  {/* Lock body - main shape */}
                  <rect 
                    x="60" 
                    y="110" 
                    width="180" 
                    height="260" 
                    rx="25" 
                    fill="#5a6268"
                    opacity="0.95"
                  />
                  
                  {/* Lock body shadow */}
                  <rect 
                    x="70" 
                    y="120" 
                    width="160" 
                    height="240" 
                    rx="20" 
                    fill="#4a5568"
                    opacity="0.8"
                  />
                  
                  {/* Highlight on lock body */}
                  <rect 
                    x="75" 
                    y="125" 
                    width="50" 
                    height="200" 
                    rx="20" 
                    fill="white"
                    opacity="0.12"
                  />
                  
                  {/* Keyhole outer circle */}
                  <circle cx="150" cy="220" r="28" fill="#2d3748" opacity="0.9"/>
                  
                  {/* Keyhole slot */}
                  <rect x="142" y="220" width="16" height="55" rx="3" fill="#1a202c" opacity="0.95"/>
                  
                  {/* Keyhole inner detail */}
                  <circle cx="150" cy="220" r="12" fill="#000000" opacity="0.7"/>
                </svg>
                
                {/* Chain link right */}
                <div className="absolute -right-20 bottom-28 w-14 h-14 border-8 border-gray-500 rounded-full opacity-40 transform -rotate-12"></div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
