"use client";

import React, { useState, useEffect } from "react";
import { Dropzone } from "@/components/ui/Dropzone";
import { ResultCard } from "@/components/ui/ResultCard";
import { useImageUpload } from "@/hooks/useImageUpload";
import { useCaptionJobStatus } from "@/hooks/useCaptionJobStatus";
import { Sparkles, Image as ImageIcon } from "lucide-react";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [currentFile, setCurrentFile] = useState<File | null>(null);

  const { uploadImage, isUploading, progress, error: uploadError } = useImageUpload();
  const { job, isPolling, error: pollError } = useCaptionJobStatus(jobId);

  const handleFileAccepted = async (file: File) => {
    setCurrentFile(file);
    // Revoke previous URL to prevent memory leaks
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
    }
    
    // Create new preview
    const previewUrl = URL.createObjectURL(file);
    setImagePreviewUrl(previewUrl);

    // Reset current job and upload
    setJobId(null);

    const newJobId = await uploadImage(file);
    if (newJobId) {
      setJobId(newJobId);
    }
  };

  const handleRegenerate = async () => {
    if (currentFile) {
      setJobId(null);
      const newJobId = await uploadImage(currentFile);
      if (newJobId) {
        setJobId(newJobId);
      }
    }
  };

  const handleReset = () => {
    setJobId(null);
    setCurrentFile(null);
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
      setImagePreviewUrl(null);
    }
  };

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      if (imagePreviewUrl) {
        URL.revokeObjectURL(imagePreviewUrl);
      }
    };
  }, [imagePreviewUrl]);

  const hasResult = job !== null;

  return (
    <main className="flex-grow flex flex-col items-center py-12 px-6 md:px-8 max-w-7xl mx-auto w-full">
      {/* Header / Marketing */}
      <div className="text-center mb-12 max-w-2xl">
        <div className="inline-flex items-center justify-center p-3 bg-brand-100 rounded-full mb-6">
          <Sparkles className="w-8 h-8 text-brand-600" />
        </div>
        <h1 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6 tracking-tight">
          Image captioning powered by deep learning.
        </h1>
        <p className="text-lg text-slate-600 font-sans max-w-xl mx-auto">
          Upload an image to automatically generate a descriptive caption.
        </p>
      </div>

      {/* Main App Container */}
      <div className="w-full max-w-3xl space-y-8">
        {!hasResult && (
          <Dropzone
            onFileAccepted={handleFileAccepted}
            isUploading={isUploading}
            progress={progress}
            error={uploadError}
          />
        )}

        {(hasResult || isUploading || isPolling) && (
          <ResultCard
            job={job}
            imagePreviewUrl={imagePreviewUrl}
            onRegenerate={handleRegenerate}
            onClear={handleReset}
          />
        )}
      </div>

      {/* Features / Footer area */}
      {!hasResult && !isUploading && (
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl text-center text-slate-600">
          <div className="flex flex-col items-center">
            <div className="bg-white p-4 rounded-full shadow-sm border border-slate-200 mb-4">
              <ImageIcon className="w-6 h-6 text-brand-500" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-2">High Quality</h3>
            <p className="text-sm">Trained on the massive MS-COCO dataset for context-aware descriptions.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="bg-white p-4 rounded-full shadow-sm border border-slate-200 mb-4">
              <Sparkles className="w-6 h-6 text-brand-500" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-2">Fast Inference</h3>
            <p className="text-sm">Get accurate captions in seconds with our optimized serving pipeline.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="bg-white p-4 rounded-full shadow-sm border border-slate-200 mb-4">
              <svg className="w-6 h-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-900 mb-2">Private by Design</h3>
            <p className="text-sm">Anonymous uploads are securely processed and never shared.</p>
          </div>
        </div>
      )}
    </main>
  );
}
