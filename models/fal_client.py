"""
GILL VEDIO - Fal.ai API Client
=============================
Integrates Fal.ai queue-based video generation for HunyuanVideo/Wan2.1.
"""
import requests
import json
import time
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class FalJob:
    job_id: str
    status: str
    output_url: Optional[str] = None

class FalClient:
    """Client for Fal.ai API (generates videos via HunyuanVideo)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Default high-quality open-source text-to-video model on fal
        self.model_id = "fal-ai/hunyuan-video"
        self.headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate_video(self, prompt: str, duration_seconds: int = 10) -> FalJob:
        """Submit a video generation request to the fal.ai queue."""
        url = f"https://queue.fal.run/{self.model_id}"
        
        # Mapping standard inputs for fal-ai/hunyuan-video
        payload = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": "9:16",  # Vertical shorts/reels
            }
        }
        
        logger.info(f"Submitting job to Fal.ai for model {self.model_id}...")
        resp = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        
        job_id = data.get("request_id")
        if not job_id:
            raise RuntimeError(f"Fal.ai returned no request_id: {data}")
            
        logger.info(f"Fal.ai job submitted successfully. request_id={job_id}")
        return FalJob(job_id=str(job_id), status="submitted")

    def poll_job(
        self,
        job_id: str,
        poll_interval_seconds: int = 10,
        timeout_seconds: int = 600,
    ) -> FalJob:
        """Poll the fal.ai queue for job status and get the response."""
        status_url = f"https://queue.fal.run/{self.model_id}/requests/{job_id}/status"
        response_url = f"https://queue.fal.run/{self.model_id}/requests/{job_id}/response"
        
        logger.info(f"Polling status for Fal.ai job {job_id}...")
        start = time.time()
        
        while time.time() - start < timeout_seconds:
            resp = requests.get(status_url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            status_data = resp.json()
            status = status_data.get("status", "IN_QUEUE")
            
            logger.info(f"Fal.ai job {job_id} status: {status}")
            
            if status == "COMPLETED":
                # Get the final result
                res_resp = requests.get(response_url, headers=self.headers, timeout=30)
                res_resp.raise_for_status()
                res_data = res_resp.json()
                
                video_data = res_data.get("video", {})
                output_url = video_data.get("url")
                
                if not output_url:
                    raise RuntimeError(f"Fal.ai job completed but returned no video URL: {res_data}")
                    
                logger.info(f"Fal.ai job {job_id} succeeded. Output URL: {output_url}")
                return FalJob(job_id=job_id, status="succeeded", output_url=output_url)
                
            if status in {"failed", "error", "FAILED", "ERROR"}:
                raise RuntimeError(f"Fal.ai job failed. job_id={job_id}, response={status_data}")
                
            time.sleep(poll_interval_seconds)
            
        raise TimeoutError(f"Fal.ai job timed out. job_id={job_id}")
