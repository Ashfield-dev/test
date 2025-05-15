import os
import queue
import threading
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from app.core.logger import main_logger

@dataclass
class DownloadItem:
    url: str
    caption: str = ""
    priority: int = 5
    status: str = "queued"
    progress: float = 0
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class DownloadManager:
    def __init__(self, max_workers: int = 5, bandwidth_limit: int = 1024*1024):
        self.max_workers = max_workers
        self.bandwidth_limit = bandwidth_limit
        self.download_queue = queue.PriorityQueue()
        self.active_downloads: Dict[str, DownloadItem] = {}
        self.failed_downloads: List[DownloadItem] = []
        self.workers: List[threading.Thread] = []
        self.paused = False
        self.lock = threading.Lock()
        self._start_workers()
        main_logger.info(f"Download Manager initialized with {max_workers} workers")

    def _start_workers(self):
        """Start worker threads"""
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker_thread, daemon=True)
            worker.start()
            self.workers.append(worker)

    def _worker_thread(self):
        """Worker thread for processing downloads"""
        while True:
            if self.paused:
                continue
            try:
                priority, item = self.download_queue.get(timeout=1)
                self._process_download(item)
            except queue.Empty:
                continue
            except Exception as e:
                main_logger.error(f"Worker thread error: {str(e)}")

    def _process_download(self, item: DownloadItem):
        """Process a single download"""
        try:
            item.start_time = datetime.now()
            item.status = "downloading"
            self.active_downloads[item.url] = item

            response = requests.get(item.url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            filename = os.path.join('temp_downloads', os.path.basename(item.url))
            os.makedirs('temp_downloads', exist_ok=True)

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size:
                            item.progress = (downloaded_size / total_size) * 100

            item.status = "completed"
            item.end_time = datetime.now()
            del self.active_downloads[item.url]

        except Exception as e:
            item.status = "failed"
            item.error = str(e)
            self.failed_downloads.append(item)
            if item.url in self.active_downloads:
                del self.active_downloads[item.url]
            main_logger.error(f"Download failed for {item.url}: {str(e)}")

    def add_download(self, url: str, caption: str = "", priority: int = 5):
        """Add a new download to the queue"""
        item = DownloadItem(url=url, caption=caption, priority=priority)
        self.download_queue.put((priority, item))
        main_logger.info(f"Added download: {url} with priority {priority}")

    def pause(self):
        """Pause all downloads"""
        self.paused = True
        main_logger.info("Downloads paused")

    def resume(self):
        """Resume all downloads"""
        self.paused = False
        main_logger.info("Downloads resumed")

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.download_queue.qsize()

    def get_active_downloads_count(self) -> int:
        """Get number of active downloads"""
        return len(self.active_downloads)

    def get_failed_downloads_count(self) -> int:
        """Get number of failed downloads"""
        return len(self.failed_downloads)

    def get_active_downloads(self) -> Dict[str, dict]:
        """Get active downloads status"""
        return {url: {
            'progress': item.progress,
            'status': item.status,
            'caption': item.caption
        } for url, item in self.active_downloads.items()}

    def get_failed_downloads(self) -> List[dict]:
        """Get failed downloads"""
        return [{
            'url': item.url,
            'error': item.error,
            'caption': item.caption
        } for item in self.failed_downloads]

    def retry_failed(self, url: str):
        """Retry a failed download"""
        for item in self.failed_downloads[:]:
            if item.url == url:
                self.failed_downloads.remove(item)
                self.add_download(item.url, item.caption, item.priority)
                main_logger.info(f"Retrying download: {url}")
                break

    def set_bandwidth_limit(self, limit: int):
        """Set bandwidth limit in bytes/second"""
        self.bandwidth_limit = limit
        main_logger.info(f"Bandwidth limit set to {limit} bytes/second") 