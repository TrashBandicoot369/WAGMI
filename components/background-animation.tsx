"use client"

import { useEffect, useRef } from "react"

export default function BackgroundAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    // Define colors based on the WAGMI logo - exact match for the logo
    const hotPink = "#e6007a" // Hot pink from logo - exact match
    const palePink = "#ffe6f5" // Super pale pink
    const midPink = "#ff9ed2" // Mid-tone pink for transition

    // Animation variables
    let time = 0
    const speed = 0.0003

    // Animation function
    const animate = () => {
      time += speed

      // Create gradient - ensure top left is solid hot pink
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)

      // Fixed color stops with solid hot pink at the top left
      gradient.addColorStop(0, hotPink) // Solid hot pink at top left
      gradient.addColorStop(0.3, hotPink) // Extend solid hot pink area
      gradient.addColorStop(0.5 + Math.sin(time) * 0.05, midPink) // Subtle animation in the middle
      gradient.addColorStop(1, palePink) // Pale pink at bottom right

      // Fill background
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
    }
  }, [])

  return <canvas ref={canvasRef} className="fixed top-0 left-0 w-full h-full z-0" />
}
