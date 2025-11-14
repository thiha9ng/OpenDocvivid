"use client"

import { AuroraText } from "@/components/ui/aurora-text"
import { motion } from "motion/react"
import DocVividInput from "@/components/doc-vivid-input"

// Video data
const videos = [
  {
    id: "V_py9Ap0qOE",
    title: "Introducing LangChain 1.0",
    thumbnail: `https://img.youtube.com/vi/V_py9Ap0qOE/maxresdefault.jpg`,
    url: "https://www.youtube.com/watch?v=V_py9Ap0qOE",
    duration: "3:52"
  },
  {
    id: "MN0A9N1tJT4",
    title: "Claude Agent SDK by Anthropic",
    thumbnail: `https://img.youtube.com/vi/MN0A9N1tJT4/maxresdefault.jpg`,
    url: "https://youtu.be/MN0A9N1tJT4?si=coeRkeGiXCZr_7Wb",
    duration: "3:22"
  },
  {
    id: "NvRsasOsMUE",
    title: "Introduction to Agentic Coding",
    thumbnail: `https://img.youtube.com/vi/NvRsasOsMUE/maxresdefault.jpg`,
    url: "https://youtu.be/NvRsasOsMUE",
    duration: "3:36"
  },
]

export default function Page() {
  return (
    <div className="w-full">
      {/* Hero section */}
      <div className="flex flex-col items-center justify-center p-4 py-16 md:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-4xl space-y-8"
        >
          <div className="text-center space-y-4">
            <motion.h1
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-4xl md:text-5xl font-bold tracking-tight bg-clip-text"
            >
              <AuroraText>AI DocVivid</AuroraText>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-muted-foreground text-lg md:text-xl"
            >
              Transform Technical Documentation into Engaging AI-Powered Videos in Minutes
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex justify-center w-full"
          >
            <DocVividInput />
          </motion.div>
        </motion.div>
      </div>

      {/* Explore section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="container mx-auto px-4 py-16"
      >
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Explore
          </h2>
          <p className="text-muted-foreground text-lg">
            Discover examples of AI-powered documentation videos
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {videos.map((video, index) => (
            <motion.div
              key={video.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
              className="space-y-3"
            >
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-1">{video.title}</h3>
              </div>
              <div className="bg-black rounded-lg overflow-hidden shadow-xl">
                <iframe
                  id={`ytplayer-${video.id}`}
                  width="100%"
                  height="220"
                  src={`https://www.youtube.com/embed/${video.id}?origin=${typeof window !== 'undefined' ? window.location.origin : ''}`}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="w-full"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="py-8 border-t border-border/40"
      >
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-muted-foreground">
            © 2025 AI DocVivid. All rights reserved. |{" "}
            <a
              href="/terms"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors underline underline-offset-4"
            >
              Terms of Service
            </a>
            {" | "}
            <a
              href="/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors underline underline-offset-4"
            >
              Privacy Policy
            </a>
          </p>
        </div>
      </motion.footer>
    </div>
  )
}
