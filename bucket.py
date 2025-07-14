import boto3
from django.conf import settings
import os

class Bucket:
    '''
    ArvanCloud bucket manager

    initializes the connection to the s3-compatible Arvan storages.
    '''

    def __init__(self):
        session = boto3.session.Session()
        self.connection = session.client(
            service_name=settings.AWS_SERVICE_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def get_bucket_objects(self):
        response = self.connection.list_objects_v2(Bucket=self.bucket_name)
        return response.get('Contents', [])
    
    def delete_bucket_object(self, key):
        self.connection.delete_object(Bucket=self.bucket_name, Key=key)
        return True
    
    def download_bucket_object(self, key):
        local_path = os.path.join(settings.AWS_LOCAL_STORAGE, key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True) 
        with open(local_path, 'wb') as f:
            self.connection.download_fileobj(self.bucket_name, key, f)
        return True

    def update_bucket_object(self, key, local_path):
        with open(local_path, 'rb') as f:
            self.connection.upload_fileobj(f, self.bucket_name, key)
        os.remove(local_path)
        return True

                     
bucket = Bucket()

