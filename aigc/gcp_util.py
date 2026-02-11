import logging
import os
from google.cloud import storage
from dotenv import load_dotenv

# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")


class GCPStorageManager:
    """Manage Google Cloud Storage operations."""
    
    def __init__(self, project_id: str = None):
        """
        Initialize the GCP Storage manager.
        
        Args:
            project_id: GCP project ID. If not provided, uses GCP_PROJECT_ID env var
        """
        self.project_id = project_id or GCP_PROJECT_ID
        self.client = storage.Client(project=self.project_id)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized GCPStorageManager with project: {self.project_id}")
    
    def put_file(self, bucket_name: str, local_file_path: str, destination_name: str = None) -> str:
        """
        Upload a media file to a GCS bucket.
        
        Args:
            bucket_name: Name of the GCS bucket
            local_file_path: Local path to the file to upload
            destination_name: Optional destination name in the bucket (if not provided, uses source filename)
            
        Returns:
            Public URL of the uploaded file
            
        Raises:
            FileNotFoundError: If local file does not exist
            Exception: If upload fails
        """
        try:
            # Validate file exists
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"File not found: {local_file_path}")
            
            # Use source filename if no destination name provided
            if destination_name is None:
                destination_name = os.path.basename(local_file_path)
            
            self.logger.info(f"Uploading {local_file_path} to gs://{bucket_name}/{destination_name}")
            
            # Get bucket and blob
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_name)
            
            # Upload file
            blob.upload_from_filename(local_file_path)
            
            # Make file public (optional, remove if you want private files)
            blob.make_public()
            
            public_url = blob.public_url
            self.logger.info(f"File uploaded successfully: {public_url}")
            
            return public_url
            
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error uploading file to GCS: {str(e)}")
            raise
    
    def delete_file(self, bucket_name: str, blob_name: str) -> bool:
        """
        Delete a file from a GCS bucket.
        
        Args:
            bucket_name: Name of the GCS bucket
            blob_name: Name of the blob/file to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            self.logger.info(f"Deleting gs://{bucket_name}/{blob_name}")
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            
            self.logger.info(f"File deleted successfully: {blob_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file from GCS: {str(e)}")
            raise
    
    def list_files(self, bucket_name: str, prefix: str = None) -> list:
        """
        List files in a GCS bucket.
        
        Args:
            bucket_name: Name of the GCS bucket
            prefix: Optional prefix to filter files
            
        Returns:
            List of blob names in the bucket
        """
        try:
            self.logger.info(f"Listing files in gs://{bucket_name}")
            
            bucket = self.client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            
            file_list = [blob.name for blob in blobs]
            self.logger.info(f"Found {len(file_list)} files in bucket")
            
            return file_list
            
        except Exception as e:
            self.logger.error(f"Error listing files in GCS: {str(e)}")
            raise
