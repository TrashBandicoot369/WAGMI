import Link from "next/link"
import { Twitter, TextIcon as Telegram } from "lucide-react"

interface FooterProps {
  socialLinks?: {
    twitter?: string
    telegram?: string
  }
  copyrightText?: string
}

export default function Footer({
  socialLinks = {
    twitter: "#",
    telegram: "#",
  },
  copyrightText = "© 2025 WAGMI. Powered by Degens.",
}: FooterProps) {
  return (
    <footer className="py-8 mt-12 relative">
      <div className="absolute inset-0 bg-white/10 backdrop-blur-sm"></div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="flex flex-col items-center justify-center">
          <div className="flex items-center space-x-6 mb-6">
            {socialLinks.twitter && (
              <Link
                href={socialLinks.twitter}
                className="text-pink-500 hover:text-green-400 transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={24} />
              </Link>
            )}

            {socialLinks.telegram && (
              <Link
                href={socialLinks.telegram}
                className="text-pink-500 hover:text-green-400 transition-colors"
                aria-label="Telegram"
              >
                <Telegram size={24} />
              </Link>
            )}
          </div>

          <p className="text-white/70 text-sm text-center">{copyrightText}</p>
        </div>
      </div>
    </footer>
  )
}
