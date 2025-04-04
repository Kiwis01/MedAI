'use client'

import { useState, useCallback } from 'react'
import Image from 'next/image'
import { api, AnalysisResult } from '@/lib/api'

export default function ImageAnalysis() {
  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setImage(file)
      setPreview(URL.createObjectURL(file))
      setResult(null)
      setError(null)
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setImage(file)
      setPreview(URL.createObjectURL(file))
      setResult(null)
      setError(null)
    }
  }, [])

  const handleAnalyze = async () => {
    if (!image) return

    setLoading(true)
    setError(null)
    
    try {
      const result = await api.analyzeImage(image)
      console.log('API Response:', result) // Debug log
      setResult(result)
    } catch (err) {
      console.error('Analysis error:', err) // Debug log
      setError('Failed to analyze image. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors"
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
          id="imageInput"
        />
        <label
          htmlFor="imageInput"
          className="cursor-pointer block"
        >
          {preview ? (
            <div className="relative w-full aspect-video max-w-2xl mx-auto">
              <Image
                src={preview}
                alt="Selected image"
                fill
                className="object-contain"
              />
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-gray-500">
                Drag and drop your medical image here, or click to select
              </p>
              <p className="text-sm text-gray-400">
                Supports: PNG, JPG, JPEG
              </p>
            </div>
          )}
        </label>
      </div>

      {/* Analysis Button */}
      {image && (
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className={`w-full py-3 px-4 rounded-lg text-white font-medium ${
            loading
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? 'Analyzing...' : 'Analyze Image'}
        </button>
      )}

      {/* Results */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="font-medium text-green-800 mb-2">Analysis Results:</h3>
          <div className="space-y-4">
            {result.predictions?.map((prediction, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-green-700">
                    {prediction.class}
                  </span>
                  <span className="text-sm text-green-600">
                    Confidence: {(prediction.confidence * 100).toFixed(2)}%
                  </span>
                </div>
                {prediction.bbox && (
                  <div className="text-sm text-green-600">
                    <p>Bounding Box:</p>
                    <ul className="list-disc list-inside pl-4">
                      <li>Top Left: ({prediction.bbox.x1}, {prediction.bbox.y1})</li>
                      <li>Bottom Right: ({prediction.bbox.x2}, {prediction.bbox.y2})</li>
                    </ul>
                  </div>
                )}
              </div>
            ))}
            <div className="text-sm text-green-600 mt-2">
              <p>Inference ID: {result.inference_id}</p>
              <p>Processing Time: {result.time}</p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}
    </div>
  )
}