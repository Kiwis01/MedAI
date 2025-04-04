const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export interface ChatMessage {
  content: string
  is_user: boolean
  imageUrl?: string
  analysis?: AnalysisResult
}

export interface Prediction {
  class: string
  confidence: number
  bbox?: {
    x1: number
    y1: number
    x2: number
    y2: number
  }
}

export interface AnalysisResult {
  image: string
  inference_id: string
  predictions: Prediction[]
  time: string
  error?: string
}

export const api = {
  async analyzeImage(file: File): Promise<AnalysisResult> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Failed to analyze image')
    }

    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }

    return data
  },

  async sendMessage(message: string, image?: File): Promise<ChatMessage[]> {
    try {
      // If there's an image, analyze it first
      let analysis: AnalysisResult | undefined
      if (image) {
        analysis = await this.analyzeImage(image)
      }

      // Send the message with analysis data
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          analysis
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      if (!Array.isArray(data)) {
        throw new Error('Invalid response format')
      }

      return data
    } catch (error) {
      console.error('Error in sendMessage:', error)
      throw error
    }
  }
}