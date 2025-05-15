from flask import Blueprint, jsonify, request
from app.core.logger import web_logger
from app.config import Config
import csv

# Create blueprint
api = Blueprint('api', __name__)

def init_api(download_manager):
    """Initialize API routes with download manager instance"""
    
    @api.route('/queue/data', methods=['GET'])
    def get_queue_data():
        try:
            # Get all items (queue + active + failed)
            queue_items = []
            
            # Add items from queue
            queue_size = download_manager.get_queue_size()
            while queue_size > 0:
                priority, item = download_manager.download_queue.get()
                queue_items.append({
                    'url': item.url,
                    'caption': item.caption,
                    'priority': priority,
                    'status': item.status
                })
                download_manager.download_queue.put((priority, item))
                queue_size -= 1
            
            # Add active downloads
            for url, item in download_manager.active_downloads.items():
                queue_items.append({
                    'url': item.url,
                    'caption': item.caption,
                    'priority': item.priority,
                    'status': 'downloading',
                    'progress': item.progress
                })
            
            # Add failed downloads
            for item in download_manager.failed_downloads:
                queue_items.append({
                    'url': item.url,
                    'caption': item.caption,
                    'priority': item.priority,
                    'status': 'failed',
                    'error': item.error
                })
            
            return jsonify(queue_items)
        except Exception as e:
            web_logger.error(f"Error getting queue data: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @api.route('/queue/data', methods=['POST'])
    def save_queue_data():
        try:
            data = request.json
            
            # Save to CSV file for persistence
            fieldnames = ['url', 'caption', 'priority']
            with open(Config.CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            # Update download manager queue
            download_manager.update_queue_from_csv(Config.CSV_FILE)
            web_logger.info("Queue data saved and updated")
            
            return jsonify({'message': 'Queue updated successfully'})
        except Exception as e:
            web_logger.error(f"Error saving queue data: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @api.route('/status')
    def get_status():
        return jsonify({
            'queue_size': download_manager.get_queue_size(),
            'active_downloads': download_manager.get_active_downloads_count(),
            'failed_downloads': download_manager.get_failed_downloads_count(),
            'paused': download_manager.is_paused(),
            'bandwidth_limit': download_manager.get_bandwidth_limit()
        })

    @api.route('/downloads')
    def get_downloads():
        return jsonify({
            'active': download_manager.get_active_downloads(),
            'failed': download_manager.get_failed_downloads()
        })

    @api.route('/download/start', methods=['POST'])
    def start_download():
        try:
            url = request.json.get('url')
            if not url:
                return jsonify({'error': 'URL is required'}), 400
                
            # Add to queue with high priority to start immediately
            download_manager.add_download(url, priority=1)
            web_logger.info(f"Started download for URL: {url}")
            return jsonify({'message': 'Download started'})
        except Exception as e:
            web_logger.error(f"Error starting download: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @api.route('/download/retry', methods=['POST'])
    def retry_download():
        try:
            url = request.json.get('url')
            if not url:
                return jsonify({'error': 'URL is required'}), 400
                
            download_manager.retry_failed(url)
            web_logger.info(f"Retrying download for URL: {url}")
            return jsonify({'message': 'Download queued for retry'})
        except Exception as e:
            web_logger.error(f"Error retrying download: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @api.route('/download/pause', methods=['POST'])
    def pause_downloads():
        try:
            download_manager.pause()
            web_logger.info("Downloads paused")
            return jsonify({'message': 'Downloads paused'})
        except Exception as e:
            web_logger.error(f"Error pausing downloads: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @api.route('/download/resume', methods=['POST'])
    def resume_downloads():
        try:
            download_manager.resume()
            web_logger.info("Downloads resumed")
            return jsonify({'message': 'Downloads resumed'})
        except Exception as e:
            web_logger.error(f"Error resuming downloads: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    @api.route('/settings', methods=['POST'])
    def update_settings():
        try:
            data = request.json
            if 'bandwidth_limit' in data:
                limit = int(data['bandwidth_limit'])
                download_manager.set_bandwidth_limit(limit)
                web_logger.info(f"Bandwidth limit updated to: {limit} bytes/s")
            return jsonify({'message': 'Settings updated'})
        except Exception as e:
            web_logger.error(f"Error updating settings: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    return api 