"use client";

import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { useSession } from "next-auth/react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Play,
  Clock,
  CheckCircle,
  Video,
  Calendar,
  Loader2,
  AlertCircle,
  Download,
} from "lucide-react";
import { getTasks } from "@/lib/api";
import type { VideoTask } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function LibraryPage() {
  const { status } = useSession();
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [videos, setVideos] = useState<VideoTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch video tasks from API
  useEffect(() => {
    const fetchTasks = async () => {
      if (status === "loading") return; // Wait for session to load

      try {
        setLoading(true);
        setError(null);

        const response = await getTasks({
          page: 1,
          page_size: 50, // Get more tasks at once
          sort_by: 'created_at',
          sort_order: 'desc'
        });

        if (response.status === 'success') {
          setVideos(response.data.tasks);
        } else {
          toast.error('Failed to load video tasks', {
            description: 'Please try refreshing the page',
          });
        }
      } catch {
        setError('Failed to load video tasks. Please try again.');
        toast.error('Failed to load video library', {
          description: 'There was a problem connecting to the server',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [status]);

  const handleVideoClick = (video: VideoTask) => {
    if (video.status === "completed" && video.output_video_url) {
      const videoUrl = video.output_video_url
      setSelectedVideo(videoUrl);
      setIsDialogOpen(true);
    }
  };

  const completedVideos = videos.filter((v) => v.status === "completed");
  const processingVideos = videos.filter((v) => v.status === "processing" || v.status === "pending");

  // Merge all videos, with generating ones first
  const allVideos = [...processingVideos, ...completedVideos];

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
            Library
          </h1>
        </motion.div>

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <Loader2 className="h-12 w-12 animate-spin text-blue-500 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Loading your videos...
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Please wait while we fetch your video library
            </p>
          </motion.div>
        )}

        {/* Error State */}
        {error && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <AlertCircle className="size-12 text-red-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Failed to load videos
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {error}
            </p>
            <Button
              onClick={() => window.location.reload()}
              className=""
            >
              Try Again
            </Button>
          </motion.div>
        )}

        {/* All Videos */}
        {!loading && !error && allVideos.length > 0 && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {allVideos.map((video, index) => (
              <motion.div
                key={video.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                whileHover={video.status === "completed" ? { y: -8 } : {}}
                className={video.status === "completed" ? "cursor-pointer" : ""}
                onClick={() => video.status === "completed" && handleVideoClick(video)}
              >
                <Card className={`group relative overflow-hidden border-2 transition-all duration-300 ${video.status === "processing" || video.status === "pending"
                    ? "border-blue-200 dark:border-blue-900 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm"
                    : video.status === "failed"
                      ? "border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/50"
                      : "border-transparent hover:border-green-500 dark:hover:border-green-600 bg-white dark:bg-gray-900 hover:shadow-xl"
                  }`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-lg line-clamp-2 flex-1 min-h-[3rem] flex items-start">
                        {/* Use task_id as fallback title if no specific title field */}
                        {video.name || `Video Task ${video.id.slice(0, 8)}`}
                      </CardTitle>
                      <Badge
                        variant="outline"
                        className={`shrink-0 ${video.status === "processing" || video.status === "pending"
                            ? "border-blue-500 text-blue-600 dark:text-blue-400"
                            : video.status === "failed"
                              ? "border-red-500 text-red-600 dark:text-red-400"
                              : "border-green-500 text-green-600 dark:text-green-400"
                          }`}
                      >
                        {video.status === "processing" || video.status === "pending" ? (
                          <>
                            <Clock className="mr-1 h-3 w-3" />
                            {video.status === "pending" ? "Pending" : "Processing"}
                          </>
                        ) : video.status === "failed" ? (
                          <>
                            <AlertCircle className="mr-1 h-3 w-3" />
                            Failed
                          </>
                        ) : (
                          <>
                            <CheckCircle className="mr-1 h-3 w-3" />
                            Ready
                          </>
                        )}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className={`relative aspect-video w-full overflow-hidden rounded-lg ${video.status === "processing"
                          ? "bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-950 dark:to-purple-950"
                          : "bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900"
                        } flex items-center justify-center`}>
                        {video.status === "processing" ? (
                          <Loader2 className="h-12 w-12 animate-spin text-blue-500" />
                        ) : (
                          <>
                            {/* Thumbnail overlay */}
                            <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                              <motion.div
                                whileHover={{ scale: 1.1 }}
                                className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg"
                              >
                                <Play className="h-8 w-8 text-green-600 ml-1" />
                              </motion.div>
                            </div>
                            {/* Video icon when not hovering */}
                            <div className="absolute inset-0 flex items-center justify-center group-hover:opacity-0 transition-opacity">
                              <Video className="h-12 w-12 text-gray-400" />
                            </div>
                          </>
                        )}
                      </div>

                      {video.status === "processing" || video.status === "pending" ? (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">
                              Progress
                            </span>
                            <span className="font-medium text-blue-600 dark:text-blue-400">
                              {video.progress || 0}%
                            </span>
                          </div>
                          <Progress value={video.progress || 0} className="h-2" />
                        </div>
                      ) : video.status === "failed" ? (
                        <div className="space-y-2">
                          <div className="text-sm text-red-600 dark:text-red-400">
                            {video.error_message || "Processing failed"}
                          </div>
                          <div className="flex items-center text-gray-500 dark:text-gray-400 text-sm">
                            <Calendar className="mr-2 h-4 w-4" />
                            {new Date(video.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center text-gray-500 dark:text-gray-400">
                              <Calendar className="mr-2 h-4 w-4" />
                              {new Date(video.created_at).toLocaleDateString()}
                            </div>
                            <div className="flex flex-col items-end">
                              <span className="font-medium text-gray-700 dark:text-gray-300">
                                {video.target_language?.toUpperCase()}
                              </span>
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {video.voice_type}
                              </span>
                            </div>
                          </div>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="w-full cursor-pointer flex items-center justify-center"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (video.output_video_url) {
                                window.open(video.output_video_url, '_blank');
                              }
                            }}
                          >
                            <Download className="mr-2 size-4" />
                            Download
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && allVideos.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <Video className="h-20 w-20 text-gray-300 dark:text-gray-700 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No videos yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Start creating your first AI-generated documentation video
            </p>
          </motion.div>
        )}
      </div>

      {/* Video Player Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-5xl w-full p-0 overflow-hidden">
          <div className="bg-black">
            {selectedVideo && (
              <video
                src={selectedVideo}
                controls
                autoPlay
                className="w-full h-auto max-h-[80vh]"
                onError={() => {
                  toast.info('Unable to play this video', {
                    description: 'Please refresh the page and try again'
                  });
                }}
              >
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}