import React, { useState, useEffect, useRef, useMemo } from 'react'
import Hls from 'hls.js'
import mpegts from 'mpegts.js'
import { 
  Home, 
  Tv, 
  Film, 
  Clapperboard, 
  Settings, 
  Play, 
  Pause,
  Maximize,
  Minimize,
  Search, 
  Heart, 
  ShieldAlert, 
  X, 
  Volume2, 
  VolumeX, 
  Lock,
  Unlock,
  Key,
  Globe,
  User,
  LogOut,
  AlertCircle
} from 'lucide-react'
import { XtreamApi } from './services/xtreamApi'
import type { 
  XtreamAccountInfo, 
  XtreamCategory, 
  XtreamLiveChannel, 
  XtreamMovie, 
  XtreamSeries 
} from './services/xtreamApi'

// Fallback image helper
function MoviePoster({ src, title, category }: { src: string; title: string; category?: string }) {
  const [hasError, setHasError] = useState(false)
  const isPosterEmpty = !src || src.trim() === ''

  if (hasError || isPosterEmpty) {
    return (
      <div className="w-full h-full bg-gradient-to-br from-purple-900/60 to-black/85 flex flex-col items-center justify-between p-4 text-center border border-white/5 select-none">
        <div className="w-8 h-8 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-neon mt-4">
          <Film className="w-4 h-4" />
        </div>
        <span className="text-xs font-bold text-white leading-tight uppercase px-1 line-clamp-3">{title}</span>
        <span className="text-[9px] text-brand-neon font-semibold uppercase mb-2">{category || 'IPTV'}</span>
      </div>
    )
  }

  return (
    <img 
      src={src} 
      alt={title} 
      onError={() => setHasError(true)}
      className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105" 
      loading="lazy"
    />
  )
}

function ChannelLogo({ src, name }: { src: string; name: string }) {
  const [hasError, setHasError] = useState(false)
  const isLogoEmpty = !src || src.trim() === ''

  if (hasError || isLogoEmpty) {
    return (
      <div className="w-16 h-16 rounded-2xl bg-brand-purple/20 flex items-center justify-center border border-white/10 text-brand-neon text-xs font-black uppercase">
        {name.slice(0, 3)}
      </div>
    )
  }

  return (
    <img 
      src={src} 
      alt={name} 
      onError={() => setHasError(true)}
      className="w-16 h-16 rounded-2xl object-cover border border-white/10" 
      loading="lazy"
    />
  )
}

