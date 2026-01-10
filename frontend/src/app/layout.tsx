import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { Navbar } from '@/components/shared/Navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Insurance AI Bridge',
  description: 'AI-powered claim analysis system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ErrorBoundary>
          <Providers>
            <Navbar />
            <main className="min-h-screen">
              {children}
            </main>
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  )
}

