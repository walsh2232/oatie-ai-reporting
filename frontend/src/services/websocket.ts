/**
 * WebSocket Service for Real-time Analytics
 * Handles connection management and data streaming
 */

export interface RealTimeMetrics {
  timestamp: string
  metrics: {
    active_users: number
    queries_per_second: number
    response_time_ms: number
    memory_usage: number
    cpu_usage: number
  }
  alerts: Array<{
    type: string
    message: string
    severity: string
    timestamp: string
  }>
}

export interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
}

export class AnalyticsWebSocketService {
  private socket: WebSocket | null = null
  private config: WebSocketConfig
  private reconnectAttempts = 0
  private listeners: Array<(data: RealTimeMetrics) => void> = []
  private statusListeners: Array<(connected: boolean) => void> = []
  private reconnectTimer: NodeJS.Timeout | null = null

  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = {
      url: this.getWebSocketUrl(),
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      ...config
    }
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/api/v1/analytics/streaming`
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(this.config.url)

        this.socket.onopen = () => {
          console.log('Analytics WebSocket connected')
          this.reconnectAttempts = 0
          this.notifyStatusListeners(true)
          resolve()
        }

        this.socket.onmessage = (event) => {
          try {
            const data: RealTimeMetrics = JSON.parse(event.data)
            this.notifyListeners(data)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.socket.onclose = (event) => {
          console.log('Analytics WebSocket closed:', event.reason)
          this.notifyStatusListeners(false)
          this.handleReconnect()
        }

        this.socket.onerror = (error) => {
          console.error('Analytics WebSocket error:', error)
          reject(error)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    
    this.notifyStatusListeners(false)
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`)
      
      this.reconnectTimer = setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error)
        })
      }, this.config.reconnectInterval)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  addListener(callback: (data: RealTimeMetrics) => void): void {
    this.listeners.push(callback)
  }

  removeListener(callback: (data: RealTimeMetrics) => void): void {
    this.listeners = this.listeners.filter(listener => listener !== callback)
  }

  addStatusListener(callback: (connected: boolean) => void): void {
    this.statusListeners.push(callback)
  }

  removeStatusListener(callback: (connected: boolean) => void): void {
    this.statusListeners = this.statusListeners.filter(listener => listener !== callback)
  }

  private notifyListeners(data: RealTimeMetrics): void {
    this.listeners.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error('Error in WebSocket listener:', error)
      }
    })
  }

  private notifyStatusListeners(connected: boolean): void {
    this.statusListeners.forEach(callback => {
      try {
        callback(connected)
      } catch (error) {
        console.error('Error in WebSocket status listener:', error)
      }
    })
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }

  getConnectionState(): string {
    if (!this.socket) return 'DISCONNECTED'
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING'
      case WebSocket.OPEN:
        return 'CONNECTED'
      case WebSocket.CLOSING:
        return 'CLOSING'
      case WebSocket.CLOSED:
        return 'CLOSED'
      default:
        return 'UNKNOWN'
    }
  }
}

// Singleton instance for application-wide use
export const analyticsWebSocket = new AnalyticsWebSocketService()