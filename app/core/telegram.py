import os
from typing import Optional, Callable
from pyrogram import Client, errors
from pyrogram.types import Message
from pyrogram.errors import RPCError, UnknownError, AuthKeyUnregistered, SessionPasswordNeeded
from pyrogram.enums import ParseMode
from app.core.logger import main_logger
from app.config import Config

class TelegramNotifier:
    def __init__(self):
        self.enabled = Config.TELEGRAM_ENABLED
        if self.enabled:
            try:
                session_file = os.path.join(Config.SESSION_DIR, Config.TELEGRAM_SESSION_NAME)
                self.client = Client(
                    name=session_file,
                    api_id=Config.TELEGRAM_API_ID,
                    api_hash=Config.TELEGRAM_API_HASH,
                    phone_number=Config.TELEGRAM_PHONE,
                    workdir=Config.SESSION_DIR
                )
                self.chat_id = Config.TELEGRAM_CHAT_ID
                main_logger.info("Telegram notifications enabled")
            except Exception as e:
                self.enabled = False
                self.client = None
                main_logger.error(f"Failed to initialize Telegram client: {str(e)}")
        else:
            self.client = None
            main_logger.info("Telegram notifications disabled")

    async def start(self):
        """Start the Pyrogram client"""
        if not self.enabled or not self.client:
            return False

        try:
            await self.client.start()
            me = await self.client.get_me()
            main_logger.info(f"Telegram client started successfully as {me.first_name}")
            
            # Verify chat_id is valid
            try:
                await self.client.get_chat(self.chat_id)
            except RPCError as e:
                main_logger.error(f"Invalid chat_id {self.chat_id}: {str(e)}")
                self.enabled = False
                await self.stop()
                return False
                
            return True
        except SessionPasswordNeeded:
            main_logger.error("Two-factor authentication required. Please disable it or use session string.")
            self.enabled = False
            return False
        except AuthKeyUnregistered:
            main_logger.error("Session expired. Please remove the session file and restart.")
            self.enabled = False
            return False
        except Exception as e:
            main_logger.error(f"Failed to start Telegram client: {str(e)}")
            self.enabled = False
            return False

    async def stop(self):
        """Stop the Pyrogram client"""
        if self.enabled and self.client:
            try:
                await self.client.stop()
                main_logger.info("Telegram client stopped")
            except Exception as e:
                main_logger.error(f"Error stopping Telegram client: {str(e)}")

    async def send_message(self, message: str, reply_to: Optional[int] = None) -> Optional[int]:
        """Send a message via telegram"""
        if not self.enabled or not self.client:
            return None
            
        try:
            msg = await self.client.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=reply_to,
                disable_web_page_preview=True
            )
            return msg.id
        except RPCError as e:
            main_logger.error(f"Failed to send telegram message: {str(e)}")
            return None

    async def notify_download_started(self, url: str, caption: str = "") -> Optional[int]:
        """Notify when a download starts"""
        message = f"📥 Download Started\n<b>URL:</b> {url}"
        if caption:
            message += f"\n<b>Caption:</b> {caption}"
        return await self.send_message(message)

    async def notify_download_completed(self, url: str, caption: str = "", file_path: str = None, reply_to: Optional[int] = None) -> None:
        """Notify when a download completes and optionally send the file"""
        message = f"✅ Download Completed\n<b>URL:</b> {url}"
        if caption:
            message += f"\n<b>Caption:</b> {caption}"
        
        # First send the completion message
        msg_id = await self.send_message(message, reply_to)
        
        # If file path is provided and exists, send the file
        if file_path and os.path.exists(file_path) and self.enabled:
            try:
                # Calculate file size
                file_size = os.path.getsize(file_path)
                if file_size > 2000 * 1024 * 1024:  # 2GB limit for Telegram
                    await self.send_message(
                        f"⚠️ File too large to send via Telegram ({file_size/(1024*1024*1024):.1f} GB)",
                        msg_id
                    )
                    return

                progress_message = await self.send_message("📤 Uploading file to Telegram...")
                
                async def progress(current: int, total: int):
                    if total > 0:
                        percentage = (current * 100) / total
                        try:
                            await self.client.edit_message_text(
                                chat_id=self.chat_id,
                                message_id=progress_message,
                                text=f"📤 Uploading: {percentage:.1f}% ({current/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)"
                            )
                        except RPCError:
                            pass  # Ignore errors from too many edits

                await self.client.send_document(
                    chat_id=self.chat_id,
                    document=file_path,
                    caption=caption or url,
                    progress=progress,
                    reply_to_message_id=msg_id,
                    force_document=True  # Always send as file, not media
                )
                
                # Delete the progress message
                try:
                    await self.client.delete_messages(self.chat_id, progress_message)
                except RPCError:
                    pass
                
            except RPCError as e:
                error_msg = f"Failed to send file via Telegram: {str(e)}"
                main_logger.error(error_msg)
                await self.send_message(f"❌ {error_msg}", msg_id)

    async def notify_download_failed(self, url: str, error: str, caption: str = "", reply_to: Optional[int] = None) -> None:
        """Notify when a download fails"""
        message = f"❌ Download Failed\n<b>URL:</b> {url}\n<b>Error:</b> {error}"
        if caption:
            message += f"\n<b>Caption:</b> {caption}"
        await self.send_message(message, reply_to)

    async def edit_message(self, message_id: int, new_text: str) -> bool:
        """Edit an existing message"""
        if not self.enabled or not self.client:
            return False
            
        try:
            await self.client.edit_message_text(
                chat_id=self.chat_id,
                message_id=message_id,
                text=new_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            return True
        except RPCError as e:
            main_logger.error(f"Failed to edit telegram message: {str(e)}")
            return False

    def is_enabled(self) -> bool:
        """Check if notifications are enabled and client is ready"""
        return self.enabled and self.client is not None

# Create a global instance
notifier = TelegramNotifier() 