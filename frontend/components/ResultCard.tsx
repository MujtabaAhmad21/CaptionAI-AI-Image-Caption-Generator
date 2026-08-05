import React, { useState, useEffect } from "react";
import { Check, Copy, RefreshCw, Edit2, AlertTriangle, Save, X, Upload } from "lucide-react";
import { JobResponse } from "@/hooks/useCaptionJobStatus";
import { Button } from "./Button";

interface ResultCardProps {
  job: JobResponse | null;
  imagePreviewUrl: string | null;
  onRegenerate?: () => void;
  onClear?: () => void; 
}

export const ResultCard: React.FC<ResultCardProps> = ({ job, imagePreviewUrl, onRegenerate, onClear }) => {
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState("");
  const [finalText, setFinalText] = useState("");

  useEffect(() => {
    if (job?.captions && job.captions.length > 0) {
      setFinalText(job.captions[0].text);
      setEditedText(job.captions[0].text);
    }
  }, [job]);

  if (!job && !imagePreviewUrl) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(finalText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveEdit = () => {
    setFinalText(editedText);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedText(finalText);
    setIsEditing(false);
  };

  const isProcessing = job?.status === "queued" || job?.status === "running";
  const hasFailed = job?.status === "failed";
  const hasSucceeded = job?.status === "succeeded";

  const renderStatusBadge = () => {
    if (isProcessing) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-600/10 text-warning-600">
          <span className="w-2 h-2 mr-1.5 bg-warning-600 rounded-full animate-pulse" />
          Processing
        </span>
      );
    }
    if (hasFailed) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-600/10 text-error-600">
          <span className="w-2 h-2 mr-1.5 bg-error-600 rounded-full" />
          Failed
        </span>
      );
    }
    if (hasSucceeded) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-600/10 text-success-600">
          <span className="w-2 h-2 mr-1.5 bg-success-600 rounded-full" />
          Done
        </span>
      );
    }
    return null;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-md shadow-sm overflow-hidden flex flex-col md:flex-row">
      {/* Image Section */}
      <div className="w-full md:w-2/5 bg-slate-100 border-b md:border-b-0 md:border-r border-slate-200 min-h-[200px] flex items-center justify-center overflow-hidden">
        {imagePreviewUrl ? (
          <img
            src={imagePreviewUrl}
            alt="Uploaded preview"
            className="w-full h-full object-cover object-center max-h-[400px] md:max-h-none"
          />
        ) : (
          <div className="text-slate-400">No Image</div>
        )}
      </div>

      {/* Content Section */}
      <div className="w-full md:w-3/5 p-6 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">Result</h3>
          {renderStatusBadge()}
        </div>

        <div className="flex-grow flex flex-col justify-center min-h-[120px]">
          {isProcessing && (
            <div className="space-y-3 animate-pulse">
              <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              <div className="h-4 bg-slate-200 rounded w-full"></div>
              <div className="h-4 bg-slate-200 rounded w-5/6"></div>
              <p className="text-sm text-slate-400 mt-4">Analyzing image...</p>
            </div>
          )}

          {hasFailed && (
            <div className="flex flex-col items-center justify-center text-center text-error-600 space-y-2">
              <AlertTriangle className="w-8 h-8 opacity-80" />
              <p className="text-sm font-medium">
                {job.error_message || "An error occurred while generating the caption."}
              </p>
            </div>
          )}

          {hasSucceeded && job.captions && job.captions.length > 0 && (
            <div>
              {isEditing ? (
                <div className="flex flex-col gap-3">
                  <textarea
                    value={editedText}
                    onChange={(e) => setEditedText(e.target.value)}
                    className="w-full min-h-[100px] p-3 text-base text-slate-900 leading-relaxed font-body border border-brand-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-y"
                    autoFocus
                  />
                  <div className="flex items-center gap-2">
                    <Button variant="accent" size="sm" onClick={handleSaveEdit} leftIcon={<Save className="w-4 h-4" />}>
                      Save
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleCancelEdit} leftIcon={<X className="w-4 h-4" />}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-base text-slate-900 leading-relaxed font-body whitespace-pre-wrap">
                  {finalText}
                </p>
              )}
              
              {/* Future feature placeholders for Multiple suggestions */}
              {!isEditing && job.captions.length > 1 && (
                <div className="mt-4 pt-4 border-t border-slate-100">
                  <p className="text-xs text-slate-400 mb-2 uppercase tracking-wider font-semibold">Other suggestions</p>
                  <ul className="space-y-2 text-sm text-slate-600">
                    {job.captions.slice(1).map((caption, idx) => (
                      <li key={idx}>• {caption.text}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {hasSucceeded && !isEditing && (
          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col gap-3">
            <div className="flex flex-wrap gap-2">
              <Button
                variant="ghost"
                size="sm"
                leftIcon={copied ? <Check className="w-4 h-4 text-success-600" /> : <Copy className="w-4 h-4" />}
                onClick={handleCopy}
              >
                {copied ? "Copied!" : "Copy"}
              </Button>
              <Button variant="accent" size="sm" leftIcon={<RefreshCw className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />} onClick={onRegenerate} disabled={isProcessing}>
                Regenerate
              </Button>
              <Button variant="ghost" size="sm" leftIcon={<Edit2 className="w-4 h-4" />} onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            </div>
            <div>
              <Button variant="ghost" size="sm" leftIcon={<Upload className="w-4 h-4" />} onClick={onClear}>
                Upload New Image
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
