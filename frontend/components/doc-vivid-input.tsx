"use client"

import { useState, useRef } from "react"
import { motion, AnimatePresence } from "motion/react"
import { toast } from "sonner"
import { getUrlPreview, generateVideo } from "@/lib/api"
import { ApiClientError } from "@/lib/api-client"
import { VoiceType } from "@/lib/types/api"
import {
  Globe,
  Volume2,
  Link2,
  Upload,
  ChevronDown,
  Play,
  Pause,
  Check,
  X,
  FileText,
  ExternalLink
} from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupTextarea,
  InputGroupButton,
  InputGroupText,
} from "@/components/ui/input-group"
import {
  ButtonGroup,
  ButtonGroupSeparator,
} from "@/components/ui/button-group"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { useAutoResizeTextarea } from "@/hooks/use-auto-resize-textarea"
import { Kbd } from "./ui/kbd"

interface VoiceOption {
  id: string
  name: string
  voiceUrl?: string
}

interface UploadedFile {
  id: string
  name: string
  type: string
  file: File
}

interface UrlPreview {
  id: string
  url: string
  title: string
  favicon_url: string
}

const VOICE_OPTIONS: VoiceOption[] = [
  { id: "zephyr", name: "Zephyr", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-zephyr.wav" },
  { id: "puck", name: "Puck", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-puck.wav" },
  { id: "charon", name: "Charon", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-charon.wav" },
  { id: "kore", name: "Kore", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-kore.wav" },
  { id: "fenrir", name: "Fenrir", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-fenrir.wav" },
  { id: "leda", name: "Leda", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-leda.wav" },
  { id: "orus", name: "Orus", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-orus.wav" },
  { id: "aoede", name: "Aoede", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-aoede.wav" },
  { id: "callirrhoe", name: "Callirrhoe", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-callirrhoe.wav" },
  { id: "autonoe", name: "Autonoe", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-autonoe.wav" },
  { id: "enceladus", name: "Enceladus", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-enceladus.wav" },
  { id: "iapetus", name: "Iapetus", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-iapetus.wav" },
  { id: "umbriel", name: "Umbriel", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-umbriel.wav" },
  { id: "algieba", name: "Algieba", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-algieba.wav" },
  { id: "despina", name: "Despina", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-despina.wav" },
  { id: "erinome", name: "Erinome", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-erinome.wav" },
  { id: "algenib", name: "Algenib", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-algenib.wav" },
  { id: "rasalgethi", name: "Rasalgethi", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-rasalgethi.wav" },
  { id: "laomedeia", name: "Laomedeia", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-laomedeia.wav" },
  { id: "achernar", name: "Achernar", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-achernar.wav" },
  { id: "alnilam", name: "Alnilam", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-alnilam.wav" },
  { id: "schedar", name: "Schedar", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-schedar.wav" },
  { id: "gacrux", name: "Gacrux", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-gacrux.wav" },
  { id: "pulcherrima", name: "Pulcherrima", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-pulcherrima.wav" },
  { id: "achird", name: "Achird", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-achird.wav" },
  { id: "zubenelgenubi", name: "Zubenelgenubi", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-zubenelgenubi.wav" },
  { id: "vindemiatrix", name: "Vindemiatrix", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-vindemiatrix.wav" },
  { id: "sadachbia", name: "Sadachbia", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-sadachbia.wav" },
  { id: "sadaltager", name: "Sadaltager", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-sadaltager.wav" },
  { id: "sulafat", name: "Sulafat", voiceUrl: "https://cloud.google.com/static/text-to-speech/docs/audio/chirp3-hd-sulafat.wav" }
]

const LANGUAGE_OPTIONS = [
  { id: "en-US", name: "English", icon: <Globe className="h-4 w-4" /> },
]

// Map voice IDs to VoiceType enum values
const VOICE_ID_TO_TYPE: Record<string, VoiceType> = {
  zephyr: VoiceType.ZEPHYR,
  puck: VoiceType.PUCK,
  charon: VoiceType.CHARON,
  kore: VoiceType.KORE,
  fenrir: VoiceType.FENRIR,
  leda: VoiceType.LEDA,
  orus: VoiceType.ORUS,
  aoede: VoiceType.AOEDE,
  callirrhoe: VoiceType.CALLIRRHOE,
  autonoe: VoiceType.AUTONOE,
  enceladus: VoiceType.ENCELADUS,
  iapetus: VoiceType.IAPETUS,
  umbriel: VoiceType.UMBRIEL,
  algieba: VoiceType.ALGIEBA,
  despina: VoiceType.DESPINA,
  erinome: VoiceType.ERINOME,
  algenib: VoiceType.ALGENIB,
  rasalgethi: VoiceType.RASALGETHI,
  laomedeia: VoiceType.LAOMEDEIA,
  achernar: VoiceType.ACHERNAR,
  alnilam: VoiceType.ALNILAM,
  schedar: VoiceType.SCHEDAR,
  gacrux: VoiceType.GACRUX,
  pulcherrima: VoiceType.PULCHERRIMA,
  achird: VoiceType.ACHIRD,
  zubenelgenubi: VoiceType.ZUBENELGENUBI,
  vindemiatrix: VoiceType.VINDEMIATRIX,
  sadachbia: VoiceType.SADACHBIA,
  sadaltager: VoiceType.SADALTAGER,
  sulafat: VoiceType.SULAFAT,
}

// Map language IDs to API language codes
const LANGUAGE_ID_TO_CODE: Record<string, string> = {
  "en-US": "en",
  "zh-CN": "zh",
}

export default function DocVividInput() {
  const [value, setValue] = useState("")
  const [selectedVoice, setSelectedVoice] = useState(VOICE_OPTIONS[0])
  const [selectedLanguage, setSelectedLanguage] = useState(LANGUAGE_OPTIONS[0])
  const [isGenerating, setIsGenerating] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [playingVoiceId, setPlayingVoiceId] = useState<string | null>(null)
  const [isUrlDialogOpen, setIsUrlDialogOpen] = useState(false)
  const [urlInput, setUrlInput] = useState("")
  const [urlPreviews, setUrlPreviews] = useState<UrlPreview[]>([])
  const [isLoadingUrlPreview, setIsLoadingUrlPreview] = useState(false)

  const audioRef = useRef<HTMLAudioElement | null>(null)

  const { textareaRef, adjustHeight } = useAutoResizeTextarea({
    minHeight: 120,
    maxHeight: 300,
  })

  const handleGenerate = async () => {
    if (!value.trim() && uploadedFiles.length === 0 && urlPreviews.length === 0) {
      toast.error("Please enter text, upload a file, or add a URL")
      return
    }

    setIsGenerating(true)

    try {
      // Prepare parameters for API call
      const voiceType = VOICE_ID_TO_TYPE[selectedVoice.id] || VoiceType.ACHERNAR
      const language = LANGUAGE_ID_TO_CODE[selectedLanguage.id] || "en"

      // Determine input type and prepare params
      const params: {
        text?: string
        file?: File
        url?: string
        language: string
        voice_type: VoiceType
      } = {
        language,
        voice_type: voiceType,
      }

      // Priority: file > url > text
      if (uploadedFiles.length > 0) {
        // Use uploaded file
        params.file = uploadedFiles[0].file
        if (value.trim()) {
          params.text = value.trim()
        }
      } else if (urlPreviews.length > 0) {
        // Use URL
        params.url = urlPreviews[0].url
        if (value.trim()) {
          params.text = value.trim()
        }
      } else {
        // Use text only
        params.text = value.trim()
      }

      // Call the generateVideo API
      const response = await generateVideo(params)

      if (response.status === 'success') {
        toast.success(`Video generation started! `)

        // Clear form after successful submission
        setValue("")
        setUploadedFiles([])
        setUrlPreviews([])

        // Adjust textarea height after clearing
        setTimeout(() => adjustHeight(), 0)
      } else {
        toast.error("Failed to generate video. Please try again.")
      }
    } catch (error) {
      console.error("Error generating video:", error)

      // Handle specific API errors
      if (error instanceof ApiClientError) {
        // Show detailed error message
        const errorMsg = error.message || "Failed to generate video"

        if (error.status !== 200) {
          toast.error(errorMsg)
        }
      } else {
        // Network error or other unexpected errors
        toast.error("Network error. Please check your connection and try again.")
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleGenerate()
    }
  }

  const handlePlayVoice = (voice: VoiceOption, e: React.MouseEvent) => {
    e.stopPropagation()

    if (!voice.voiceUrl) {
      toast.info("No voice sample available for this voice")
      return
    }

    // If currently playing this voice, pause it
    if (playingVoiceId === voice.id && audioRef.current) {
      if (audioRef.current.paused) {
        // Resume playback
        audioRef.current.play().catch(() => {
          toast.error("Failed to play audio")
          setPlayingVoiceId(null)
        })
      } else {
        // Pause playback
        audioRef.current.pause()
        setPlayingVoiceId(null)
      }
      return
    }

    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }

    // Create new audio instance
    const audio = new Audio(voice.voiceUrl)
    audioRef.current = audio

    audio.addEventListener('ended', () => {
      setPlayingVoiceId(null)
    })

    audio.addEventListener('error', () => {
      toast.error("Failed to play audio")
      setPlayingVoiceId(null)
    })

    setPlayingVoiceId(voice.id)
    audio.play().catch(() => {
      toast.error("Failed to play audio")
      setPlayingVoiceId(null)
    })
  }

  const getFileType = (filename: string): string => {
    const ext = filename.split('.').pop()?.toUpperCase()
    return ext || 'FILE'
  }

  const handleFileUpload = () => {
    document.getElementById("file-upload")?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Check if there's already a file uploaded
      if (uploadedFiles.length >= 1) {
        toast.error("Only one file can be uploaded at a time")
        e.target.value = ''
        return
      }

      // Remove any existing URL previews
      if (urlPreviews.length > 0) {
        setUrlPreviews([])
      }

      const newFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        type: getFileType(file.name),
        file: file,
      }
      setUploadedFiles([newFile])
      // Reset input value to allow uploading the same file again
      e.target.value = ''
    }
  }

  const removeFile = (fileId: string) => {
    setUploadedFiles(uploadedFiles.filter(f => f.id !== fileId))
  }

  const removeUrlPreview = (previewId: string) => {
    setUrlPreviews(urlPreviews.filter(p => p.id !== previewId))
  }

  const handleUrlSubmit = async () => {
    if (!urlInput.trim()) {
      toast.error("Please enter a valid URL")
      return
    }

    // Basic URL validation
    let url: URL
    try {
      url = new URL(urlInput)
    } catch {
      toast.error("Please enter a valid URL")
      return
    }

    // Show loading state
    setIsLoadingUrlPreview(true)

    try {
      // Call the getUrlPreview API
      const response = await getUrlPreview(urlInput)

      if (response.status === 'success') {
        // Remove any existing uploaded files
        if (uploadedFiles.length > 0) {
          setUploadedFiles([])
        }

        // Remove any existing URL previews
        if (urlPreviews.length > 0) {
          setUrlPreviews([])
        }

        // Create a new URL preview object
        const newUrlPreview: UrlPreview = {
          id: Math.random().toString(36).substr(2, 9),
          url: urlInput,
          title: response.data.title || url.hostname,
          favicon_url: response.data.favicon_url || ""
        }

        // Add the URL preview to the state
        setUrlPreviews([newUrlPreview])

        // Add URL to the textarea
        const newValue = value ? `${value}\n${urlInput}` : urlInput
        setValue(newValue)

        setUrlInput("")
        setIsUrlDialogOpen(false)
        toast.success("URL added successfully")

        // Adjust textarea height after adding content
        setTimeout(() => adjustHeight(), 0)
      } else {
        toast.error("Failed to get URL preview")
      }
    } catch (error) {
      console.error("Error fetching URL preview:", error)

      // Remove any existing uploaded files
      if (uploadedFiles.length > 0) {
        setUploadedFiles([])
      }

      // Remove any existing URL previews
      if (urlPreviews.length > 0) {
        setUrlPreviews([])
      }

      // Still add the URL even if preview fails
      const newValue = value ? `${value}\n${urlInput}` : urlInput
      setValue(newValue)

      // Create a basic preview with just the URL
      const newUrlPreview: UrlPreview = {
        id: Math.random().toString(36).substr(2, 9),
        url: urlInput,
        title: url.hostname,
        favicon_url: ""
      }

      setUrlPreviews([newUrlPreview])
      setUrlInput("")
      setIsUrlDialogOpen(false)
      toast.success("URL added successfully")

      // Adjust textarea height after adding content
      setTimeout(() => adjustHeight(), 0)
    } finally {
      setIsLoadingUrlPreview(false)
    }
  }

  const handleUrlKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleUrlSubmit()
    }
    if (e.key === "Escape") {
      setIsUrlDialogOpen(false)
      setUrlInput("")
    }
  }

  return (
    <div className="w-full max-w-4xl space-y-3">
      {/* Uploaded Files and URL Previews Display */}
      <AnimatePresence>
        {(uploadedFiles.length > 0 || urlPreviews.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="flex flex-wrap gap-2"
          >
            {/* Uploaded Files */}
            {uploadedFiles.map((file) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
                className={cn(
                  "flex items-center gap-2 px-4 py-2.5 rounded-xl",
                  "bg-background border border-border shadow-sm",
                  "group hover:border-primary/50 transition-all duration-200"
                )}
              >
                <div className="flex items-center gap-2 flex-1">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{file.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground px-2 py-0.5 rounded bg-muted">
                    {file.type}
                  </span>
                  <button
                    onClick={() => removeFile(file.id)}
                    className={cn(
                      "h-5 w-5 rounded-full flex items-center justify-center",
                      "hover:bg-destructive/10 transition-colors",
                      "text-muted-foreground hover:text-destructive"
                    )}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </motion.div>
            ))}

            {/* URL Previews */}
            {urlPreviews.map((preview) => (
              <motion.div
                key={preview.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
                className={cn(
                  "flex items-center gap-2 px-4 py-2.5 rounded-xl",
                  "bg-background border border-border shadow-sm",
                  "group hover:border-primary/50 transition-all duration-200"
                )}
              >
                <div className="flex items-center gap-2 flex-1">
                  {preview.favicon_url ? (
                    <img
                      src={preview.favicon_url}
                      alt="Favicon"
                      className="h-4 w-4 object-contain"
                      onError={(e) => {
                        // Fallback to globe icon if favicon fails to load
                        e.currentTarget.style.display = 'none';
                        const nextElement = e.currentTarget.nextSibling as HTMLElement;
                        if (nextElement) nextElement.style.display = 'block';
                      }}
                    />
                  ) : null}
                  <Globe
                    className={cn(
                      "h-4 w-4 text-muted-foreground",
                      preview.favicon_url ? "hidden" : "block"
                    )}
                  />
                  <span className="text-sm font-medium truncate max-w-[200px]" title={preview.title}>
                    {preview.title}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={preview.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-primary transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                  <button
                    onClick={() => removeUrlPreview(preview.id)}
                    className={cn(
                      "h-5 w-5 rounded-full flex items-center justify-center",
                      "hover:bg-destructive/10 transition-colors",
                      "text-muted-foreground hover:text-destructive"
                    )}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <InputGroup className="flex-col rounded-2xl shadow-[0px_0px_16px_0px_#0000000A] border border-border/50 overflow-hidden min-h-[180px]">
          {/* Textarea Section */}
          <InputGroupTextarea
            ref={textareaRef}
            value={value}
            onChange={(e) => {
              setValue(e.target.value)
              adjustHeight()
            }}
            onKeyDown={handleKeyDown}
            placeholder="Enter text, upload files, or paste links - we'll create videos for you"
            className={cn(
              "px-6 py-5 text-base min-h-[120px]",
              "placeholder:text-muted-foreground/60"
            )}
          />

          {/* Control Bar */}
          <InputGroupAddon
            align="block-end"
            className="px-4 py-3"
          >
            <div className="flex items-center justify-between w-full gap-3">
              {/* Left Controls */}
              <ButtonGroup className="flex items-center">
                {/* Language Selector */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-9 px-3 gap-2 text-sm font-normal"
                    >
                      <InputGroupText>
                        <Globe className="h-4 w-4" />
                        <span>{selectedLanguage.name}</span>
                      </InputGroupText>
                      <ChevronDown className="h-3 w-3 ml-auto" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="w-48">
                    <DropdownMenuLabel className="text-xs text-muted-foreground">
                      Select Language
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    {LANGUAGE_OPTIONS.map((lang) => (
                      <DropdownMenuItem
                        key={lang.id}
                        onClick={() => setSelectedLanguage(lang)}
                        className="flex items-center justify-between"
                      >
                        <div className="flex items-center gap-2">
                          {lang.icon}
                          <span>{lang.name}</span>
                        </div>
                        {selectedLanguage.id === lang.id && (
                          <Check className="h-4 w-4 text-primary" />
                        )}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>

                <ButtonGroupSeparator />

                {/* Voice Selector */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-9 px-3 gap-2 text-sm font-normal"
                    >
                      <InputGroupText>
                        <Volume2 className="h-4 w-4" />
                        <span>{selectedVoice.name}</span>
                      </InputGroupText>
                      <ChevronDown className="h-3 w-3 ml-auto" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="w-64 p-2">
                    <DropdownMenuLabel className="text-xs text-muted-foreground px-2">
                      Select a voice
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <ScrollArea className="h-[240px]">
                      <div className="space-y-1 py-1">
                        {VOICE_OPTIONS.map((voice) => (
                          <motion.div
                            key={voice.id}
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.99 }}
                          >
                            <button
                              onClick={() => setSelectedVoice(voice)}
                              className={cn(
                                "w-full flex items-center justify-between gap-3 px-3 py-3 rounded-lg",
                                "hover:bg-accent/50 transition-all duration-200",
                                "group relative",
                                selectedVoice.id === voice.id && "bg-accent/70"
                              )}
                            >
                              <div className="flex items-center gap-3 flex-1">
                                <div className="relative">
                                  <button
                                    onClick={(e) => handlePlayVoice(voice, e)}
                                    className={cn(
                                      "w-10 h-10 rounded-full flex items-center justify-center",
                                      "bg-gradient-to-br from-primary/20 to-primary/10",
                                      "border border-primary/20",
                                      "hover:from-primary/30 hover:to-primary/20 hover:scale-110",
                                      "transition-all duration-200",
                                      "disabled:opacity-50 disabled:cursor-not-allowed",
                                      playingVoiceId === voice.id && "from-primary/40 to-primary/30"
                                    )}
                                    disabled={!voice.voiceUrl}
                                  >
                                    <AnimatePresence mode="wait">
                                      {playingVoiceId === voice.id ? (
                                        <motion.div
                                          key="pause"
                                          initial={{ scale: 0, rotate: -90 }}
                                          animate={{ scale: 1, rotate: 0 }}
                                          exit={{ scale: 0, rotate: 90 }}
                                          transition={{ duration: 0.2 }}
                                        >
                                          <Pause className="h-4 w-4 text-primary fill-primary" />
                                        </motion.div>
                                      ) : (
                                        <motion.div
                                          key="play"
                                          initial={{ scale: 0, rotate: -90 }}
                                          animate={{ scale: 1, rotate: 0 }}
                                          exit={{ scale: 0, rotate: 90 }}
                                          transition={{ duration: 0.2 }}
                                          className="ml-0.5"
                                        >
                                          <Play className="h-4 w-4 text-primary fill-primary" />
                                        </motion.div>
                                      )}
                                    </AnimatePresence>
                                  </button>
                                </div>
                                <div className="text-left">
                                  <div className="font-medium text-sm">{voice.name}</div>
                                </div>
                              </div>
                              <AnimatePresence>
                                {selectedVoice.id === voice.id && (
                                  <motion.div
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    exit={{ scale: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                  >
                                    <Check className="h-4 w-4 text-primary" />
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </button>
                          </motion.div>
                        ))}
                      </div>
                    </ScrollArea>
                  </DropdownMenuContent>
                </DropdownMenu>
              </ButtonGroup>

              {/* Right Controls */}
              <div className="flex items-center gap-2">
                {/* File Upload & Link Buttons */}
                <ButtonGroup className="flex items-center">
                  <InputGroupButton
                    size="icon-sm"
                    onClick={() => setIsUrlDialogOpen(true)}
                    className="hover:bg-accent/50"
                    disabled={uploadedFiles.length > 0}
                    title={uploadedFiles.length > 0 ? "Remove file first to add URL" : "Add URL"}
                  >
                    <Link2 className={cn("h-4 w-4", uploadedFiles.length > 0 ? "text-muted-foreground/40" : "")} />
                  </InputGroupButton>

                  <InputGroupButton
                    size="icon-sm"
                    onClick={handleFileUpload}
                    className="hover:bg-accent/50"
                    disabled={urlPreviews.length > 0}
                    title={urlPreviews.length > 0 ? "Remove URL first to upload file" : "Upload file"}
                  >
                    <Upload className={cn("h-4 w-4", urlPreviews.length > 0 ? "text-muted-foreground/40" : "")} />
                  </InputGroupButton>
                </ButtonGroup>

                {/* Generate Button */}
                <Button
                  onClick={handleGenerate}
                  disabled={(!value.trim() && uploadedFiles.length === 0 && urlPreviews.length === 0) || isGenerating}
                  className={cn(
                    "h-9 px-6 font-medium",
                    "bg-gradient-to-r from-primary to-primary/80",
                    "hover:from-primary/90 hover:to-primary/70",
                    "transition-all duration-200",
                    "shadow-sm hover:shadow-md"
                  )}
                >
                  {isGenerating ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="h-4 w-4 border-2 border-white border-t-transparent rounded-full"
                    />
                  ) : (
                    "Generate"
                  )}
                </Button>
              </div>

              {/* Hidden file input */}
              <input
                id="file-upload"
                type="file"
                className="hidden"
                accept=".pdf,.docx,.md,.txt"
                onChange={handleFileChange}
              />
            </div>
          </InputGroupAddon>
        </InputGroup>
      </motion.div>

      {/* Helper Text */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-xs text-muted-foreground text-center mt-3"
      >
        Supports PDF, Word, TXT and other document formats · Press{" "}
        <Kbd>⌘</Kbd> +{" "}
        <Kbd>Enter</Kbd> to generate quickly
      </motion.p>

      {/* URL Input Dialog */}
      <Dialog
        open={isUrlDialogOpen}
        onOpenChange={(open) => {
          // Only allow opening if no files are uploaded
          if (open && uploadedFiles.length > 0) {
            toast.error("Please remove the uploaded file first")
            return
          }
          setIsUrlDialogOpen(open)
        }}
      >
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold">Paste Link</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Input
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  onKeyDown={handleUrlKeyDown}
                  placeholder="https://example.com"
                  className="flex-1"
                  autoFocus
                />
                <Button
                  onClick={handleUrlSubmit}
                  disabled={!urlInput.trim() || isLoadingUrlPreview}
                  size="icon"
                  className="shrink-0"
                >
                  {isLoadingUrlPreview ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="h-4 w-4 border-2 border-white border-t-transparent rounded-full"
                    />
                  ) : (
                    <Check className="h-4 w-4" />
                  )}
                </Button>
              </div>

              <div className="text-sm text-muted-foreground text-center">
                Paste any URL from documents or blogs
              </div>

              {urlPreviews.length > 0 && (
                <div className="text-sm text-amber-500 text-center font-medium">
                  Adding a new URL will replace the existing one
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
