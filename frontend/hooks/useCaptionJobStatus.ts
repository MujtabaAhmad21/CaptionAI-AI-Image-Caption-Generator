import { useState, useEffect } from "react";

export type Caption = {
  id: string;
  text: string;
  beam_rank: number;
  is_edited: boolean;
  edited_text: string | null;
};

export type JobStatus = "queued" | "running" | "succeeded" | "failed";

export type JobResponse = {
  job_id: string;
  status: JobStatus;
  error_message: string | null;
  captions: Caption[];
};

export const useCaptionJobStatus = (jobId: string | null) => {
  const [job, setJob] = useState<JobResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      setIsPolling(false);
      setError(null);
      return;
    }

    let isMounted = true;
    let timeoutId: NodeJS.Timeout;

    const poll = async () => {
      setIsPolling(true);
      try {
        const response = await fetch(`/api/v1/jobs/${jobId}`, {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error("Failed to fetch job status");
        }
        
        const data: JobResponse = await response.json();
        if (!isMounted) return;

        setJob(data);

        if (data.status === "queued" || data.status === "running") {
          timeoutId = setTimeout(poll, 2000);
        } else {
          setIsPolling(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || "Error polling job");
          setIsPolling(false);
        }
      }
    };

    poll();

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, [jobId]);

  return { job, isPolling, error };
};
