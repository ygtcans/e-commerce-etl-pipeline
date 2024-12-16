import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import os
import datetime
import time

# Load .env file
load_dotenv()

class S3Client:
    def __init__(self):
        """
        Initialize the S3Client with AWS credentials and region from environment variables.
        
        Loads AWS credentials and region from environment variables and initializes the 
        boto3 S3 client.

        Args:
            None
        """
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_REGION')

        # Initialize AWS S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def list_buckets(self) -> list:
        """
        List all S3 buckets in the AWS account.
        
        Retrieves the list of all available S3 buckets and logs their names. If no buckets 
        are found, an appropriate message is logged.

        Returns:
            list: A list of bucket objects, each containing details of the buckets.
        """
        try:
            response = self.s3_client.list_buckets()
            buckets = response.get('Buckets', [])
            if not buckets:
                self.logger.info("No buckets found.")
            else:
                self.logger.info(f"Buckets found: {[bucket['Name'] for bucket in buckets]}")
            return buckets
        except (NoCredentialsError, PartialCredentialsError) as e:
            self.logger.error(f"Credentials error: {e}")
        except EndpointConnectionError as e:
            self.logger.error(f"Network error: {e}")
        except Exception as e:
            self.logger.error(f"Error listing buckets: {e}")

    def upload_file(self, file_path: str, bucket_name: str, object_name: str = None) -> None:
        """
        Upload a single file to an S3 bucket.

        If no object_name is provided, it automatically generates a name by appending 
        the current timestamp to the file name.

        Args:
            file_path (str): Path to the local file to be uploaded.
            bucket_name (str): Name of the S3 bucket where the file will be uploaded.
            object_name (str, optional): The name to assign to the uploaded file in S3. 
            
        Returns:
            None
        """
        try:
            if not object_name:
                # Get the current date and time, formatted as YYYY-MM-DD_HH-MM
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                # Append the date and time to the file name (before extension)
                file_name = file_path.split('/')[-1]
                file_name_without_extension, extension = os.path.splitext(file_name)
                object_name = f"{file_name_without_extension}_{current_time}{extension}"

            self.s3_client.upload_file(file_path, bucket_name, object_name)
            self.logger.info(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
        except FileNotFoundError:
            self.logger.error(f"File '{file_path}' not found.")
        except NoCredentialsError as e:
            self.logger.error(f"Credentials error: {e}")
        except EndpointConnectionError as e:
            self.logger.error(f"Network error: {e}")
        except Exception as e:
            self.logger.error(f"Error uploading file to S3: {e}")

    def upload_files(self, files: list, bucket_name: str) -> None:
        """
        Upload multiple files to an S3 bucket in parallel.

        This method uses a `ThreadPoolExecutor` to upload multiple files concurrently, 
        improving the upload speed when dealing with many files.

        Args:
            files (list): List of file paths to be uploaded.
            bucket_name (str): Name of the S3 bucket where files will be uploaded.

        Returns:
            None
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for file_path in files:
                # Get the current date and time, formatted as YYYY-MM-DD_HH-MM
                current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                # Append the date and time to the file name (before extension)
                file_name = file_path.split('/')[-1]
                file_name_without_extension, extension = os.path.splitext(file_name)
                object_name = f"{file_name_without_extension}_{current_time}{extension}"

                futures.append(executor.submit(self.upload_file, file_path, bucket_name, object_name))
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error during file upload: {e}")


    def download(self, bucket_name: str, destination_dir: str, object_name: str = None, object_prefix: str = None, multiple: bool = False) -> bool:
        """
        Reads data from S3, either a single file or all files with a prefix.

        Args:
            bucket_name (str): The name of the S3 bucket.
            destination_dir (str): The directory to save downloaded files.
            object_name (str, optional): The name of the object to download (if single file).
            object_prefix (str, optional): The prefix of objects to download (if multiple files).
            multiple (bool, optional): Whether to download multiple files.

        Returns:
            bool: True if download is successful, False otherwise.
        """
        try:
            if multiple:
                paginator = self.s3_client.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name, Prefix=object_prefix):
                    for obj in page.get('Contents', []):
                        file_name = obj['Key']
                        local_file_path = os.path.join(destination_dir, file_name)
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                        self.s3_client.download_file(bucket_name, file_name, local_file_path)
                        self.logger.info(f"Downloaded {file_name} to {local_file_path}")
            else:
                local_file_path = os.path.join(destination_dir, object_name)
                self.s3_client.download_file(bucket_name, object_name, local_file_path)
                self.logger.info(f"Downloaded {object_name} to {destination_dir}")

            return True
        except NoCredentialsError:
            self.logger.error("AWS credentials not available.")
        except Exception as e:
            self.logger.error(f"Error downloading from S3: {e}")
        return False




