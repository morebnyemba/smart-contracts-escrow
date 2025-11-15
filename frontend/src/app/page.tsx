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
              <Link href="/" className="text-white hover:text-[#00ff00] transition-colors">
                Home
              </Link>
              <Link href="#about" className="text-white hover:text-[#00ff00] transition-colors">
                About
              </Link>
              <Link href="#service-providers" className="text-white hover:text-[#00ff00] transition-colors">
                Service Providers
              </Link>
              <Link href="#faq" className="text-white hover:text-[#00ff00] transition-colors">
                FAQ
              </Link>
              <Link href="/contact" className="text-white hover:text-[#00ff00] transition-colors">
                Contact Us
              </Link>
              <Link href="/dashboard/buyer" className="bg-[#00ff00] text-black hover:bg-[#00dd00] px-6 py-2.5 rounded font-semibold transition-all">
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
            <div className="relative w-full max-w-lg">
              {/* Padlock SVG */}
              <svg className="w-full h-auto opacity-80" viewBox="0 0 400 500" fill="none">
                {/* Shackle */}
                <path 
                  d="M150 150 L150 100 Q150 50 200 50 Q250 50 250 100 L250 150" 
                  stroke="#6b7280" 
                  strokeWidth="30" 
                  fill="none"
                  strokeLinecap="round"
                />
                {/* Lock Body */}
                <rect 
                  x="100" 
                  y="150" 
                  width="200" 
                  height="250" 
                  rx="20" 
                  fill="#4b5563"
                  stroke="#6b7280"
                  strokeWidth="4"
                />
                {/* Keyhole */}
                <circle cx="200" cy="250" r="25" fill="#1f2937"/>
                <rect x="190" y="250" width="20" height="50" rx="3" fill="#1f2937"/>
                
                {/* Shine effect */}
                <rect 
                  x="120" 
                  y="170" 
                  width="40" 
                  height="120" 
                  rx="20" 
                  fill="white"
                  opacity="0.15"
                />
              </svg>
              
              {/* Additional chain elements */}
              <div className="absolute -left-16 top-1/4 w-20 h-20 border-8 border-gray-500 rounded-full opacity-60"></div>
              <div className="absolute -right-12 bottom-1/4 w-16 h-16 border-8 border-gray-500 rounded-full opacity-60"></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
