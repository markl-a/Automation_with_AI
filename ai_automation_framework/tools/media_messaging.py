"""Image processing, OCR, and messaging platform tools."""

from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any, List, Optional
import requests
import json
from pathlib import Path
import base64
import io


class ImageProcessingTool:
    """Tool for image processing and manipulation."""

    @staticmethod
    def resize_image(
        input_path: str,
        output_path: str,
        width: int,
        height: int,
        maintain_aspect: bool = True
    ) -> Dict[str, Any]:
        """
        Resize an image.

        Args:
            input_path: Input image path
            output_path: Output image path
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio

        Returns:
            Result dictionary
        """
        try:
            img = Image.open(input_path)
            original_size = img.size

            if maintain_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)

            img.save(output_path)

            return {
                "success": True,
                "original_size": original_size,
                "new_size": img.size,
                "output": output_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def convert_format(
        input_path: str,
        output_path: str,
        format: str = "PNG"
    ) -> Dict[str, Any]:
        """Convert image to different format."""
        try:
            img = Image.open(input_path)
            img.save(output_path, format=format.upper())

            return {
                "success": True,
                "input": input_path,
                "output": output_path,
                "format": format
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def apply_filter(
        input_path: str,
        output_path: str,
        filter_type: str = "BLUR"
    ) -> Dict[str, Any]:
        """
        Apply filter to image.

        Args:
            input_path: Input image
            output_path: Output image
            filter_type: Filter type (BLUR, SHARPEN, EDGE_ENHANCE, etc.)

        Returns:
            Result
        """
        try:
            img = Image.open(input_path)

            filters = {
                "BLUR": ImageFilter.BLUR,
                "SHARPEN": ImageFilter.SHARPEN,
                "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
                "SMOOTH": ImageFilter.SMOOTH,
                "DETAIL": ImageFilter.DETAIL
            }

            if filter_type.upper() in filters:
                filtered = img.filter(filters[filter_type.upper()])
                filtered.save(output_path)

                return {
                    "success": True,
                    "filter": filter_type,
                    "output": output_path
                }
            else:
                return {"success": False, "error": f"Unknown filter: {filter_type}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def adjust_brightness(
        input_path: str,
        output_path: str,
        factor: float = 1.5
    ) -> Dict[str, Any]:
        """Adjust image brightness (factor: 0.0 to 2.0)."""
        try:
            img = Image.open(input_path)
            enhancer = ImageEnhance.Brightness(img)
            enhanced = enhancer.enhance(factor)
            enhanced.save(output_path)

            return {
                "success": True,
                "brightness_factor": factor,
                "output": output_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def create_thumbnail(
        input_path: str,
        output_path: str,
        size: tuple = (128, 128)
    ) -> Dict[str, Any]:
        """Create image thumbnail."""
        try:
            img = Image.open(input_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path)

            return {
                "success": True,
                "thumbnail_size": img.size,
                "output": output_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """Get image metadata."""
        try:
            img = Image.open(image_path)

            return {
                "success": True,
                "size": img.size,
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class OCRTool:
    """OCR (Optical Character Recognition) tool."""

    @staticmethod
    def extract_text_from_image(image_path: str) -> Dict[str, Any]:
        """
        Extract text from image using OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        try:
            import pytesseract

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)

            return {
                "success": True,
                "text": text.strip(),
                "char_count": len(text),
                "line_count": len(text.splitlines())
            }
        except ImportError:
            return {
                "success": False,
                "error": "pytesseract not installed. Install with: pip install pytesseract"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def extract_text_from_pdf(pdf_path: str, page_num: int = 0) -> Dict[str, Any]:
        """Extract text from PDF page."""
        try:
            from pdf2image import convert_from_path
            import pytesseract

            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)

            if images:
                text = pytesseract.image_to_string(images[0])
                return {
                    "success": True,
                    "page": page_num,
                    "text": text.strip()
                }
            else:
                return {"success": False, "error": "Could not convert PDF page"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class SlackTool:
    """Slack integration tool."""

    def __init__(self, webhook_url: str = None, token: str = None):
        """
        Initialize Slack tool.

        Args:
            webhook_url: Slack webhook URL
            token: Slack bot token
        """
        self.webhook_url = webhook_url
        self.token = token

    def send_message(
        self,
        message: str,
        channel: str = None,
        username: str = "Bot"
    ) -> Dict[str, Any]:
        """
        Send message to Slack.

        Args:
            message: Message text
            channel: Channel name (if using token)
            username: Bot username

        Returns:
            Result
        """
        try:
            if self.webhook_url:
                payload = {
                    "text": message,
                    "username": username
                }
                response = requests.post(self.webhook_url, json=payload)
                response.raise_for_status()

                return {
                    "success": True,
                    "message": "Message sent via webhook",
                    "status_code": response.status_code
                }
            elif self.token and channel:
                headers = {"Authorization": f"Bearer {self.token}"}
                data = {
                    "channel": channel,
                    "text": message
                }
                response = requests.post(
                    "https://slack.com/api/chat.postMessage",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()

                return {
                    "success": True,
                    "message": "Message sent via API",
                    "response": response.json()
                }
            else:
                return {"success": False, "error": "No webhook URL or token provided"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_file(
        self,
        file_path: str,
        channel: str,
        title: str = None
    ) -> Dict[str, Any]:
        """Upload file to Slack channel."""
        try:
            if not self.token:
                return {"success": False, "error": "Token required for file upload"}

            headers = {"Authorization": f"Bearer {self.token}"}

            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'channels': channel,
                    'title': title or Path(file_path).name
                }

                response = requests.post(
                    "https://slack.com/api/files.upload",
                    headers=headers,
                    files=files,
                    data=data
                )
                response.raise_for_status()

                return {
                    "success": True,
                    "response": response.json()
                }

        except Exception as e:
            return {"success": False, "error": str(e)}


class DiscordTool:
    """Discord integration tool."""

    def __init__(self, webhook_url: str = None):
        """
        Initialize Discord tool.

        Args:
            webhook_url: Discord webhook URL
        """
        self.webhook_url = webhook_url

    def send_message(
        self,
        content: str,
        username: str = "Bot",
        avatar_url: str = None
    ) -> Dict[str, Any]:
        """
        Send message to Discord.

        Args:
            content: Message content
            username: Bot username
            avatar_url: Avatar URL

        Returns:
            Result
        """
        try:
            payload = {
                "content": content,
                "username": username
            }

            if avatar_url:
                payload["avatar_url"] = avatar_url

            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

            return {
                "success": True,
                "message": "Message sent to Discord",
                "status_code": response.status_code
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_embed(
        self,
        title: str,
        description: str,
        color: int = 0x00ff00,
        fields: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send embed message to Discord."""
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color
            }

            if fields:
                embed["fields"] = fields

            payload = {"embeds": [embed]}

            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

            return {
                "success": True,
                "message": "Embed sent to Discord"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Tool schemas
MEDIA_MESSAGING_SCHEMAS = {
    "resize_image": {
        "type": "function",
        "function": {
            "name": "resize_image",
            "description": "Resize an image",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {"type": "string"},
                    "output_path": {"type": "string"},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"}
                },
                "required": ["input_path", "output_path", "width", "height"]
            }
        }
    },
    "send_slack_message": {
        "type": "function",
        "function": {
            "name": "send_slack_message",
            "description": "Send message to Slack",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        }
    }
}
