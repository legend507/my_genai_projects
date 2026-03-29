import logging
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

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

        # Model names.
        self.GEMINI_AUDIO = "lyria-3-pro-preview"
        self.GEMINI_VIDEO = "veo-3.1-generate-preview"
    
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
            
            response = self.client.models.generate_images(
                model="imagen-3.0-generate-001",
                prompt=prompt,
                number_of_images=1,
                safety_filter_level="block_none",
            )
            
            image_url = response.generated_images[0].gcs_uri
            self.logger.info(f"Image generated successfully: {image_url}")
            
            if output_path:
                # Save image URL to file or download
                with open(output_path, 'w') as f:
                    f.write(f"Generated Image URL:\n{image_url}\n")
                self.logger.info(f"Image reference saved to {output_path}")
            
            return image_url
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise
    
    def audio_gen(self, prompt: str, output_path: str = None) -> str:
        """
        Generate audio content from a text prompt using Gemini.
        This generates a mp3 file, but NOT a mp4 that can directly be uploaded to YouTube.
        
        Args:
            prompt: Text description or script for audio generation
            output_path: Optional file path to save the generated audio file
            
        Returns:
            Audio file path or reference
        """
        try:
            self.logger.info(f"Generating audio with prompt: {prompt}")
            
            response = self.client.models.generate_content(
                model=self.GEMINI_AUDIO,
                contents=f"Create a 3 minutes audio with the following description: {prompt}",
                config=types.GenerateContentConfig(response_modalities=["AUDIO", "TEXT"],),
            )
            
            # Lyria model responses needs special parsing.
            lyrics = []
            audio_data = None

            for part in response.parts:
                if part.text is not None:
                    lyrics.append(part.text)
                elif part.inline_data is not None:
                    audio_data = part.inline_data.data
           
           # Only save the audio to mp4 file, ignore the lyrics.
            if output_path:
                # Write binary audio data to file
                with open(output_path+".mp4", 'wb') as f:
                    f.write(audio_data)
                self.logger.info(f"Audio content saved to {output_path}")
                return output_path
            
            self.logger.info("Audio content generated successfully")
            return audio_data
            
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
            
            operation = self.client.models.generate_videos(
                model=self.GEMINI_VIDEO,
                prompt=f"Generate a video with the following description: {prompt}"
            )
            
            while not operation.done:
                self.logger.info("Waiting for video generation to complete...")
                time.sleep(10)  # Poll every 10 seconds
                operation = self.client.operations.get(operation)
            
            # Download the generated video content.
            generated_video = operation.response.generated_videos[0]
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(output_path+".mp4")
            self.logger.info(f"Generated video saved to {output_path}.mp4")
            
        except Exception as e:
            self.logger.error(f"Error generating video: {str(e)}")
            raise


if __name__ == "__main__":

    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is not set.")

    generator = GeminiContentGenerator()
    output = "test"

    prompt = ("An epic cinematic orchestral piece about a journey home. "
              "Starts with a solo piano intro, builds through sweeping "
              "strings, and climaxes with a massive wall of sound.")

    # result = generator.image_gen(prompt, output)
    result = generator.video_gen(prompt, output)
    # result = generator.video_gen(prompt, output)

    print(result)
