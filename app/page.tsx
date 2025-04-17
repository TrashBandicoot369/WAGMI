import Header from "@/components/header"
import HeroSection from "@/components/hero-section"
import FeedSection from "@/components/feed-section"
import Footer from "@/components/footer"
import BackgroundAnimation from "@/components/background-animation"
import { sampleTokenData } from "@/lib/sample-data"

export default function Home() {
  // Add a class to the main element to ensure proper positioning
  return (
    <main className="min-h-screen text-white overflow-hidden relative">
      <BackgroundAnimation />
      <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10 z-0"></div>
      <div className="relative z-10">
        <Header />
        {/* Add padding-top to push content down and make room for the logo */}
        <div className="pt-20">
          <HeroSection />
          <FeedSection tokenData={sampleTokenData} />
          <Footer />
        </div>
      </div>
    </main>
  )
}
