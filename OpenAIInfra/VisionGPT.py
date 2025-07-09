from typing import List, Dict
import base64

from configs import ChatConfig, VisionConfig
from open_ai_infra import OpenAIInfra


class VisionGPT(OpenAIInfra):
    """Specialized client for vision and image analysis tasks."""

    def __init__(self, config: ChatConfig):
        # Force vision-capable model
        if not isinstance(config, VisionConfig):
            vision_config = VisionConfig(
                api_key=config.api_key,
                model="gpt-4o",
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                max_retries=config.max_retries,
                memory_size=config.memory_size
            )
        else:
            vision_config = config

        super().__init__(vision_config)
        self.blocked_domains = [
            "istockphoto.com",
            "shutterstock.com",
            "gettyimages.com",
            "adobe.com",
            "dreamstime.com",
            "123rf.com"
        ]

    def analyze_image(self, image_url: str, prompt: str = "Describe this image in detail") -> str:
        """Analyze an image with optional custom prompt."""
        return self.send_vision_message(prompt, image_url)

    def extract_text(self, image_url: str) -> str:
        """Extract text from an image (OCR)."""
        prompt = "Extract all visible text from this image. Provide the text exactly as it appears, maintaining formatting where possible."
        return self.send_vision_message(prompt, image_url)

    def describe_scene(self, image_url: str) -> str:
        """Get a detailed scene description."""
        prompt = "Provide a detailed description of the scene in this image, including objects, people, setting, colors, mood, and any activities taking place."
        return self.send_vision_message(prompt, image_url)

    def identify_objects(self, image_url: str) -> str:
        """Identify and list objects in the image."""
        prompt = "List and identify all objects, people, animals, and items visible in this image. Be specific and detailed."
        return self.send_vision_message(prompt, image_url)

    def analyze_document(self, image_url: str) -> str:
        """Analyze a document image."""
        prompt = "Analyze this document image. Extract the text content, identify the document type, and summarize the key information."
        return self.send_vision_message(prompt, image_url)

    def compare_images(self, image_urls: List[str], prompt: str = "Compare and contrast these images") -> str:
        """Compare multiple images (max 2 for GPT-4V)."""
        if len(image_urls) > 2:
            raise ValueError("GPT-4V supports maximum 2 images per request")

        if len(image_urls) < 2:
            raise ValueError("Need at least 2 images to compare")

        for url in image_urls:
            if not self._is_vision_compatible_url(url):
                raise ValueError(f"Image URL not compatible: {url}")

        content = [{"type": "text", "text": prompt}]

        for i, url in enumerate(image_urls):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": url,
                    "detail": getattr(self.config, 'detail', 'auto')
                }
            })

        messages = [{"role": "user", "content": content}]
        return self._make_request(messages, model="gpt-4o")

    def analyze_chart_or_graph(self, image_url: str) -> str:
        """Analyze charts, graphs, or data visualizations."""
        prompt = """Analyze this chart/graph/data visualization. Provide:
1. Type of chart/graph
2. Key data points and trends
3. Main insights or conclusions
4. Any notable patterns or outliers"""
        return self.send_vision_message(prompt, image_url)

    def describe_for_accessibility(self, image_url: str) -> str:
        """Generate accessibility descriptions for images."""
        prompt = "Create a detailed accessibility description for this image that would help visually impaired users understand its content. Be descriptive but concise."
        return self.send_vision_message(prompt, image_url)

    def analyze_artwork(self, image_url: str) -> str:
        """Analyze artwork or creative images."""
        prompt = """Analyze this artwork. Describe:
1. Style and technique
2. Colors and composition
3. Subject matter and themes
4. Mood and emotional impact
5. Possible artistic movement or influences"""
        return self.send_vision_message(prompt, image_url)

    def send_vision_message(self, prompt: str, image_url: str, model: str = "gpt-4o") -> str:
        """Send a message with image for vision analysis."""
        if not self._is_valid_url(image_url):
            raise ValueError(f"Invalid image URL: {image_url}")

        if not self._is_vision_compatible_url(image_url):
            raise ValueError(f"Image URL not compatible with OpenAI Vision API: {image_url}")

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": getattr(self.config, 'detail', 'auto')
                    }
                }
            ]
        }]

        self.logger.debug(f"Sending vision request to: {image_url}")
        return self._make_request(messages, model=model)

    def send_vision_with_base64(self, prompt: str, image_base64: str, image_format: str = "jpeg") -> str:
        """Send vision message with base64 encoded image."""
        if not image_base64:
            raise ValueError("Base64 image data is required")

        # Ensure proper data URL format
        if not image_base64.startswith("data:image/"):
            image_base64 = f"data:image/{image_format};base64,{image_base64}"

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_base64,
                        "detail": getattr(self.config, 'detail', 'auto')
                    }
                }
            ]
        }]

        return self._make_request(messages, model="gpt-4o")

    def analyze_local_image(self, image_path: str, prompt: str = "Describe this image") -> str:
        """Analyze a local image file by converting it to base64."""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

                # Detect image format from file extension
                image_format = image_path.split('.')[-1].lower()
                if image_format not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    image_format = 'jpeg'  # Default fallback

                return self.send_vision_with_base64(prompt, image_base64, image_format)

        except FileNotFoundError:
            raise ValueError(f"Image file not found: {image_path}")
        except Exception as e:
            raise ValueError(f"Error processing local image: {e}")

    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        return url.startswith(("http://", "https://", "data:image/"))

    def _is_vision_compatible_url(self, url: str) -> bool:
        """Check if URL is compatible with OpenAI Vision API."""
        # Skip validation for data URLs (base64 images)
        if url.startswith("data:image/"):
            return True

        # Check against blocked domains
        return not any(domain in url.lower() for domain in self.blocked_domains)

    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return ["PNG", "JPEG", "JPG", "WEBP", "GIF"]

    def validate_image_url(self, url: str) -> Dict[str, bool]:
        """Validate an image URL and return detailed status."""
        return {
            "is_valid_url": self._is_valid_url(url),
            "is_vision_compatible": self._is_vision_compatible_url(url),
            "is_blocked_domain": any(domain in url.lower() for domain in self.blocked_domains)
        }
