'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, Shield, AlertCircle } from 'lucide-react'
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
  const [dragOver, setDragOver] = useState(false);
  
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

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    multiple: false,
    onDragEnter: () => setDragOver(true),
    onDragLeave: () => setDragOver(false),
    onDropAccepted: () => setDragOver(false),
    onDropRejected: () => setDragOver(false)
  })

  return (
    <div className="max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8 md:p-12 text-center cursor-pointer
          transition-all duration-300 shadow-sm
          ${dragOver 
            ? 'border-amber-600 bg-amber-50 shadow-md scale-[1.02]' 
            : 'border-gray-300 bg-white hover:border-amber-600 hover:bg-stone-50 hover:shadow'
          }
        `}
        aria-label="Drop zone for PDF upload"
        role="button"
        tabIndex={0}
      >
        <input {...getInputProps()} aria-label="File upload input" />
        
        <div className="flex flex-col items-center">
          <div className={`
            rounded-full p-4 mb-6
            ${dragOver 
              ? 'bg-blue-100' 
              : 'bg-gray-100'
            }
          `}>
            {dragOver ? (
              <Upload className="h-12 w-12 text-amber-700 animate-bounce" aria-hidden="true" />
            ) : (
              <File className="h-12 w-12 text-amber-700" aria-hidden="true" />
            )}
          </div>
          
          <h3 className="text-2xl font-semibold text-black mb-3">
            {dragOver ? 'Drop your PDF here' : 'Upload Credit Card Statement'}
          </h3>
          
          <p className="text-black mb-6 max-w-md mx-auto">
            Drag and drop your PDF file here, or click to browse your files
          </p>
          
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm text-black">
              <File className="h-4 w-4" aria-hidden="true" />
              <span>PDF only</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm text-black">
              <AlertCircle className="h-4 w-4" aria-hidden="true" />
              <span>Max 10MB</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm text-black">
              <Shield className="h-4 w-4" aria-hidden="true" />
              <span>Secure Processing</span>
            </div>
          </div>

          <button
            type="button"
            onClick={open}
            className="mt-2 px-6 py-3 bg-amber-700 text-white rounded-md hover:shadow-md transition-all font-medium focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2"
            aria-label="Select file to upload"
          >
            Select File
          </button>
        </div>
      </div>
      
      <div className="mt-6 text-center">
        <p className="text-sm text-black">
          By uploading a file, you agree to our <a href="#" className="text-black underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:rounded">Terms of Service</a> and <a href="#" className="text-black underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:rounded">Privacy Policy</a>
        </p>
      </div>

      <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
        <h4 className="font-semibold text-black mb-2 text-sm">Supported Banks:</h4>
        <ul className="text-sm text-black space-y-1">
          <li>✓ Kotak Mahindra Bank</li>
          <li>✓ Axis Bank</li>
          <li>✓ HDFC Bank</li>
          <li>✓ ICICI Bank</li>
          <li>✓ IDFC First Bank</li>
          <li>✓ American Express</li>
          <li>✓ Capital One</li>
        </ul>
      </div>
    </div>
  )
}
