"use client"

import { motion } from "motion/react"

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

export default function ExploreContent() {
  return (
    <div className="min-h-screen dark:from-gray-950 dark:to-gray-900">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white">
            Explore
          </h1>
        </motion.div>

        {/* Videos Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {videos.map((video, index) => (
            <motion.div
              key={video.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
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
      </div>
    </div>
  )
}

