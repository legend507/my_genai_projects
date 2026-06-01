import base64
import logging
import os
import warnings
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s",
)

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MEDIA_DIR = Path(__file__).resolve().parent / "media"

# Model names for media generation. These can be overridden when initializing the OpenAIMediaGenerator.
OPENAI_IMAGE_MODEL = "gpt-image-2"
OPENAI_AUDIO_MODEL = "gpt-4o-mini-tts"
OPENAI_VIDEO_MODEL = "sora-2"   # This is a placeholder name. Sora-2 will be deprecated in Sep.


class OpenAIMediaGenerator:
    """Generate image, audio, and video media with OpenAI models."""

    def __init__(
        self,
        client: OpenAI = None,
        api_key: str = OPENAI_API_KEY,
        image_model: str = OPENAI_IMAGE_MODEL,
        audio_model: str = OPENAI_AUDIO_MODEL,
        video_model: str = OPENAI_VIDEO_MODEL,
    ):
        """Initialize the OpenAI media generator."""
        self.client = client or OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)

        # Model names.
        self.OPENAI_IMAGE = image_model
        self.OPENAI_AUDIO = audio_model
        self.OPENAI_VIDEO = video_model

    def image_gen(
        self,
        prompt: str,
        output_path: str = None,
        size: str = "1024x1024",
        quality: str = "auto",
        storage_backend: str = "local",
        gcp_bucket_name: str = None,
        gcp_destination_name: str = None,
    ) -> Any:
        """
        Generate an image from a text prompt using OpenAI.

        Args:
            prompt: Text description of the image to generate
            output_path: Optional file path to save the generated image
            size: Requested image size
            quality: Requested image quality
            storage_backend: Where to store generated media. Supported: local, gcp
            gcp_bucket_name: Placeholder GCP bucket name
            gcp_destination_name: Placeholder GCP object name

        Returns:
            Output path when saved, otherwise the raw OpenAI response
        """
        try:
            self.logger.info(f"Generating image with prompt: {prompt}")

            response = self.client.images.generate(
                model=self.OPENAI_IMAGE,
                prompt=prompt,
                size=size,
                quality=quality,
            )

            image_data = response.data[0]
            image_bytes = base64.b64decode(image_data.b64_json)

            self.logger.info("Image generated successfully")
            return self.handle_generated_media(
                media_content=image_bytes,
                media_type="image",
                output_path=output_path,
                file_extension=".png",
                storage_backend=storage_backend,
                raw_response=response,
                gcp_bucket_name=gcp_bucket_name,
                gcp_destination_name=gcp_destination_name,
            )

        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise

    def audio_gen(
        self,
        prompt: str,
        output_path: str = None,
        voice: str = "alloy",
        response_format: str = "mp3",
        storage_backend: str = "local",
        gcp_bucket_name: str = None,
        gcp_destination_name: str = None,
    ) -> Any:
        """
        Generate spoken audio from a text prompt using OpenAI.

        Args:
            prompt: Text to turn into speech
            output_path: Optional file path to save the generated audio file
            voice: Voice to use for speech generation
            response_format: Audio file format
            storage_backend: Where to store generated media. Supported: local, gcp
            gcp_bucket_name: Placeholder GCP bucket name
            gcp_destination_name: Placeholder GCP object name

        Returns:
            Output path when saved, otherwise the raw OpenAI response
        """
        try:
            self.logger.info(f"Generating audio with prompt: {prompt}")

            response = self.client.audio.speech.create(
                model=self.OPENAI_AUDIO,
                voice=voice,
                input=prompt,
                response_format=response_format,
            )

            self.logger.info("Audio generated successfully")
            return self.handle_generated_media(
                media_content=response,
                media_type="audio",
                output_path=output_path,
                file_extension=f".{response_format}",
                storage_backend=storage_backend,
                raw_response=response,
                gcp_bucket_name=gcp_bucket_name,
                gcp_destination_name=gcp_destination_name,
            )

        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            raise

    def video_gen(
        self,
        prompt: str,
        output_path: str = None,
        size: str = "1280x720",
        seconds: int = 8,
        poll_interval_seconds: int = 10,
        timeout_seconds: int = 900,
    ) -> Any:
        """
        Placeholder for OpenAI video generation.

        Args:
            prompt: Text description of the video to generate
            output_path: Optional file path to save the generated video
            size: Requested video size
            seconds: Requested video duration in seconds
            poll_interval_seconds: How often to poll for completion
            timeout_seconds: Maximum time to wait for completion

        Returns:
            Warning message explaining that OpenAI video generation is disabled
        """
        message = (
            "OpenAI video generation is currently disabled because OpenAI video "
            "generation models are being deprecated. Use another video provider "
            "or update this method when a supported OpenAI replacement is available."
        )
        self.logger.warning(message)
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        return message

    def handle_generated_media(
        self,
        media_content: Any,
        media_type: str,
        output_path: str = None,
        file_extension: str = None,
        storage_backend: str = "local",
        raw_response: Any = None,
        gcp_bucket_name: str = None,
        gcp_destination_name: str = None,
    ) -> Any:
        """
        Centralized handler for generated media content.

        Args:
            media_content: Generated media bytes, stream, or SDK response
            media_type: Media type label such as image, audio, or video
            output_path: Optional local path for local storage
            file_extension: Extension to append when output_path has no suffix
            storage_backend: Storage destination. Supported: local, gcp
            raw_response: Original SDK response to return when no storage is requested
            gcp_bucket_name: Placeholder GCP bucket name
            gcp_destination_name: Placeholder GCP object name

        Returns:
            Local file path, GCP placeholder message, or generated media response
        """
        if storage_backend == "local":
            if not output_path:
                return raw_response if raw_response is not None else media_content

            path = self._local_media_path(output_path, file_extension)
            self._write_media_to_local_file(media_content, path)
            self.logger.info(f"Generated {media_type} saved to {path}")
            return str(path)

        # Placeholder.
        if storage_backend == "gcp":
            message = (
                "GCP media storage is not implemented yet. "
                f"Requested upload for {media_type} to bucket={gcp_bucket_name}, "
                f"destination={gcp_destination_name}."
            )
            self.logger.warning(message)
            return message

        raise ValueError(f"Unsupported storage_backend: {storage_backend}")

    @staticmethod
    def _write_media_to_local_file(media_content: Any, path: Path) -> None:
        """Write generated media bytes or SDK stream content to a local file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(media_content, bytes):
            path.write_bytes(media_content)
            return

        if hasattr(media_content, "write_to_file"):
            media_content.write_to_file(path)
            return

        if hasattr(media_content, "read"):
            path.write_bytes(media_content.read())
            return

        raise TypeError(f"Unsupported media content type: {type(media_content)}")

    def _local_media_path(self, output_path: str, suffix: str) -> Path:
        """Resolve local media output paths under the default media directory."""
        path = self._with_suffix(output_path, suffix)
        if path.is_absolute():
            return path
        return MEDIA_DIR / path

    @staticmethod
    def _with_suffix(output_path: str, suffix: str) -> Path:
        """Return output_path as a Path with suffix appended when missing."""
        path = Path(output_path)
        if path.suffix or not suffix:
            return path
        return path.with_suffix(suffix)


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    generator = OpenAIMediaGenerator()
    prompt = """
    An avatar image for a creator named Isabell Tiny, in a vibrant and colorful style.
    """

    result = generator.image_gen(prompt, "openai_generated_image")
    print(result)