function App() {
  // Authentication states
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [serverUrl, setServerUrl] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [showCorsWarning, setShowCorsWarning] = useState(false)
  const [accountInfo, setAccountInfo] = useState<XtreamAccountInfo | null>(null)

  // Real IPTV Content States
  const [liveCategories, setLiveCategories] = useState<XtreamCategory[]>([])
  const [vodCategories, setVodCategories] = useState<XtreamCategory[]>([])
  const [seriesCategories, setSeriesCategories] = useState<XtreamCategory[]>([])
  const [channels, setChannels] = useState<XtreamLiveChannel[]>([])
  const [movies, setMovies] = useState<XtreamMovie[]>([])
  const [series, setSeries] = useState<XtreamSeries[]>([])

  // Category selection states
  const [selectedLiveCat, setSelectedLiveCat] = useState<string>('all')
  const [selectedVodCat, setSelectedVodCat] = useState<string>('all')
  const [selectedSeriesCat, setSelectedSeriesCat] = useState<string>('all')

  // Navigation states
  const [activeTab, setActiveTab] = useState<'home' | 'live' | 'movies' | 'series' | 'settings'>('home')
  const [favorites, setFavorites] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)
  const [currentTimeStr, setCurrentTimeStr] = useState('20:45')
  
  // Parental Control States
  const [parentalLocked, setParentalLocked] = useState(true)
  const [showPinModal, setShowPinModal] = useState(false)
  const [pinInput, setPinInput] = useState('')
  const [pinError, setPinError] = useState(false)
  const [savedPin] = useState('1234') // Default PIN

  // Video Player States
  const [activeStream, setActiveStream] = useState<string | null>(null)
  const [activeStreamTitle, setActiveStreamTitle] = useState('')
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isVideoPaused, setIsVideoPaused] = useState(false)
  const [playerLoading, setPlayerLoading] = useState(false)
  const [playerError, setPlayerError] = useState<string | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [recentPlays, setRecentPlays] = useState<any[]>([])
  const [showControls, setShowControls] = useState(true)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const mpegtsPlayerRef = useRef<mpegts.Player | null>(null)
  const playerContainerRef = useRef<HTMLDivElement>(null)
  const controlsTimeoutRef = useRef<any>(null)

  // Series Detail View States
  const [selectedSeriesObj, setSelectedSeriesObj] = useState<XtreamSeries | null>(null)
  const [selectedSeriesInfo, setSelectedSeriesInfo] = useState<any | null>(null)
  const [selectedSeason, setSelectedSeason] = useState<number>(1)
  const [loadingSeriesInfo, setLoadingSeriesInfo] = useState(false)

  // Listen to browser fullscreen change event
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
    }
  }, [])

  // Auto-hide controls timer
  const resetControlsTimer = () => {
    setShowControls(true)
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current)
    }
    // Only auto-hide if video is playing and not paused
    if (videoRef.current && !videoRef.current.paused) {
      controlsTimeoutRef.current = setTimeout(() => {
        setShowControls(false)
      }, 3500) // 3.5 seconds
    }
  }

  const handleContainerClick = (e: React.MouseEvent) => {
    // If clicking on a button or the controls bar, just reset the timer
    if ((e.target as HTMLElement).closest('.player-controls-bar')) {
      resetControlsTimer()
      return
    }
    // Toggle controls visibility when clicking on the background/video
    if (showControls) {
      setShowControls(false)
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current)
      }
    } else {
      resetControlsTimer()
    }
  }

  // Monitor when video starts playing to start the timer, and cleanup on close
  useEffect(() => {
    if (isVideoPlaying && activeStream) {
      setShowControls(true)
      resetControlsTimer()
    }
    return () => {
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current)
      }
    }
  }, [isVideoPlaying, activeStream])

  // Progressive Loading / Pagination limits
  const [visibleLiveCount, setVisibleLiveCount] = useState(60)
  const [visibleVodCount, setVisibleVodCount] = useState(60)
  const [visibleSeriesCount, setVisibleSeriesCount] = useState(60)
  const [visibleSearchCount, setVisibleSearchCount] = useState(60)

  // Reset pagination limits when categories, search, or active tab changes
  useEffect(() => {
    setVisibleLiveCount(60)
  }, [selectedLiveCat])

  useEffect(() => {
    setVisibleVodCount(60)
  }, [selectedVodCat])

  useEffect(() => {
    setVisibleSeriesCount(60)
  }, [selectedSeriesCat])

  useEffect(() => {
    setVisibleSearchCount(60)
  }, [searchQuery, showSearch])

  useEffect(() => {
    setVisibleLiveCount(60)
    setVisibleVodCount(60)
    setVisibleSeriesCount(60)
    setVisibleSearchCount(60)
  }, [activeTab])

  // Check stored credentials on mount
  useEffect(() => {
    const storedUrl = localStorage.getItem('lizzytv_server_url')
    const storedUser = localStorage.getItem('lizzytv_username')
    const storedPass = localStorage.getItem('lizzytv_password')
    const storedFavs = localStorage.getItem('lizzytv_favorites')
    const storedRecents = localStorage.getItem('lizzytv_recents')

    if (storedFavs) {
      try {
        setFavorites(JSON.parse(storedFavs))
      } catch (e) {
        console.error(e)
      }
    }

    if (storedRecents) {
      try {
        setRecentPlays(JSON.parse(storedRecents))
      } catch (e) {
        console.error(e)
      }
    }

    if (storedUrl && storedUser && storedPass) {
      setServerUrl(storedUrl)
      setUsername(storedUser)
      setPassword(storedPass)
      autoLogin(storedUrl, storedUser, storedPass)
    }
  }, [])

  // Auto-login handler
  const autoLogin = async (url: string, user: string, pass: string) => {
    setLoading(true)
    setApiError(null)
    try {
      const api = new XtreamApi(url, user, pass)
      const authInfo = await api.authenticate()
      if (authInfo.auth) {
        setAccountInfo(authInfo)
        setIsLoggedIn(true)
        loadIptvData(api)
      } else {
        setApiError('Sesión caducada o credenciales inválidas.')
        handleLogout()
      }
    } catch (err: any) {
      console.error(err)
      setApiError('Error de red al conectar automáticamente.')
      handleLogout()
    } finally {
      setLoading(false)
    }
  }

  // Load all IPTV data
  const loadIptvData = async (api: XtreamApi) => {
    try {
      const [liveCats, vodCats, seriesCats, liveList, vodList, seriesList] = await Promise.all([
        api.getLiveCategories().catch(() => [] as XtreamCategory[]),
        api.getVodCategories().catch(() => [] as XtreamCategory[]),
        api.getSeriesCategories().catch(() => [] as XtreamCategory[]),
        api.getLiveStreams().catch(() => [] as XtreamLiveChannel[]),
        api.getVodStreams().catch(() => [] as XtreamMovie[]),
        api.getSeries().catch(() => [] as XtreamSeries[])
      ])

      // Deduplicar listas para evitar claves duplicadas
      const deduplicate = <T extends { id: string }>(items: T[]): T[] => {
        return Array.from(new Map(items.map(item => [item.id, item])).values())
      }

      setLiveCategories(deduplicate(liveCats))
      setVodCategories(deduplicate(vodCats))
      setSeriesCategories(deduplicate(seriesCats))
      setChannels(deduplicate(liveList))
      setMovies(deduplicate(vodList))
      setSeries(deduplicate(seriesList))
    } catch (e) {
      console.error("Error loading IPTV content lists:", e)
    }
  }

  // Manual Login submission
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!serverUrl || !username || !password) {
      setApiError('Por favor ingresa todos los campos.')
      return
    }

    setLoading(true)
    setApiError(null)
    setShowCorsWarning(false)

    try {
      const api = new XtreamApi(serverUrl, username, password)
      const authInfo = await api.authenticate()

      if (authInfo.auth) {
        localStorage.setItem('lizzytv_server_url', serverUrl)
        localStorage.setItem('lizzytv_username', username)
        localStorage.setItem('lizzytv_password', password)

        setAccountInfo(authInfo)
        setIsLoggedIn(true)
        loadIptvData(api)
      } else {
        setApiError('Usuario o contraseña incorrectos, o cuenta inactiva.')
      }
    } catch (err: any) {
      console.error(err)
      if (err.message === 'CORS_ERROR') {
        setShowCorsWarning(true)
        setApiError('Bloqueo de CORS detectado. Tu navegador bloqueó la conexión.')
      } else {
        setApiError('No se pudo conectar al servidor. Revisa la URL y tu conexión.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Logout handler
  const handleLogout = () => {
    localStorage.removeItem('lizzytv_server_url')
    localStorage.removeItem('lizzytv_username')
    localStorage.removeItem('lizzytv_password')
    setIsLoggedIn(false)
    setAccountInfo(null)
    setChannels([])
    setMovies([])
    setSeries([])
  }

  // Clock effect
  useEffect(() => {
    const updateClock = () => {
      const now = new Date()
      const hrs = String(now.getHours()).padStart(2, '0')
      const mins = String(now.getMinutes()).padStart(2, '0')
      setCurrentTimeStr(`${hrs}:${mins}`)
    }
    updateClock()
    const interval = setInterval(updateClock, 30000)
    return () => clearInterval(interval)
  }, [])

  // Favorites Toggle
  const toggleFavorite = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const updated = favorites.includes(id) 
      ? favorites.filter(favId => favId !== id) 
      : [...favorites, id]
    setFavorites(updated)
    localStorage.setItem('lizzytv_favorites', JSON.stringify(updated))
  }

  // Video playback management
  const playVideo = (url: string, title: string, logo: string = '', category: string = '', type: 'channel' | 'movie' | 'episode' = 'channel') => {
    setPlayerError(null)
    setPlayerLoading(true)
    setIsVideoPaused(false)
    setActiveStream(url)
    setActiveStreamTitle(title)
    setIsVideoPlaying(true)

    // Prepend to recently played list
    const newRecent = {
      id: url,
      title,
      logo,
      category,
      streamUrl: url,
      type
    }
    setRecentPlays(prev => {
      const filtered = prev.filter(item => item.streamUrl !== url)
      const updated = [newRecent, ...filtered].slice(0, 10)
      localStorage.setItem('lizzytv_recents', JSON.stringify(updated))
      return updated
    })
  }

  const closeVideo = () => {
    setIsVideoPlaying(false)
    setActiveStream(null)
    setPlayerLoading(false)
    setPlayerError(null)
    setShowControls(true)
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current)
    }

    // Exit fullscreen if active
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(err => console.log("Exit fullscreen error:", err))
    }
  }

  const toggleFullscreen = () => {
    if (!playerContainerRef.current) return
    
    if (!document.fullscreenElement) {
      playerContainerRef.current.requestFullscreen().then(() => {
        setIsFullscreen(true)
      }).catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`)
      })
    } else {
      document.exitFullscreen().then(() => {
        setIsFullscreen(false)
      }).catch(err => {
        console.error(`Error attempting to exit fullscreen: ${err.message}`)
      })
    }
  }

  const handleSeriesClick = async (seriesItem: XtreamSeries) => {
    setSelectedSeriesObj(seriesItem)
    setLoadingSeriesInfo(true)
    setSelectedSeriesInfo(null)
    setSelectedSeason(1)
    try {
      const api = new XtreamApi(serverUrl, username, password)
      const info = await api.getSeriesInfo(seriesItem.id)
      setSelectedSeriesInfo(info)
      
      if (info?.seasons && info.seasons.length > 0) {
        const firstSeasonNum = info.seasons[0].season_number || 1
        setSelectedSeason(Number(firstSeasonNum))
      } else if (info?.episodes) {
        const seasons = Object.keys(info.episodes)
        if (seasons.length > 0) {
          setSelectedSeason(Number(seasons[0]))
        }
      }
    } catch (err) {
      console.error("Error loading series info:", err)
    } finally {
      setLoadingSeriesInfo(false)
    }
  }

  // Handle HLS and mpegts.js stream loading with cleanup
  useEffect(() => {
    let activeHls: Hls | null = null
    let activeMpegts: mpegts.Player | null = null

    if (isVideoPlaying && activeStream && videoRef.current) {
      const video = videoRef.current
      video.muted = isMuted

      // Caso 1: Flujo Raw .ts (MPEG-TS)
      if (activeStream.includes('.ts') && !activeStream.includes('.m3u8')) {
        if (mpegts.isSupported()) {
          const player = mpegts.createPlayer({
            type: 'mpegts',
            isLive: true,
            url: activeStream
          }, {
            enableWorker: true,
            lazyLoad: false,
            stashInitialSize: 128 * 1024
          })
          player.attachMediaElement(video)
          player.load()
          
          player.on(mpegts.Events.ERROR, (errorType, errorDetail, errorInfo) => {
            console.error("mpegts error:", errorType, errorDetail, errorInfo)
            setPlayerLoading(false)
            if (errorType === mpegts.ErrorTypes.NETWORK_ERROR) {
              setPlayerError("Error de Red / CORS al descargar flujo (.ts). Verifica que tu servidor IPTV responda o activa la extensión CORS en el navegador.")
            } else {
              setPlayerError(`Error de reproducción de stream (.ts): ${errorType} (${errorDetail})`)
            }
          })

          const playPromise = player.play()
          if (playPromise) {
            playPromise.catch((e: any) => {
              console.error("mpegts.js play error: ", e)
              setPlayerError("Error de códec o bloqueo al reproducir el flujo MPEG-TS.")
            })
          }
          activeMpegts = player
          mpegtsPlayerRef.current = player
        } else {
          // Fallback a video estándar (fallará en navegadores sin soporte TS nativo)
          video.src = activeStream
          const playPromise = video.play()
          if (playPromise) {
            playPromise.catch((e: any) => {
              console.error("Native play error: ", e)
              setPlayerError("Este navegador no soporta flujos raw MPEG-TS de forma nativa.")
            })
          }
        }
      } 
      // Caso 2: HLS (.m3u8)
      else if (activeStream.includes('.m3u8')) {
        if (Hls.isSupported()) {
          const hls = new Hls({
            enableWorker: true,
            lowLatencyMode: true
          })
          hls.loadSource(activeStream)
          hls.attachMedia(video)
          activeHls = hls
          hlsRef.current = hls
          
          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            video.play().catch(e => {
              console.log("Play failed: ", e)
              setPlayerError("La reproducción automática fue bloqueada. Haz clic en reproducir para iniciar.")
            })
          })
          
          hls.on(Hls.Events.ERROR, (_, data) => {
            console.error("HLS error:", data)
            if (data.fatal) {
              switch (data.type) {
                case Hls.ErrorTypes.NETWORK_ERROR:
                  hls.startLoad()
                  setPlayerError("Fallo de red HLS (CORS o caída). Intentando reconectar...")
                  break
                case Hls.ErrorTypes.MEDIA_ERROR:
                  hls.recoverMediaError()
                  setPlayerError("Fallo de decodificación de medios. Recuperando flujo...")
                  break
                default:
                  setPlayerError(`Error fatal del reproductor HLS: ${data.details}`)
                  closeVideo()
                  break
              }
            } else {
              if (data.details === "manifestLoadTimeOut" || data.details === "manifestLoadError") {
                setPlayerError("No se pudo cargar el manifiesto HLS. Es posible que la URL haya expirado o CORS bloquee el acceso.")
              }
            }
          })
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          video.src = activeStream
          video.addEventListener('loadedmetadata', () => {
            video.play().catch(e => console.log("Play failed: ", e))
          })
        }
      } 
      // Caso 3: Video estándar (MP4, MKV)
      else {
        video.src = activeStream
        video.play().catch(e => {
          console.log("Play failed: ", e)
          setPlayerError("El navegador no pudo reproducir el archivo de video. Comprueba el formato de codificación.")
        })
      }
    }

    return () => {
      if (activeHls) {
        try {
          activeHls.destroy()
        } catch (e) {
          console.error("Error destroying Hls instance:", e)
        }
        if (hlsRef.current === activeHls) {
          hlsRef.current = null
        }
      }
      if (activeMpegts) {
        try {
          activeMpegts.destroy()
        } catch (e) {
          console.error("Error destroying mpegts instance:", e)
        }
        if (mpegtsPlayerRef.current === activeMpegts) {
          mpegtsPlayerRef.current = null
        }
      }
      if (videoRef.current) {
        try {
          videoRef.current.removeAttribute('src')
          videoRef.current.load()
        } catch (e) {
          console.error("Error unloading video element:", e)
        }
      }
    }
  }, [isVideoPlaying, activeStream])

  // Volume toggle
  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }

  // Parental Control Handlers
  const handlePinSubmit = () => {
    if (pinInput === savedPin) {
      setParentalLocked(!parentalLocked)
      setShowPinModal(false)
      setPinInput('')
      setPinError(false)
    } else {
      setPinError(true)
      setPinInput('')
    }
  }

  const handleParentalToggleClick = () => {
    if (!parentalLocked) {
      setParentalLocked(true)
    } else {
      setShowPinModal(true)
    }
  }

  // Adults Content detection helper
  const isAdultContent = (name: string, categoryName?: string): boolean => {
    const adultKeywords = ['xxx', 'adult', '18+', 'hot', 'redlight', 'pink', 'adultos', 'for adults', 'playboy']
    const textToSearch = `${name.toLowerCase()} ${(categoryName || '').toLowerCase()}`
    return adultKeywords.some(keyword => textToSearch.includes(keyword))
  }

  // Memoized filters for content categories & search to optimize rendering performance
  const filteredChannels = useMemo(() => {
    const searchFilter = <T extends { name?: string }>(items: T[]): T[] => {
      if (!searchQuery) return items
      const query = searchQuery.toLowerCase()
      return items.filter(item => (item.name || '').toLowerCase().includes(query))
    }

    const adultFiltered = channels.filter(c => {
      const cat = liveCategories.find(catItem => catItem.id === c.categoryId)
      const adult = isAdultContent(c.name, cat?.name || '')
      return !(parentalLocked && adult)
    })

    const catFiltered = adultFiltered.filter(c => selectedLiveCat === 'all' || c.categoryId === selectedLiveCat)
    
    return searchFilter(catFiltered)
  }, [channels, liveCategories, selectedLiveCat, searchQuery, parentalLocked])

  const filteredMovies = useMemo(() => {
    const searchFilter = <T extends { title?: string }>(items: T[]): T[] => {
      if (!searchQuery) return items
      const query = searchQuery.toLowerCase()
      return items.filter(item => (item.title || '').toLowerCase().includes(query))
    }

    const adultFiltered = movies.filter(m => {
      const cat = vodCategories.find(catItem => catItem.id === m.categoryId)
      const adult = isAdultContent(m.title, cat?.name || '')
      return !(parentalLocked && adult)
    })

    const catFiltered = adultFiltered.filter(m => selectedVodCat === 'all' || m.categoryId === selectedVodCat)
    
    return searchFilter(catFiltered)
  }, [movies, vodCategories, selectedVodCat, searchQuery, parentalLocked])

  const filteredSeries = useMemo(() => {
    const searchFilter = <T extends { title?: string }>(items: T[]): T[] => {
      if (!searchQuery) return items
      const query = searchQuery.toLowerCase()
      return items.filter(item => (item.title || '').toLowerCase().includes(query))
    }

    const adultFiltered = series.filter(s => {
      const cat = seriesCategories.find(catItem => catItem.id === s.categoryId)
      const adult = isAdultContent(s.title, cat?.name || '')
      return !(parentalLocked && adult)
    })

    const catFiltered = adultFiltered.filter(s => selectedSeriesCat === 'all' || s.categoryId === selectedSeriesCat)
    
    return searchFilter(catFiltered)
  }, [series, seriesCategories, selectedSeriesCat, searchQuery, parentalLocked])

  // Favorites Shape adapter
  const favoriteItems = useMemo(() => {
    return [
      ...channels.map(c => {
        const cat = liveCategories.find(catItem => catItem.id === c.categoryId)
        return { id: c.id, title: c.name, poster: c.logo, category: cat?.name || 'Canal TV', streamUrl: c.streamUrl, type: 'channel' as const, isAdult: isAdultContent(c.name, cat?.name) }
      }),
      ...movies.map(m => {
        const cat = vodCategories.find(catItem => catItem.id === m.categoryId)
        return { id: m.id, title: m.title, poster: m.logo, category: cat?.name || 'Película', streamUrl: m.streamUrl, type: 'movie' as const, isAdult: isAdultContent(m.title, cat?.name) }
      }),
      ...series.map(s => {
        const cat = seriesCategories.find(catItem => catItem.id === s.categoryId)
        return { id: s.id, title: s.title, poster: s.logo, category: cat?.name || 'Serie', streamUrl: '', type: 'series' as const, isAdult: isAdultContent(s.title, cat?.name) }
      })
    ].filter(item => favorites.includes(item.id))
  }, [channels, liveCategories, movies, vodCategories, series, seriesCategories, favorites])

  const filteredFavorites = useMemo(() => {
    const searchFilter = <T extends { title?: string }>(items: T[]): T[] => {
      if (!searchQuery) return items
      const query = searchQuery.toLowerCase()
      return items.filter(item => (item.title || '').toLowerCase().includes(query))
    }
    return searchFilter(
      favoriteItems.filter(item => !parentalLocked || !item.isAdult)
    )
  }, [favoriteItems, searchQuery, parentalLocked])

  // Featured Movie from the real VOD list
  const realFeaturedMovie: XtreamMovie | null = useMemo(() => {
    return filteredMovies.length > 0 ? filteredMovies[0] : null
  }, [filteredMovies])

  // 1. RENDER LOGIN SCREEN (IF NOT LOGGED IN)
  if (!isLoggedIn) {
    return (
      <div className="flex h-screen w-screen bg-bg-obsidian items-center justify-center overflow-auto px-4 relative select-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-purple/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-900/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="w-full max-w-lg bg-bg-card border border-white/5 rounded-3xl p-8 shadow-2xl relative z-10 my-8">
          <div className="flex flex-col items-center gap-3 mb-6 select-none">
            <img 
              src="/lizzytv_logo.png" 
              alt="LizzyTV Logo" 
              className="w-28 h-28 rounded-full border border-white/10 shadow-glow-hover object-cover animate-fade-in"
            />
            <div className="text-center flex flex-col gap-1">
              <span className="text-2xl font-black tracking-widest bg-gradient-to-r from-brand-purple to-purple-400 bg-clip-text text-transparent">
                LIZZYTV
              </span>
              <span className="text-[10px] uppercase font-bold text-brand-neon bg-brand-purple/15 px-3 py-0.5 rounded-full border border-brand-purple/10 self-center">
                IPTV Client
              </span>
            </div>
          </div>

          <form onSubmit={handleLoginSubmit} className="flex flex-col gap-5">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wide flex items-center gap-1.5">
                <Globe className="w-4 h-4 text-brand-neon" />
                URL del Servidor IPTV
              </label>
              <input 
                type="url" 
                placeholder="http://proveedor-iptv.com:8080" 
                value={serverUrl}
                onChange={(e) => setServerUrl(e.target.value)}
                disabled={loading}
                className="w-full bg-black/35 border border-white/10 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:border-brand-purple/60 text-white placeholder-gray-500"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wide flex items-center gap-1.5">
                <User className="w-4 h-4 text-brand-neon" />
                Nombre de Usuario
              </label>
              <input 
                type="text" 
                placeholder="Ingresa tu usuario" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                className="w-full bg-black/35 border border-white/10 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:border-brand-purple/60 text-white placeholder-gray-500"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-400 uppercase tracking-wide flex items-center gap-1.5">
                <Key className="w-4 h-4 text-brand-neon" />
                Contraseña
              </label>
              <input 
                type="password" 
                placeholder="Ingresa tu contraseña" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="w-full bg-black/35 border border-white/10 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:border-brand-purple/60 text-white placeholder-gray-500"
              />
            </div>

            {apiError && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 flex gap-3 items-start text-xs text-red-400 mt-2">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold">Error de Autenticación</p>
                  <p className="mt-1 opacity-90">{apiError}</p>
                </div>
              </div>
            )}

            {showCorsWarning && (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-4 flex gap-3 items-start text-xs text-yellow-400 mt-2">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold">¿Cómo solucionar el bloqueo por CORS?</p>
                  <p className="mt-1 opacity-95">
                    Como estás probando la app en el navegador local (`localhost`), tu navegador bloquea la llamada al servidor IPTV por seguridad.
                  </p>
                  <p className="mt-2 font-bold text-white">Solución rápida:</p>
                  <ul className="list-disc list-inside mt-1 space-y-1 opacity-90">
                    <li>Instala la extensión de Chrome llamada <span className="underline font-bold text-white">"Allow CORS: Access-Control-Allow-Origin"</span> en tu navegador.</li>
                    <li>Actívala haciendo clic en su icono (se pondrá en verde).</li>
                    <li>Vuelve a hacer clic en "Conectar".</li>
                  </ul>
                  <p className="mt-3 text-[10px] text-gray-400">Nota: Al instalarse en celulares o televisiones como app local, este problema no ocurrirá.</p>
                </div>
              </div>
            )}

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-brand-purple hover:bg-brand-purple-dark text-white font-bold py-3.5 rounded-2xl cursor-pointer shadow-glow-hover transition-all duration-200 mt-4 flex items-center justify-center disabled:bg-gray-700 disabled:cursor-not-allowed text-sm"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                'Conectar con el Servidor'
              )}
            </button>
          </form>
        </div>
      </div>
    )
  }

  // 2. RENDER MAIN IPTV DASHBOARD (IF LOGGED IN)
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-bg-obsidian text-gray-100 select-none">
      
      {/* LEFT SIDEBAR */}
      <aside className="w-24 md:w-28 flex flex-col items-center justify-between py-8 glass-panel z-20 shrink-0 border-r border-white/5">
        <div className="flex flex-col items-center gap-1.5 select-none">
          <img 
            src="/lizzytv_logo.png" 
            alt="LizzyTV" 
            className="w-12 h-12 rounded-full border border-white/10 shadow-glow-hover object-cover"
          />
          <div className="flex flex-col items-center">
            <span className="text-xs font-extrabold tracking-wider bg-gradient-to-r from-brand-purple to-purple-400 bg-clip-text text-transparent">
              Lizzy
            </span>
            <span className="text-[9px] font-bold text-brand-neon bg-brand-purple/20 px-2 py-0.2 rounded-full">
              TV
            </span>
          </div>
        </div>

        <nav className="flex flex-col gap-6 w-full px-2">
          <button 
            onClick={() => { setActiveTab('home'); setShowSearch(false) }}
            className={`tv-focusable py-3 rounded-2xl flex flex-col items-center justify-center gap-1 border border-transparent ${activeTab === 'home' && !showSearch ? 'bg-brand-purple/10 text-brand-neon border-brand-purple/30' : 'text-gray-400 hover:text-white'}`}
          >
            <Home className="w-5 h-5 md:w-6 md:h-6" />
            <span className="text-[9px] md:text-[10px] font-medium uppercase tracking-wider">Inicio</span>
          </button>
          
          <button 
            onClick={() => { setActiveTab('live'); setShowSearch(false) }}
            className={`tv-focusable py-3 rounded-2xl flex flex-col items-center justify-center gap-1 border border-transparent ${activeTab === 'live' && !showSearch ? 'bg-brand-purple/10 text-brand-neon border-brand-purple/30' : 'text-gray-400 hover:text-white'}`}
          >
            <Tv className="w-5 h-5 md:w-6 md:h-6" />
            <span className="text-[9px] md:text-[10px] font-medium uppercase tracking-wider">En Vivo</span>
          </button>

          <button 
            onClick={() => { setActiveTab('movies'); setShowSearch(false) }}
            className={`tv-focusable py-3 rounded-2xl flex flex-col items-center justify-center gap-1 border border-transparent ${activeTab === 'movies' && !showSearch ? 'bg-brand-purple/10 text-brand-neon border-brand-purple/30' : 'text-gray-400 hover:text-white'}`}
          >
            <Film className="w-5 h-5 md:w-6 md:h-6" />
            <span className="text-[9px] md:text-[10px] font-medium uppercase tracking-wider">Cine</span>
          </button>

          <button 
            onClick={() => { setActiveTab('series'); setShowSearch(false) }}
            className={`tv-focusable py-3 rounded-2xl flex flex-col items-center justify-center gap-1 border border-transparent ${activeTab === 'series' && !showSearch ? 'bg-brand-purple/10 text-brand-neon border-brand-purple/30' : 'text-gray-400 hover:text-white'}`}
          >
            <Clapperboard className="w-5 h-5 md:w-6 md:h-6" />
            <span className="text-[9px] md:text-[10px] font-medium uppercase tracking-wider">Series</span>
          </button>

          <button 
            onClick={() => { setActiveTab('settings'); setShowSearch(false) }}
            className={`tv-focusable py-3 rounded-2xl flex flex-col items-center justify-center gap-1 border border-transparent ${activeTab === 'settings' && !showSearch ? 'bg-brand-purple/10 text-brand-neon border-brand-purple/30' : 'text-gray-400 hover:text-white'}`}
          >
            <Settings className="w-5 h-5 md:w-6 md:h-6" />
            <span className="text-[9px] md:text-[10px] font-medium uppercase tracking-wider">Ajustes</span>
          </button>
        </nav>

        <button 
          onClick={handleParentalToggleClick}
          className={`tv-focusable w-12 h-12 rounded-full flex items-center justify-center border transition-all ${parentalLocked ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-green-500/10 border-green-500/30 text-green-400'}`}
        >
          {parentalLocked ? <Lock className="w-5 h-5" /> : <Unlock className="w-5 h-5" />}
        </button>
      </aside>

      {/* MAIN VIEWPORT */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        
        {/* HEADER */}
        <header className="h-16 shrink-0 flex items-center justify-between px-8 bg-gradient-to-b from-bg-obsidian to-transparent z-10">
          <div className="flex items-center gap-4">
            <h1 className="text-xl md:text-2xl font-bold tracking-tight capitalize">
              {showSearch ? 'Buscador' : activeTab === 'home' ? 'Inicio' : activeTab === 'live' ? 'Canales En Vivo' : activeTab === 'movies' ? 'Películas VOD' : activeTab === 'series' ? 'Series' : 'Configuración'}
            </h1>
            
            <div className="relative flex items-center">
              <button 
                onClick={() => setShowSearch(!showSearch)}
                className={`tv-focusable p-2 rounded-xl border border-transparent bg-white/5 hover:bg-white/10 ${showSearch ? 'border-brand-purple/30 text-brand-neon bg-brand-purple/10' : 'text-gray-300'}`}
              >
                <Search className="w-5 h-5" />
              </button>
              {showSearch && (
                <input 
                  type="text" 
                  placeholder="Buscar canales, películas..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="ml-2 w-48 md:w-64 bg-white/5 border border-white/10 rounded-xl px-4 py-1.5 text-sm focus:outline-none focus:border-brand-purple/50 text-white placeholder-gray-400"
                  autoFocus
                />
              )}
            </div>
          </div>

          <div className="flex items-center gap-6">
            <span className="text-base font-semibold tracking-wider text-gray-200">
              {currentTimeStr}
            </span>
            <div className="flex items-center gap-2">
              <img 
                src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=60" 
                alt="Profile" 
                className="w-8 h-8 rounded-full border-2 border-brand-purple/40"
              />
              <span className="text-xs md:text-sm font-semibold text-gray-200">
                {accountInfo?.username || 'Invitado'}
              </span>
            </div>
          </div>
        </header>

        {/* CONTAINER CONTENT */}
        <div className="flex-1 overflow-y-auto no-scrollbar pb-12 px-8 -mt-16 pt-16">
          
          {/* SEARCH MODE */}
          {showSearch ? (
            <div className="mt-6 flex flex-col gap-8">
              {searchQuery ? (
                <>
                  <p className="text-sm text-gray-400">Resultados para: <span className="text-brand-neon font-semibold">"{searchQuery}"</span></p>
                  
                  {/* Real Live Channels search */}
                  {filteredChannels.length > 0 && (
                    <div>
                      <h2 className="text-base font-bold uppercase tracking-wider text-gray-400 mb-4">Canales en Vivo ({filteredChannels.length})</h2>
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                        {filteredChannels.slice(0, visibleSearchCount).map(channel => (
                          <div 
                            key={`search-channel-${channel.id}`}
                            onClick={() => playVideo(channel.streamUrl, channel.name, channel.logo, 'Canal en Vivo', 'channel')}
                            className="tv-focusable cursor-pointer bg-bg-card border border-white/5 rounded-2xl p-4 flex flex-col items-center gap-3 hover:border-brand-purple/30 group"
                          >
                            <ChannelLogo src={channel.logo} name={channel.name} />
                            <span className="text-xs font-semibold text-center truncate w-full text-white">{channel.name}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Real Movies search */}
                  {filteredMovies.length > 0 && (
                    <div>
                      <h2 className="text-base font-bold uppercase tracking-wider text-gray-400 mb-4">Películas ({filteredMovies.length})</h2>
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                        {filteredMovies.slice(0, visibleSearchCount).map(movie => (
                          <div 
                            key={`search-movie-${movie.id}`}
                            onClick={() => playVideo(movie.streamUrl, movie.title, movie.logo, 'Película', 'movie')}
                            className="tv-focusable cursor-pointer relative rounded-2xl overflow-hidden aspect-[2/3] group border border-white/5"
                          >
                            <MoviePoster src={movie.logo} title={movie.title} category={movie.categoryId} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent opacity-0 group-hover:opacity-100 flex flex-col justify-end p-3 transition-all">
                              <span className="text-xs font-bold text-white truncate">{movie.title}</span>
                              <span className="text-[10px] text-brand-neon font-semibold mt-0.5">Rating: ⭐{movie.rating}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Real Series search */}
                  {filteredSeries.length > 0 && (
                    <div>
                      <h2 className="text-base font-bold uppercase tracking-wider text-gray-400 mb-4">Series ({filteredSeries.length})</h2>
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
                        {filteredSeries.slice(0, visibleSearchCount).map(s => (
                          <div 
                            key={`search-series-${s.id}`}
                            onClick={() => handleSeriesClick(s)}
                            className="tv-focusable cursor-pointer relative rounded-2xl overflow-hidden aspect-[2/3] group border border-white/5"
                          >
                            <MoviePoster src={s.logo} title={s.title} category={s.categoryId} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent opacity-0 group-hover:opacity-100 flex flex-col justify-end p-3 transition-all">
                              <span className="text-xs font-bold text-white truncate">{s.title}</span>
                              <span className="text-[10px] text-brand-neon font-semibold mt-0.5">Rating: ⭐{s.rating}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(filteredChannels.length > visibleSearchCount || filteredMovies.length > visibleSearchCount || filteredSeries.length > visibleSearchCount) && (
                    <div className="flex justify-center mt-6">
                      <button 
                        onClick={() => setVisibleSearchCount(prev => prev + 60)}
                        className="tv-focusable bg-white/5 border border-white/10 text-brand-neon hover:text-white font-bold px-8 py-3 rounded-2xl text-sm transition-all hover:bg-brand-purple hover:border-brand-purple shadow-glow-hover"
                      >
                        Cargar más resultados
                      </button>
                    </div>
                  )}

                  {filteredChannels.length === 0 && filteredMovies.length === 0 && filteredSeries.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                      <ShieldAlert className="w-12 h-12 mb-3 text-gray-600 animate-pulse" />
                      <p className="text-base font-semibold">No se encontraron resultados en tu catálogo.</p>
                      <p className="text-xs text-gray-600 mt-1">Verifica las mayúsculas o desbloquea el control parental.</p>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                  <Search className="w-12 h-12 mb-3 text-gray-600" />
                  <p className="text-base font-semibold">Escribe el término de búsqueda arriba.</p>
                </div>
              )}
            </div>
          ) : (
            <>
              {/* HOME VIEW */}
              {activeTab === 'home' && (
                <div className="flex flex-col gap-8">
                  
                  {/* Dynamic Featured Hero Movie */}
                  {realFeaturedMovie ? (
                    <section className="relative w-full aspect-[21/9] rounded-3xl overflow-hidden mt-4 group border border-white/5">
                      <img 
                        src={realFeaturedMovie.logo} 
                        alt={realFeaturedMovie.title} 
                        className="absolute inset-0 w-full h-full object-cover object-[center_25%]"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1618336753974-aae8e04506aa?w=1200&auto=format&fit=crop&q=80'
                        }}
                      />
                      <div className="absolute inset-0 banner-overlay-side z-0" />
                      <div className="absolute inset-0 banner-overlay z-0" />

                      <div className="absolute left-12 bottom-8 z-10 max-w-xl flex flex-col gap-3">
                        <span className="text-xs font-bold uppercase tracking-widest text-brand-neon bg-brand-purple/30 px-2 py-0.5 rounded-md w-fit">Película Recomendada</span>
                        <h2 className="text-3xl md:text-5xl font-black tracking-tight leading-none text-white font-sans truncate">
                          {realFeaturedMovie.title}
                        </h2>
                        <div className="flex items-center gap-3 text-xs md:text-sm font-semibold text-gray-300">
                          <span className="text-brand-neon">Año: {realFeaturedMovie.year || 'N/A'}</span>
                          <span>•</span>
                          <span className="bg-white/10 px-2 py-0.5 rounded text-[10px] uppercase">{realFeaturedMovie.container}</span>
                          <span>•</span>
                          <span>⭐ {realFeaturedMovie.rating}</span>
                        </div>
                        <p className="text-xs md:text-sm leading-relaxed text-gray-300 font-light line-clamp-3">
                          Disfruta de este largometraje directo de tu catálogo privado. Haz clic en reproducir para iniciar la carga instantánea.
                        </p>

                        <div className="flex items-center gap-4 mt-2">
                          <button 
                            onClick={() => playVideo(realFeaturedMovie.streamUrl, realFeaturedMovie.title, realFeaturedMovie.logo, 'Película Recomendada', 'movie')}
                            className="tv-focusable bg-brand-purple hover:bg-brand-purple-dark text-white px-6 py-2.5 rounded-xl font-bold flex items-center gap-2 cursor-pointer shadow-glow-hover text-sm"
                          >
                            <Play className="w-4 h-4 fill-white" />
                            Reproducir Película
                          </button>
                          <button 
                            onClick={(e) => toggleFavorite(realFeaturedMovie.id, e)}
                            className="tv-focusable bg-white/10 hover:bg-white/15 text-white px-4 py-2.5 rounded-xl font-bold flex items-center gap-2 cursor-pointer text-sm border border-white/5"
                          >
                            <Heart className={`w-4 h-4 ${favorites.includes(realFeaturedMovie.id) ? 'fill-red-500 text-red-500' : 'text-white'}`} />
                            {favorites.includes(realFeaturedMovie.id) ? 'En Favoritos' : 'Añadir'}
                          </button>
                        </div>
                      </div>
                    </section>
                  ) : (
                    <section className="relative w-full aspect-[21/9] bg-gradient-to-br from-purple-950/40 to-bg-obsidian rounded-3xl overflow-hidden mt-4 border border-white/5 flex items-center justify-center">
                      <div className="text-center flex flex-col items-center gap-2 px-6">
                        <div className="w-12 h-12 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-neon animate-pulse">
                          <Tv className="w-6 h-6" />
                        </div>
                        <h3 className="text-lg font-bold">Cargando catálogo IPTV...</h3>
                        <p className="text-xs text-gray-400">Si tarda mucho, comprueba que activaste la extensión CORS en el navegador.</p>
                      </div>
                    </section>
                  )}

                  {/* RECENT PLAYS ROW */}
                  {recentPlays.length > 0 && (
                    <section className="flex flex-col gap-3 animate-fade-in">
                      <h2 className="text-base font-bold uppercase tracking-wider text-gray-400">Vistos Recientemente</h2>
                      <div className="flex gap-4 overflow-x-auto no-scrollbar py-2">
                        {recentPlays.map(item => (
                          <div 
                            key={`recent-item-${item.id}`}
                            onClick={() => playVideo(item.streamUrl, item.title, item.logo, item.category, item.type)}
                            className="tv-focusable relative shrink-0 w-28 md:w-36 aspect-[2/3] rounded-2xl overflow-hidden border border-white/5 cursor-pointer group shadow-md"
                          >
                            <MoviePoster src={item.logo} title={item.title} category={item.category} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent flex flex-col justify-end p-3">
                              <span className="text-[10px] md:text-xs font-bold truncate text-white">{item.title}</span>
                              <span className="text-[8px] md:text-[9px] text-brand-neon font-semibold uppercase mt-0.5">{item.category}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                  {/* FAVORITES ROW */}
                  {filteredFavorites.length > 0 && (
                    <section className="flex flex-col gap-3">
                      <h2 className="text-base font-bold uppercase tracking-wider text-gray-400">Mis Favoritos</h2>
                      <div className="flex gap-4 overflow-x-auto no-scrollbar py-2">
                        {filteredFavorites.map(item => (
                          <div 
                            key={`fav-item-${item.id}`}
                            onClick={() => {
                              if (item.type === 'series') {
                                handleSeriesClick({ id: item.id, title: item.title, logo: item.poster, categoryId: '', rating: '', year: '' })
                              } else {
                                playVideo(item.streamUrl, item.title, item.poster, item.category, item.type)
                              }
                            }}
                            className="tv-focusable relative shrink-0 w-28 md:w-36 aspect-[2/3] rounded-2xl overflow-hidden border border-white/5 cursor-pointer group shadow-md"
                          >
                            <MoviePoster src={item.poster} title={item.title} category={item.category} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent flex flex-col justify-end p-3">
                              <span className="text-[10px] md:text-xs font-bold truncate text-white">{item.title}</span>
                              <span className="text-[8px] md:text-[9px] text-brand-neon font-semibold uppercase mt-0.5">{item.category}</span>
                            </div>
                            <button 
                              onClick={(e) => toggleFavorite(item.id, e)}
                              className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full border border-white/10 text-red-500"
                            >
                              <Heart className="w-3.5 h-3.5 fill-red-500" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                  {/* REAL LIVE CHANNELS ROW */}
                  {filteredChannels.length > 0 && (
                    <section className="flex flex-col gap-3">
                      <div className="flex items-center justify-between">
                        <h2 className="text-base font-bold uppercase tracking-wider text-gray-400">Canales de TV Recientes</h2>
                        <button onClick={() => setActiveTab('live')} className="text-xs font-bold text-brand-neon hover:underline">Ver Todo</button>
                      </div>
                      <div className="flex gap-4 overflow-x-auto no-scrollbar py-2">
                        {filteredChannels.slice(0, 7).map(channel => (
                          <div 
                            key={`home-channel-${channel.id}`}
                            onClick={() => playVideo(channel.streamUrl, channel.name, channel.logo, 'Canal en Vivo', 'channel')}
                            className="tv-focusable relative shrink-0 w-32 md:w-40 aspect-[4/3] bg-bg-card border border-white/5 rounded-2xl p-4 flex flex-col items-center justify-between cursor-pointer group hover:border-brand-purple/30 shadow-md"
                          >
                            <ChannelLogo src={channel.logo} name={channel.name} />
                            <div className="flex flex-col items-center w-full gap-0.5">
                              <span className="text-xs font-bold text-white truncate w-full text-center">{channel.name}</span>
                              <span className="text-[9px] text-brand-neon truncate w-full text-center font-medium mt-0.5">Canal En Vivo</span>
                            </div>
                            <span className="absolute top-2 left-2 text-[8px] bg-red-600 text-white font-bold uppercase px-1.5 py-0.5 rounded-full">LIVE</span>
                            
                            <button 
                              onClick={(e) => toggleFavorite(channel.id, e)}
                              className="absolute top-2 right-2 p-1.5 bg-black/40 rounded-full border border-white/5 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
                            >
                              <Heart className={`w-3 h-3 ${favorites.includes(channel.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                  {/* REAL MOVIES VOD ROW */}
                  {filteredMovies.length > 0 && (
                    <section className="flex flex-col gap-3">
                      <div className="flex items-center justify-between">
                        <h2 className="text-base font-bold uppercase tracking-wider text-gray-400">Películas en Tendencia</h2>
                        <button onClick={() => setActiveTab('movies')} className="text-xs font-bold text-brand-neon hover:underline">Ver Todo</button>
                      </div>
                      <div className="flex gap-4 overflow-x-auto no-scrollbar py-2">
                        {filteredMovies.slice(1, 8).map(movie => (
                          <div 
                            key={`home-movie-${movie.id}`}
                            onClick={() => playVideo(movie.streamUrl, movie.title, movie.logo, 'Película', 'movie')}
                            className="tv-focusable relative shrink-0 w-28 md:w-36 aspect-[2/3] rounded-2xl overflow-hidden border border-white/5 cursor-pointer group shadow-md"
                          >
                            <MoviePoster src={movie.logo} title={movie.title} category={movie.categoryId} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent flex flex-col justify-end p-3 opacity-100 md:opacity-0 group-hover:opacity-100 transition-all">
                              <span className="text-xs font-bold truncate text-white">{movie.title}</span>
                              <div className="flex items-center gap-1.5 text-[8px] text-gray-300 mt-1">
                                <span>{movie.year || 'VOD'}</span>
                                <span>•</span>
                                <span>⭐ {movie.rating}</span>
                              </div>
                            </div>
                            <button 
                              onClick={(e) => toggleFavorite(movie.id, e)}
                              className="absolute top-2 right-2 p-1.5 bg-black/40 rounded-full border border-white/5 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
                            >
                              <Heart className={`w-3 h-3 ${favorites.includes(movie.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                  {/* REAL SERIES ROW */}
                  {filteredSeries.length > 0 && (
                    <section className="flex flex-col gap-3">
                      <div className="flex items-center justify-between">
                        <h2 className="text-base font-bold uppercase tracking-wider text-gray-400">Series en Tendencia</h2>
                        <button onClick={() => setActiveTab('series')} className="text-xs font-bold text-brand-neon hover:underline">Ver Todo</button>
                      </div>
                      <div className="flex gap-4 overflow-x-auto no-scrollbar py-2">
                        {filteredSeries.slice(0, 7).map(s => (
                          <div 
                            key={`home-series-${s.id}`}
                            onClick={() => handleSeriesClick(s)}
                            className="tv-focusable relative shrink-0 w-28 md:w-36 aspect-[2/3] rounded-2xl overflow-hidden border border-white/5 cursor-pointer group shadow-md"
                          >
                            <MoviePoster src={s.logo} title={s.title} category={s.categoryId} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent flex flex-col justify-end p-3 opacity-100 md:opacity-0 group-hover:opacity-100 transition-all">
                              <span className="text-xs font-bold truncate text-white">{s.title}</span>
                              <div className="flex items-center gap-1.5 text-[8px] text-gray-300 mt-1">
                                <span>{s.year || 'Serie'}</span>
                                <span>•</span>
                                <span>⭐ {s.rating}</span>
                              </div>
                            </div>
                            <button 
                              onClick={(e) => toggleFavorite(s.id, e)}
                              className="absolute top-2 right-2 p-1.5 bg-black/40 rounded-full border border-white/5 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
                            >
                              <Heart className={`w-3 h-3 ${favorites.includes(s.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}
                </div>
              )}

              {/* LIVE TV CHANNELS PAGE */}
              {activeTab === 'live' && (
                <div className="mt-6 flex flex-col gap-6">
                  {/* Category filters */}
                  <div className="flex gap-3 overflow-x-auto no-scrollbar py-1">
                    <button 
                      onClick={() => setSelectedLiveCat('all')}
                      className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all ${selectedLiveCat === 'all' ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                    >
                      Todos los Canales
                    </button>
                    {liveCategories.map(cat => (
                      <button 
                        key={`live-cat-btn-${cat.id}`}
                        onClick={() => setSelectedLiveCat(cat.id)}
                        className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all whitespace-nowrap ${selectedLiveCat === cat.id ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                      >
                        {cat.name}
                      </button>
                    ))}
                  </div>

                  {/* Channels grid */}
                  {filteredChannels.length > 0 ? (
                    <div className="flex flex-col gap-6">
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-6">
                        {filteredChannels.slice(0, visibleLiveCount).map(channel => (
                          <div 
                            key={`live-channel-page-${channel.id}`}
                            onClick={() => playVideo(channel.streamUrl, channel.name, channel.logo, 'Canal en Vivo', 'channel')}
                            className="tv-focusable relative bg-bg-card border border-white/5 rounded-3xl p-5 flex flex-col items-center justify-between cursor-pointer group hover:border-brand-purple/30 shadow-lg"
                          >
                            <ChannelLogo src={channel.logo} name={channel.name} />
                            <div className="flex flex-col items-center w-full gap-0.5 mt-4">
                              <span className="text-sm font-bold text-white truncate w-full text-center">{channel.name}</span>
                              <span className="text-[10px] text-brand-neon truncate w-full text-center font-medium mt-0.5">Canal En Vivo</span>
                            </div>

                            <span className="absolute top-3 left-3 text-[9px] bg-red-600 text-white font-bold uppercase px-2 py-0.5 rounded-full">LIVE</span>
                            
                            <button 
                              onClick={(e) => toggleFavorite(channel.id, e)}
                              className="absolute top-3 right-3 p-1.5 bg-black/40 rounded-full border border-white/5 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
                            >
                              <Heart className={`w-3.5 h-3.5 ${favorites.includes(channel.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
                            </button>
                          </div>
                        ))}
                      </div>
                      
                      {filteredChannels.length > visibleLiveCount && (
                        <div className="flex justify-center mt-4">
                          <button 
                            onClick={() => setVisibleLiveCount(prev => prev + 60)}
                            className="tv-focusable bg-white/5 border border-white/10 text-brand-neon hover:text-white font-bold px-8 py-3 rounded-2xl text-sm transition-all hover:bg-brand-purple hover:border-brand-purple shadow-glow-hover"
                          >
                            Cargar más canales ({filteredChannels.length - visibleLiveCount} restantes)
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                      <ShieldAlert className="w-12 h-12 mb-3 text-gray-600" />
                      <p className="text-base font-semibold">No hay canales disponibles en esta categoría.</p>
                    </div>
                  )}
                </div>
              )}

              {/* MOVIES VOD PAGE */}
              {activeTab === 'movies' && (
                <div className="mt-6 flex flex-col gap-6">
                  {/* Category filters */}
                  <div className="flex gap-3 overflow-x-auto no-scrollbar py-1">
                    <button 
                      onClick={() => setSelectedVodCat('all')}
                      className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all ${selectedVodCat === 'all' ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                    >
                      Todas las Películas
                    </button>
                    {vodCategories.map(cat => (
                      <button 
                        key={`vod-cat-btn-${cat.id}`}
                        onClick={() => setSelectedVodCat(cat.id)}
                        className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all whitespace-nowrap ${selectedVodCat === cat.id ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                      >
                        {cat.name}
                      </button>
                    ))}
                  </div>

                  {/* Movies grid */}
                  {filteredMovies.length > 0 ? (
                    <div className="flex flex-col gap-6">
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-6">
                        {filteredMovies.slice(0, visibleVodCount).map(movie => (
                          <div 
                            key={`movie-page-${movie.id}`}
                            onClick={() => playVideo(movie.streamUrl, movie.title, movie.logo, 'Película', 'movie')}
                            className="tv-focusable relative rounded-3xl overflow-hidden aspect-[2/3] border border-white/5 cursor-pointer group shadow-lg"
                          >
                            <MoviePoster src={movie.logo} title={movie.title} category={movie.categoryId} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent flex flex-col justify-end p-4">
                              <span className="text-sm font-bold truncate text-white">{movie.title}</span>
                              <div className="flex items-center gap-1.5 text-xs text-gray-300 mt-1.5">
                                <span>{movie.year || 'VOD'}</span>
                                <span>•</span>
                                <span>⭐ {movie.rating}</span>
                              </div>
                            </div>

                            <button 
                              onClick={(e) => toggleFavorite(movie.id, e)}
                              className="absolute top-3 right-3 p-1.5 bg-black/40 rounded-full border border-white/5 text-gray-400 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
                            >
                              <Heart className={`w-3.5 h-3.5 ${favorites.includes(movie.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
                            </button>
                          </div>
                        ))}
                      </div>
                      
                      {filteredMovies.length > visibleVodCount && (
                        <div className="flex justify-center mt-4">
                          <button 
                            onClick={() => setVisibleVodCount(prev => prev + 60)}
                            className="tv-focusable bg-white/5 border border-white/10 text-brand-neon hover:text-white font-bold px-8 py-3 rounded-2xl text-sm transition-all hover:bg-brand-purple hover:border-brand-purple shadow-glow-hover"
                          >
                            Cargar más películas ({filteredMovies.length - visibleVodCount} restantes)
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                      <ShieldAlert className="w-12 h-12 mb-3 text-gray-600" />
                      <p className="text-base font-semibold">No hay películas disponibles en esta categoría.</p>
                    </div>
                  )}
                </div>
              )}

              {/* SERIES PAGE */}
              {activeTab === 'series' && (
                <div className="mt-6 flex flex-col gap-6">
                  {/* Category filters */}
                  <div className="flex gap-3 overflow-x-auto no-scrollbar py-1">
                    <button 
                      onClick={() => setSelectedSeriesCat('all')}
                      className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all ${selectedSeriesCat === 'all' ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                    >
                      Todas las Series
                    </button>
                    {seriesCategories.map(cat => (
                      <button 
                        key={`series-cat-btn-${cat.id}`}
                        onClick={() => setSelectedSeriesCat(cat.id)}
                        className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all whitespace-nowrap ${selectedSeriesCat === cat.id ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                      >
                        {cat.name}
                      </button>
                    ))}
                  </div>

                  {/* Series grid */}
                  {filteredSeries.length > 0 ? (
                    <div className="flex flex-col gap-6">
                      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-6">
                        {filteredSeries.slice(0, visibleSeriesCount).map(s => (
                          <div 
                            key={`series-page-${s.id}`}
                            onClick={() => handleSeriesClick(s)}
                            className="tv-focusable cursor-pointer relative rounded-3xl overflow-hidden aspect-[2/3] border border-white/5 group shadow-lg"
                          >
                            <MoviePoster src={s.logo} title={s.title} category={s.categoryId} />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent flex flex-col justify-end p-4">
                              <span className="text-sm font-bold truncate text-white">{s.title}</span>
                              <div className="flex items-center gap-1.5 text-xs text-gray-300 mt-1.5">
                                <span>{s.year || 'Serie'}</span>
                                <span>•</span>
                                <span>⭐ {s.rating}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {filteredSeries.length > visibleSeriesCount && (
                        <div className="flex justify-center mt-4">
                          <button 
                            onClick={() => setVisibleSeriesCount(prev => prev + 60)}
                            className="tv-focusable bg-white/5 border border-white/10 text-brand-neon hover:text-white font-bold px-8 py-3 rounded-2xl text-sm transition-all hover:bg-brand-purple hover:border-brand-purple shadow-glow-hover"
                          >
                            Cargar más series ({filteredSeries.length - visibleSeriesCount} restantes)
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-20 text-gray-500">
                      <ShieldAlert className="w-12 h-12 mb-3 text-gray-600" />
                      <p className="text-base font-semibold">No hay series disponibles en esta categoría.</p>
                    </div>
                  )}
                </div>
              )}

              {/* ADJUSTMENTS & CONFIGURATION PAGE */}
              {activeTab === 'settings' && (
                <div className="mt-6 max-w-2xl bg-bg-card border border-white/5 rounded-3xl p-8 flex flex-col gap-6 shadow-xl">
                  <h2 className="text-lg font-bold border-b border-white/5 pb-3">Ajustes Generales</h2>
                  
                  <div className="flex flex-col gap-2">
                    <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider">Servidor Configurado</h3>
                    <div className="bg-black/25 rounded-2xl p-4 flex flex-col gap-2 border border-white/5">
                      <p className="text-xs text-gray-400">URL del Host: <span className="text-white font-semibold">{serverUrl}</span></p>
                      <p className="text-xs text-gray-400">Usuario: <span className="text-white font-semibold">{username}</span></p>
                      <p className="text-xs text-gray-400">Estado: <span className="text-green-400 font-semibold">{accountInfo?.status}</span></p>
                      <p className="text-xs text-gray-400">Expiración de la cuenta: <span className="text-white font-semibold">{accountInfo?.expiryDate}</span></p>
                    </div>
                  </div>

                  <div className="flex flex-col gap-4 border-t border-white/5 pt-6">
                    <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider">Control Parental</h3>
                    <div className="flex items-center justify-between bg-black/25 rounded-2xl p-4 border border-white/5">
                      <div>
                        <p className="text-sm font-semibold text-white">Bloqueo de Categorías de Adultos (18+)</p>
                        <p className="text-xs text-gray-400 mt-0.5">Oculta automáticamente el contenido XXX de las listas y la página de inicio.</p>
                      </div>
                      <button 
                        onClick={handleParentalToggleClick}
                        className={`tv-focusable px-6 py-2 rounded-xl font-bold flex items-center gap-2 border transition-all ${parentalLocked ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-green-500/10 border-green-500/30 text-green-400'}`}
                      >
                        {parentalLocked ? (
                          <>
                            <Lock className="w-4 h-4" />
                            Bloqueado (PIN para ver)
                          </>
                        ) : (
                          <>
                            <Unlock className="w-4 h-4" />
                            Desbloqueado
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-col gap-4 border-t border-white/5 pt-6">
                    <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider">Desconectar Cuenta</h3>
                    <button 
                      onClick={handleLogout}
                      className="tv-focusable bg-red-600/15 border border-red-600/30 hover:bg-red-600/25 text-red-400 px-6 py-3.5 rounded-2xl font-bold flex items-center justify-center gap-2 cursor-pointer text-sm"
                    >
                      <LogOut className="w-4 h-4" />
                      Cerrar Sesión en este Dispositivo
                    </button>
                  </div>

                  <div className="flex justify-between items-center border-t border-white/5 pt-6 text-xs text-gray-500">
                    <span>Versión del Cliente: LizzyTV v1.0.0-Beta</span>
                    <span>Desarrollado en React + Vite + Capacitor</span>
                  </div>
                </div>
              )}
            </>
          )}

        </div>
      </main>

      {/* FULL SCREEN VIDEO PLAYER OVERLAY */}
      {isVideoPlaying && activeStream && (
        <div 
          ref={playerContainerRef} 
          className={`fixed inset-0 bg-black z-50 flex items-center justify-center select-none ${showControls ? 'cursor-default' : 'cursor-none'}`}
          onMouseMove={resetControlsTimer}
          onTouchStart={resetControlsTimer}
          onClick={handleContainerClick}
        >
          <video 
            ref={videoRef}
            className="w-full h-full object-contain"
            controls={false}
            autoPlay
            playsInline
            onLoadStart={() => {
              setPlayerLoading(true)
              setPlayerError(null)
            }}
            onWaiting={() => setPlayerLoading(true)}
            onPlaying={() => {
              setPlayerLoading(false)
              setIsVideoPaused(false)
              resetControlsTimer()
            }}
            onPlay={() => {
              setIsVideoPaused(false)
              resetControlsTimer()
            }}
            onPause={() => {
              setIsVideoPaused(true)
              setShowControls(true)
              if (controlsTimeoutRef.current) {
                clearTimeout(controlsTimeoutRef.current)
              }
            }}
            onCanPlay={() => setPlayerLoading(false)}
            onError={(e) => {
              console.error("Video element error event:", e)
              setPlayerLoading(false)
              setPlayerError("Error de reproducción. Es posible que el códec de video/audio de este canal no sea compatible con tu navegador o que el servidor IPTV haya rechazado la conexión.")
            }}
          />

          {/* Loader Overlay */}
          {playerLoading && !playerError && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/75 gap-3 pointer-events-none select-none">
              <div className="w-12 h-12 border-4 border-brand-purple border-t-transparent rounded-full animate-spin shadow-glow-hover" />
              <p className="text-sm font-bold text-white tracking-wider animate-pulse">Conectando con el canal...</p>
            </div>
          )}

          {/* Error Overlay */}
          {playerError && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/90 p-8 text-center select-none z-10">
              <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-500 mb-4 animate-bounce">
                <ShieldAlert className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Error de Reproducción</h3>
              <p className="text-sm text-gray-300 max-w-lg mb-6 leading-relaxed">
                {playerError}
              </p>
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-2xl p-4 text-xs text-yellow-400 max-w-md text-left mb-6">
                <p className="font-bold flex items-center gap-1.5 mb-1">
                  <AlertCircle className="w-4 h-4" />
                  ¿Estás en la PC / Navegador?
                </p>
                <p>Verifica que tienes habilitada y encendida tu extensión de navegador para evadir CORS (ej. "Allow CORS"). De lo contrario, el navegador bloqueará la descarga del flujo directo.</p>
              </div>
              <button 
                onClick={closeVideo}
                className="tv-focusable bg-brand-purple hover:bg-brand-purple-dark text-white font-bold px-6 py-2.5 rounded-xl text-sm transition-all"
              >
                Cerrar Reproductor
              </button>
            </div>
          )}

          <div className={`player-controls-bar absolute inset-x-0 bottom-0 bg-gradient-to-t from-black via-black/50 to-transparent p-8 flex flex-col gap-4 transition-all duration-300 ${
            showControls ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-4 pointer-events-none'
          }`}>
            <div className="flex items-center justify-between">
              <h2 className="text-xl md:text-2xl font-black text-white">{activeStreamTitle}</h2>
              <button 
                onClick={closeVideo}
                className="p-3 bg-white/10 hover:bg-white/20 text-white rounded-full border border-white/10 hover:border-white/20 transition-all focus:outline-none cursor-pointer"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center gap-6">
                <button 
                  onClick={() => {
                    if (videoRef.current) {
                      if (videoRef.current.paused) {
                        videoRef.current.play().catch(e => console.log(e))
                      } else {
                        videoRef.current.pause()
                      }
                    }
                  }}
                  className="p-3 bg-brand-purple hover:bg-brand-purple-dark text-white rounded-full hover:scale-105 transition-all cursor-pointer"
                >
                  {isVideoPaused ? <Play className="w-5 h-5 fill-white" /> : <Pause className="w-5 h-5 fill-white" />}
                </button>

                <button 
                  onClick={toggleMute}
                  className="p-3 bg-white/10 hover:bg-white/20 text-white rounded-full hover:scale-105 transition-all cursor-pointer"
                >
                  {isMuted ? <VolumeX className="w-5 h-5 text-red-400" /> : <Volume2 className="w-5 h-5" />}
                </button>

                <button 
                  onClick={toggleFullscreen}
                  className="p-3 bg-white/10 hover:bg-white/20 text-white rounded-full hover:scale-105 transition-all cursor-pointer"
                  title="Pantalla Completa"
                >
                  {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
                </button>
              </div>

              <div className="flex items-center gap-3 text-xs font-bold text-gray-300 bg-black/60 px-4 py-2 rounded-full border border-white/10 select-none">
                <span className="text-green-400">1080P FHD</span>
                <span>•</span>
                <span>XTREAM STREAM</span>
                <span>•</span>
                <span>AUDIO DIGITAL</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SERIES DETAIL MODAL OVERLAY */}
      {selectedSeriesObj && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-40 flex items-center justify-center p-4 md:p-8 overflow-y-auto">
          <div className="bg-bg-card border border-white/10 rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col md:flex-row relative animate-fade-in shadow-2xl">
            
            <button 
              onClick={() => { setSelectedSeriesObj(null); setSelectedSeriesInfo(null) }}
              className="absolute top-4 right-4 p-2 bg-black/60 hover:bg-black/80 text-white rounded-full border border-white/10 transition-all z-20 focus:outline-none"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Left Column: Poster / Cover */}
            <div className="w-full md:w-1/3 aspect-[2/3] md:aspect-auto md:h-auto shrink-0 relative border-r border-white/5 bg-black/35">
              <img 
                src={selectedSeriesObj.logo} 
                alt={selectedSeriesObj.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1618336753974-aae8e04506aa?w=1200&auto=format&fit=crop&q=80'
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-bg-card via-transparent to-transparent opacity-80 md:opacity-100 pointer-events-none" />
            </div>

            {/* Right Column: Info & Episodes */}
            <div className="flex-1 p-6 md:p-8 flex flex-col gap-6 overflow-y-auto no-scrollbar">
              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold uppercase tracking-widest text-brand-neon bg-brand-purple/20 px-2 py-0.5 rounded w-fit">SERIE</span>
                <h2 className="text-2xl md:text-3xl font-black text-white leading-tight">{selectedSeriesObj.title}</h2>
                <div className="flex items-center gap-3 text-xs text-gray-300 font-semibold mt-1">
                  <span className="text-brand-neon">⭐ {selectedSeriesObj.rating}</span>
                  <span>•</span>
                  <span>Año: {selectedSeriesObj.year || 'N/A'}</span>
                </div>
              </div>

              {loadingSeriesInfo ? (
                <div className="flex-1 flex flex-col items-center justify-center py-12 gap-3 text-gray-400">
                  <div className="w-8 h-8 border-3 border-brand-purple border-t-transparent rounded-full animate-spin" />
                  <p className="text-xs font-bold animate-pulse">Cargando temporadas y episodios...</p>
                </div>
              ) : (
                <>
                  {/* Seasons Selection */}
                  {selectedSeriesInfo?.seasons && selectedSeriesInfo.seasons.length > 0 && (
                    <div className="flex flex-col gap-2 shrink-0">
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-wide">Temporadas</label>
                      <div className="flex gap-2 overflow-x-auto no-scrollbar py-1">
                        {selectedSeriesInfo.seasons.map((season: any) => {
                          const num = Number(season.season_number || 1)
                          return (
                            <button 
                              key={`season-btn-${num}`}
                              onClick={() => setSelectedSeason(num)}
                              className={`tv-focusable px-4 py-2 rounded-xl text-xs font-bold border transition-all whitespace-nowrap ${selectedSeason === num ? 'bg-brand-purple border-brand-purple text-white shadow-glow-hover' : 'bg-white/5 border-white/10 text-gray-400'}`}
                            >
                              Temporada {num}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  {/* Episodes List */}
                  <div className="flex-1 flex flex-col gap-3 min-h-[250px]">
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-wide">Episodios</label>
                    <div className="flex flex-col gap-2 overflow-y-auto pr-1">
                      {(() => {
                        const episodesForSeason = selectedSeriesInfo?.episodes?.[String(selectedSeason)] || []
                        if (episodesForSeason.length === 0) {
                          return <p className="text-xs text-gray-500 italic py-4">No hay episodios disponibles para esta temporada.</p>
                        }
                        return episodesForSeason.map((episode: any) => {
                          const cleanBase = serverUrl.endsWith('/') ? serverUrl.slice(0, -1) : serverUrl
                          const streamUrl = `${cleanBase}/series/${username}/${password}/${episode.id}.${episode.container_extension || 'mp4'}`
                          return (
                            <div 
                              key={`episode-item-${episode.id}`}
                              onClick={() => playVideo(streamUrl, `${selectedSeriesObj.title} - S${selectedSeason}E${episode.episode_num || ''}: ${episode.title}`, selectedSeriesObj.logo, `Serie S${selectedSeason}`, 'episode')}
                              className="tv-focusable cursor-pointer bg-white/5 hover:bg-brand-purple/10 border border-white/5 hover:border-brand-purple/20 rounded-2xl p-4 flex items-center justify-between group transition-all"
                            >
                              <div className="flex items-center gap-3 w-10/12">
                                <div className="w-8 h-8 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-neon font-black text-xs shrink-0">
                                  {episode.episode_num || '#'}
                                </div>
                                <div className="flex flex-col gap-0.5 truncate">
                                  <span className="text-xs font-bold text-white group-hover:text-brand-neon truncate">{episode.title}</span>
                                  <span className="text-[10px] text-gray-400 font-light">Formato: {episode.container_extension || 'mp4'}</span>
                                </div>
                              </div>
                              <Play className="w-4 h-4 text-brand-neon opacity-0 group-hover:opacity-100 fill-brand-neon transition-all" />
                            </div>
                          )
                        })
                      })()}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* PARENTAL PIN MODAL OVERLAY */}
      {showPinModal && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-bg-card border border-white/10 rounded-3xl p-8 max-w-sm w-full flex flex-col items-center gap-6 shadow-2xl animate-fade-in">
            <div className="w-16 h-16 rounded-full bg-brand-purple/10 border border-brand-purple/30 flex items-center justify-center text-brand-neon">
              <Lock className="w-8 h-8" />
            </div>

            <div className="text-center">
              <h3 className="text-lg font-bold text-white">Ingresa el PIN Parental</h3>
              <p className="text-xs text-gray-400 mt-1">El contenido de adultos requiere contraseña de seguridad.</p>
              <p className="text-[10px] text-brand-neon/60 mt-1">PIN demo por defecto: <span className="font-bold">1234</span></p>
            </div>

            <div className="w-full flex flex-col gap-2">
              <input 
                type="password" 
                maxLength={4}
                placeholder="••••"
                value={pinInput}
                onChange={(e) => setPinInput(e.target.value.replace(/\D/g, ''))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handlePinSubmit()
                }}
                className={`w-full text-center text-2xl tracking-[1em] font-bold bg-black/30 border rounded-xl py-3 text-white focus:outline-none focus:border-brand-purple/50 ${pinError ? 'border-red-500' : 'border-white/10'}`}
                autoFocus
              />
              {pinError && (
                <span className="text-[10px] text-red-500 font-bold text-center">PIN incorrecto. Intenta de nuevo.</span>
              )}
            </div>

            <div className="flex gap-4 w-full">
              <button 
                onClick={() => { setShowPinModal(false); setPinInput(''); setPinError(false) }}
                className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 border border-white/5 text-gray-300 font-bold rounded-xl text-sm transition-all"
              >
                Cancelar
              </button>
              <button 
                onClick={handlePinSubmit}
                className="flex-1 py-2.5 bg-brand-purple hover:bg-brand-purple-dark text-white font-bold rounded-xl text-sm transition-all shadow-glow-hover"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}

export default App
