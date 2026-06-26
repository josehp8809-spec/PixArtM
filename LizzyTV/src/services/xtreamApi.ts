// Xtream Codes API Service for LizzyTV

export interface XtreamAccountInfo {
  username: string
  status: string
  expiryDate: string
  auth: boolean
}

export interface XtreamCategory {
  id: string
  name: string
}

export interface XtreamLiveChannel {
  id: string
  name: string
  logo: string
  categoryId: string
  streamUrl: string
}

export interface XtreamMovie {
  id: string
  title: string
  logo: string
  categoryId: string
  rating: string
  year: string
  container: string
  streamUrl: string
}

export interface XtreamSeries {
  id: string
  title: string
  logo: string
  categoryId: string
  rating: string
  year: string
}

export class XtreamApi {
  private baseUrl: string
  private user: string
  private pass: string
  private rawUser: string
  private rawPass: string

  constructor(url: string, user: string, pass: string) {
    // Limpiar la URL de barras finales
    this.baseUrl = url.endsWith('/') ? url.slice(0, -1) : url
    this.rawUser = user
    this.rawPass = pass
    this.user = encodeURIComponent(user)
    this.pass = encodeURIComponent(pass)
  }

  // Utilidad para construir URLs de peticiones
  private getApiUrl(action?: string, extraParams: string = ''): string {
    const actionParam = action ? `&action=${action}` : ''
    return `${this.baseUrl}/player_api.php?username=${this.user}&password=${this.pass}${actionParam}${extraParams}`
  }

  // Petición genérica con manejo de errores y CORS
  private async fetchApi<T>(url: string): Promise<T> {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP Error Status: ${response.status}`)
      }
      
      const data = await response.json()
      return data as T
    } catch (error: any) {
      console.error("API Fetch Error:", error)
      // Si el error parece ser un fallo de red por CORS
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new Error('CORS_ERROR')
      }
      throw error
    }
  }

  // 1. LOGIN & AUTENTICACIÓN
  async authenticate(): Promise<XtreamAccountInfo> {
    const url = this.getApiUrl()
    const result = await this.fetchApi<any>(url)

    if (result && result.user_info) {
      const auth = result.user_info.auth === 1 || result.user_info.auth === true
      const expDateRaw = result.user_info.exp_date
      let expiryDate = 'Ilimitado'

      if (expDateRaw && expDateRaw !== 'null' && expDateRaw !== null) {
        // Convertir timestamp a formato legible
        const dateObj = new Date(parseInt(expDateRaw) * 1000)
        expiryDate = dateObj.toLocaleDateString()
      }

      return {
        username: result.user_info.username || this.user,
        status: result.user_info.status || 'Active',
        expiryDate,
        auth
      }
    }

    throw new Error('AUTH_FAILED')
  }

  // 2. CATEGORÍAS
  async getLiveCategories(): Promise<XtreamCategory[]> {
    const url = this.getApiUrl('get_live_categories')
    const data = await this.fetchApi<any[]>(url)
    return (data || []).map(item => ({
      id: String(item.category_id),
      name: item.category_name
    }))
  }

  async getVodCategories(): Promise<XtreamCategory[]> {
    const url = this.getApiUrl('get_vod_categories')
    const data = await this.fetchApi<any[]>(url)
    return (data || []).map(item => ({
      id: String(item.category_id),
      name: item.category_name
    }))
  }

  async getSeriesCategories(): Promise<XtreamCategory[]> {
    const url = this.getApiUrl('get_series_categories')
    const data = await this.fetchApi<any[]>(url)
    return (data || []).map(item => ({
      id: String(item.category_id),
      name: item.category_name
    }))
  }

  // 3. CONTENIDOS (CANALES, PELÍCULAS, SERIES)
  async getLiveStreams(): Promise<XtreamLiveChannel[]> {
    const url = this.getApiUrl('get_live_streams')
    const data = await this.fetchApi<any[]>(url)
    return (data || []).map(item => ({
      id: String(item.stream_id),
      name: item.name,
      logo: item.stream_icon || '',
      categoryId: String(item.category_id),
      // URL para reproducir canal directo .ts
      streamUrl: `${this.baseUrl}/live/${this.rawUser}/${this.rawPass}/${item.stream_id}.ts`
    }))
  }

  async getVodStreams(): Promise<XtreamMovie[]> {
    const url = this.getApiUrl('get_vod_streams')
    const data = await this.fetchApi<any[]>(url)
    return (data || []).map(item => ({
      id: String(item.stream_id),
      title: item.name,
      logo: item.stream_icon || '',
      categoryId: String(item.category_id),
      rating: String(item.rating || '4.0'),
      year: String(item.year || ''),
      container: item.container_extension || 'mp4',
      // URL de reproducción directa
      streamUrl: `${this.baseUrl}/movie/${this.rawUser}/${this.rawPass}/${item.stream_id}.${item.container_extension || 'mp4'}`
    }))
  }

  async getSeries(): Promise<XtreamSeries[]> {
    const url = this.getApiUrl('get_series')
    const data = await this.fetchApi<any[]>(url)
    return (data || []).map(item => ({
      id: String(item.series_id),
      title: item.name,
      logo: item.cover || '',
      categoryId: String(item.category_id),
      rating: String(item.rating || '4.0'),
      year: String(item.releaseDate || '')
    }))
  }

  async getSeriesInfo(seriesId: string): Promise<any> {
    const url = this.getApiUrl('get_series_info', `&series_id=${seriesId}`)
    return this.fetchApi<any>(url)
  }

  // 4. GUÍA DE PROGRAMACIÓN (EPG)
  async getShortEpg(streamId: string): Promise<string> {
    const url = this.getApiUrl('get_short_epg', `&stream_id=${streamId}`)
    try {
      const data = await this.fetchApi<any>(url)
      if (data && data.epg_listings && data.epg_listings.length > 0) {
        const currentShow = data.epg_listings[0]
        const title = currentShow.title ? atob(currentShow.title) : 'Sin Información'
        return title
      }
      return 'Sin Información'
    } catch {
      return 'Sin Información'
    }
  }
}
