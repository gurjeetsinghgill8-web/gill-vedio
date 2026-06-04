"""
GILL VEDIO - JSON2Video API Client
==================================
Integrates JSON2Video movie rendering API.
"""
import requests
import json
import time
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class JSON2VideoJob:
    job_id: str
    status: str
    output_url: Optional[str] = None

class JSON2VideoClient:
    """Client for JSON2Video API (renders videos programmatically)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2/movies"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def generate_video(self, prompt: str, duration_seconds: int = 10) -> JSON2VideoJob:
        """Submit a movie rendering job to JSON2Video."""
        # Create a vertical video scene with a dark/vibrant background and text overlay
        payload = {
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "scenes": [
                {
                    "duration": duration_seconds,
                    "background-color": "#11111d",
                    "elements": [
                        {
                            "type": "text",
                            "text": prompt[:150] + "...",  # Show a snippet of the video prompt
                            "style": {
                                "font-size": "50px",
                                "color": "#ffffff",
                                "text-align": "center",
                                "position": "center",
                                "width": 900
                            }
                        }
                    ]
                }
            ]
        }
        
        logger.info("Submitting movie render request to JSON2Video...")
        resp = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        
        project_id = data.get("project")
        if not project_id:
            raise RuntimeError(f"JSON2Video returned no project ID: {data}")
            
        logger.info(f"JSON2Video render job submitted. project_id={project_id}")
        return JSON2VideoJob(job_id=str(project_id), status="submitted")

    def poll_job(
        self,
        job_id: str,
        poll_interval_seconds: int = 10,
        timeout_seconds: int = 600,
    ) -> JSON2VideoJob:
        """Poll JSON2Video for movie render status and get the final URL."""
        url = f"{self.base_url}?project={job_id}"
        
        logger.info(f"Polling status for JSON2Video project {job_id}...")
        start = time.time()
        
        while time.time() - start < timeout_seconds:
            resp = requests.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            movie = data.get("movie", {})
            status = movie.get("status", "queued")
            
            logger.info(f"JSON2Video movie status: {status}")
            
            if status == "done":
                output_url = movie.get("url")
                if not output_url:
                    raise RuntimeError(f"JSON2Video finished but returned no output URL: {data}")
                logger.info(f"JSON2Video movie rendered successfully. URL: {output_url}")
                return JSON2VideoJob(job_id=job_id, status="succeeded", output_url=output_url)
                
            if status == "error":
                message = movie.get("message", "Unknown rendering error")
                raise RuntimeError(f"JSON2Video rendering failed. job_id={job_id}, message={message}")
                
            time.sleep(poll_interval_seconds)
            
        raise TimeoutError(f"JSON2Video job timed out. job_id={job_id}")
