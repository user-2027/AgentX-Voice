"""GCP integration utilities."""
import os
from typing import Optional, Dict, Any
from google.cloud import firestore
from google.cloud import storage
from google.cloud import logging as cloud_logging
from config import config


class GCPIntegration:
    """GCP integration for Firestore, Storage, and Logging."""
    
    def __init__(self):
        """Initialize GCP clients."""
        self.project_id = config.GCP_PROJECT_ID
        self.firestore_client: Optional[firestore.Client] = None
        self.storage_client: Optional[storage.Client] = None
        self.logging_client: Optional[cloud_logging.Client] = None
        
        if self.project_id:
            try:
                self._initialize_clients()
            except Exception as e:
                print(f"Warning: GCP initialization failed: {e}")
                print("Running in mock mode without GCP integration")
    
    def _initialize_clients(self):
        """Initialize GCP client connections."""
        if self.project_id:
            # Initialize Firestore
            self.firestore_client = firestore.Client(
                project=self.project_id,
                database=config.FIRESTORE_DATABASE
            )
            
            # Initialize Cloud Storage
            self.storage_client = storage.Client(project=self.project_id)
            
            # Initialize Cloud Logging
            self.logging_client = cloud_logging.Client(project=self.project_id)
    
    def save_interaction(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """
        Save interaction data to Firestore.
        
        Args:
            collection: Firestore collection name
            document_id: Document ID
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.firestore_client:
            return False
        
        try:
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"Error saving to Firestore: {e}")
            return False
    
    def get_interaction(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve interaction data from Firestore.
        
        Args:
            collection: Firestore collection name
            document_id: Document ID
            
        Returns:
            Document data or None
        """
        if not self.firestore_client:
            return None
        
        try:
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error retrieving from Firestore: {e}")
            return None
    
    def upload_report(self, bucket_name: str, blob_name: str, content: bytes) -> bool:
        """
        Upload report to Cloud Storage.
        
        Args:
            bucket_name: GCS bucket name
            blob_name: Blob name/path
            content: File content as bytes
            
        Returns:
            True if successful, False otherwise
        """
        if not self.storage_client:
            return False
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(content)
            return True
        except Exception as e:
            print(f"Error uploading to Cloud Storage: {e}")
            return False
    
    def log_to_cloud(self, severity: str, message: str, **kwargs):
        """
        Log to Cloud Logging.
        
        Args:
            severity: Log severity (INFO, WARNING, ERROR, etc.)
            message: Log message
            **kwargs: Additional log data
        """
        if not self.logging_client:
            return
        
        try:
            logger = self.logging_client.logger("call-center-system")
            logger.log_text(
                message,
                severity=severity,
                **kwargs
            )
        except Exception as e:
            print(f"Error logging to Cloud: {e}")
    
    def is_configured(self) -> bool:
        """Check if GCP is properly configured."""
        return (
            self.project_id is not None and
            self.firestore_client is not None
        )


# Global GCP integration instance
gcp_integration = GCPIntegration()

