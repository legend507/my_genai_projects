import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import logging
import time

# Config models.
IMAGE_MODEL = 'gemini-3-pro-image-preview'
AUDIO_MODEL = ''
VIDEO_MODEL = 'veo-3.1-generate-preview'

# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
# From my corp account, intercom-connector-prod project.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiContentGenerator():
    def __init__(self):
        """Initialize the Gemini client with API key."""
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    def image_gen(self, prompt: str, output_path: str = None) -> str:
        """
        Generate an image from a text prompt using Gemini.
        
        Args:
            prompt: Text description of the image to generate
            output_path: Optional file path to save the generated image
            
        Returns:
            Image URL or file path
        """
        try:
            self.logger.info(f"Generating image with prompt: {prompt}")
            
            response = self.client.models.generate_content(
                model=IMAGE_MODEL,
                contents=[prompt],
            )
            
            for part in response.parts:
                if part.text is not None:
                    self.logger.info(part.text)
                elif part.inline_data is not None:
                    image = part.as_image()
                    image.save("generated_image.png")
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise
    
    def audio_gen(self, prompt: str, output_path: str = None) -> str:
        """
        Generate audio content from a text prompt using Gemini.
        
        Args:
            prompt: Text description or script for audio generation
            output_path: Optional file path to save the generated audio file
            
        Returns:
            Audio file path or reference
        """
        try:
            self.logger.info(f"Generating audio with prompt: {prompt}")
            
            response = self.client.models.generate_content(
                model=AUDIO_MODEL,
                contents=f"Generate a script or narration for the following request: {prompt}"
            )
            
            audio_content = response.text
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(audio_content)
                self.logger.info(f"Audio content saved to {output_path}")
                return output_path
            
            self.logger.info("Audio content generated successfully")
            return audio_content
            
        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            raise
    
    def video_gen(self, prompt: str, output_path: str = None) -> str:
        """
        Generate video content from a text prompt using Gemini.
        
        Args:
            prompt: Text description or scenario for video generation
            output_path: Optional file path to save the video reference/script
            
        Returns:
            Video file path or reference
        """
        try:
            self.logger.info(f"Generating video with prompt: {prompt}")
            
            response = self.client.models.generate_content(
                model=VIDEO_MODEL,
                contents=f"Generate a detailed video script and storyboard for the following request: {prompt}"
            )
            
            video_content = response.text
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(video_content)
                self.logger.info(f"Video script saved to {output_path}")
                return output_path
            
            self.logger.info("Video content generated successfully")
            return video_content
            
        except Exception as e:
            self.logger.error(f"Error generating video: {str(e)}")
            raise
        