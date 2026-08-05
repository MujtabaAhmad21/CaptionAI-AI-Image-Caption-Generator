import React, { useRef, useState } from "react";
import { UploadCloud, AlertCircle } from "lucide-react";
import { UploadError } from "@/hooks/useImageUpload";

interface DropzoneProps {
  onFileAccepted: (file: File) => void;
  isUploading: boolean;
  progress: number;
  error: UploadError | null;
}

export const Dropzone: React.FC<DropzoneProps> = ({
  onFileAccepted,
  isUploading,
  progress,
  error,
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!isUploading) setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);

    if (isUploading) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      onFileAccepted(file);
      e.dataTransfer.clearData();
    }
  };

  const handleClick = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileAccepted(e.target.files[0]);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  };

  const baseContainerStyles =
    "relative flex flex-col items-center justify-center p-8 md:p-12 border-2 border-dashed rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-brand-300 focus:ring-offset-2 cursor-pointer";
  
  let stateStyles = "border-slate-300 hover:border-brand-500 hover:bg-brand-50";
  if (isDragActive) {
    stateStyles = "border-brand-500 bg-brand-50";
  } else if (isUploading) {
    stateStyles = "border-brand-500 bg-slate-50 cursor-default";
  } else if (error) {
    stateStyles = "border-error-600 bg-accent-100/50";
  }

  return (
    <div
      className={`${baseContainerStyles} ${stateStyles}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label="Upload image dropzone"
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/*"
        className="hidden"
        aria-hidden="true"
      />

      {isUploading ? (
        <div className="w-full max-w-xs flex flex-col items-center text-center">
          <UploadCloud className="w-12 h-12 text-brand-500 mb-4 animate-bounce" />
          <p className="text-slate-900 font-medium mb-2">Uploading...</p>
          <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
            <div
              className="bg-brand-500 h-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-slate-500 mt-2">{progress}%</p>
        </div>
      ) : (
        <div className="flex flex-col items-center text-center">
          <UploadCloud
            className={`w-12 h-12 mb-4 ${error ? "text-error-600" : "text-slate-400"}`}
          />
          <p className="text-slate-900 font-medium text-lg mb-1">
            Drag an image here, or click to browse
          </p>
          <p className="text-slate-500 text-sm">
            Supports JPEG, PNG, WEBP (max 10MB)
          </p>

          {error && (
            <div className="mt-4 flex items-center text-error-600 text-sm font-medium bg-white px-3 py-2 rounded-md shadow-sm border border-error-200">
              <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
              <span>{error.message}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
