# WAGMI Crypto Dashboard

A modern, responsive cryptocurrency dashboard built with React, Next.js, and Tailwind CSS.

## Features

- Real-time cryptocurrency data visualization
- Responsive design for all devices
- Beautiful glassmorphism UI
- Token feed with latest updates
- Interactive charts and analytics

## Tech Stack

- Next.js
- React
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- Shadcn UI components

## Getting Started

```bash
# Install dependencies
npm install
# or
pnpm install

# Run the development server
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
/
├── components/
│   ├── feed-card.tsx                     # Card component for displaying token data
│   ├── feed-section.tsx                  # Section that displays the grid of token cards
│   └── ui/
│       ├── StatusBadge.tsx               # Component for displaying status indicators
│       └── DexButton.tsx                 # Button component for DEX links
│
├── hooks/
│   └── useCalls.ts                       # Hook for fetching token call data
│
├── lib/
│   ├── firebase.ts                       # Firebase configuration and initialization
│   └── utils.ts                          # Utility functions including formatDate
│
├── types/
│   └── index.ts                          # TypeScript interfaces including TokenData
│
├── public/                               # Static files
│
├── pages/
│   ├── _app.tsx                          # Next.js app wrapper
│   └── index.tsx                         # Main landing page
│
├── styles/
│   └── globals.css                       # Global CSS styles including Tailwind
│
├── .gitignore                            # Git ignore file
├── package.json                          # Project dependencies and scripts
├── tailwind.config.js                    # Tailwind CSS configuration
└── tsconfig.json                         # TypeScript configuration
```

## License


git add .
git commit -m "Remove service account key and add to gitignore"
git push


MIT 