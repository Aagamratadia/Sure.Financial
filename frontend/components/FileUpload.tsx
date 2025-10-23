'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File } from 'lucide-react'
import { uploadStatement } from '@/lib/api'

interface FileUploadProps {
  onUploadComplete: (data: any) => void
  onUploadError: (error: string) => void
  onUploadStart: () => void
}

export default function FileUpload({ 
  onUploadComplete, 
  onUploadError, 
  onUploadStart 
}: FileUploadProps) {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      onUploadError('Please select a valid PDF file')
      return
    }

    const file = acceptedFiles[0]
    
    // Validate file type
    if (file.type !== 'application/pdf') {
      onUploadError('Only PDF files are supported')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      onUploadError('File size must be less than 10MB')
      return
    }

    onUploadStart()

    try {
      const result = await uploadStatement(file)
      onUploadComplete(result)
    } catch (err: any) {
      onUploadError(err.message || 'Failed to upload file')
    }
  }, [onUploadComplete, onUploadError, onUploadStart])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    multiple: false
  })

  return (
    <div className="max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          border-3 border-dashed rounded-xl p-12 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-gray-50'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center">
          {isDragActive ? (
            <Upload className="h-16 w-16 text-blue-500 mb-4 animate-bounce" />
          ) : (
            <File className="h-16 w-16 text-gray-400 mb-4" />
          )}
          
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {isDragActive ? 'Drop your PDF here' : 'Upload Credit Card Statement'}
          </h3>
          
          <p className="text-gray-600 mb-4">
            Drag and drop your PDF file here, or click to browse
          </p>
          
          <div className="text-sm text-gray-500">
            <p>Supported formats: PDF only</p>
            <p>Maximum file size: 10MB</p>
          </div>

          <button
            type="button"
            className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Select File
          </button>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2 text-sm">Supported Banks:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Kotak Mahindra Bank</li>
          <li>✓ HDFC Bank</li>
          <li>✓ ICICI Bank</li>
          <li>✓ American Express</li>
          <li>✓ Capital One</li>
        </ul>
      </div>
    </div>
  )
}
