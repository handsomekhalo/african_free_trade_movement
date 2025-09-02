import boto3
import pathlib
from django.conf import settings
from botocore.exceptions import ClientError
import mimetypes



def get_backblaze_client():
    return boto3.client(
        's3',
        # endpoint_url='https://s3.us-west-004.backblazeb2.com',  # Your Backblaze S3 endpoint
        endpoint_url='https://s3.us-east-005.backblazeb2.com',  # Your Backblaze S3 endpoint

        aws_access_key_id=settings.BACK_BLAZE_KEY_ID,
        aws_secret_access_key=settings.BACK_BLAZE_APLLICATION_KEY,
        region_name='us-east-005'

    )


def upload_to_backblaze_s3(file, file_name, company_name=None):
    """
    Uploads a file to Backblaze B2 bucket with the correct content type for inline viewing.
    """
    bucket = settings.BACK_BLAZE_BUCKET_NAME
    folder = company_name or "default"
    key = f"{folder}/{file_name}"

    # Guess content type
    content_type, _ = mimetypes.guess_type(file_name)
    content_type = content_type or 'application/octet-stream'

    try:
        s3 = get_backblaze_client()
        s3.upload_fileobj(
            file,
            bucket,
            key,
            ExtraArgs={'ContentType': content_type}
        )
        return f"https://s3.us-east-005.backblazeb2.com/{bucket}/{key}"
    except ClientError as e:
        print(f"[UPLOAD ERROR] {e}")
        return None
    
def open_back_blaze_s3_file(filepath):
    """
    Generates a presigned URL for a file stored on Backblaze B2 that allows inline viewing.
    """
    bucket = settings.BACK_BLAZE_BUCKET_NAME
    s3 = get_backblaze_client()

    # Convert FieldFile to string and extract key
    filepath_str = str(filepath)
    if filepath_str.startswith("http") and bucket in filepath_str:
        key = filepath_str.split(f"{bucket}/")[-1]
    elif bucket not in filepath_str:
        # Already a key (not a full URL)
        key = filepath_str
    else:
        key = filepath_str.split(f"{bucket}/")[-1]

    # Guess content type
    suffix = pathlib.Path(key).suffix.lower()
    content_type_mapping = {
        ".pdf": "application/pdf",
        ".mp4": "video/mp4",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".txt": "text/plain",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    content_type = content_type_mapping.get(suffix, "application/octet-stream")

    # Check if file exists before generating URL
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        print(f"[HEAD ERROR] {e}")
        return filepath_str  # Return original if file not found

    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ResponseContentDisposition': 'inline',
                'ResponseContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        return url
    except ClientError as e:
        print(f"[PRESIGN ERROR] {e}")
        return filepath_str
# def upload_to_backblaze_s3(file, file_name):
#     """
#     Upload file to Backblaze B2 bucket.
#     """
#     path = settings.COMPANY_PATH  # Optional subfolder logic
#     s3_file_name = f"{path}/{file_name}"
#     bucket_name = settings.BACK_BLAZE_BUCKET_NAME

#     s3 = get_backblaze_client()

#     try:
#         s3.upload_fileobj(file, bucket_name, s3_file_name)

#         # Construct the B2 public URL
#         s3_url = f"https://s3.us-west-004.backblazeb2.com/{bucket_name}/{s3_file_name}"
#         return s3_url

#     except ClientError as e:
#         print(f"Upload error: {e}")
#         return None
# def upload_to_backblaze_s3(file, file_name, company_name=None):
#     path = company_name or "default"

#     print('path',path)
#     s3_file_name = f"{path}/{file_name}"

#     s3 = get_backblaze_client()
#     print('s3',s3)

#     bucket_name = settings.BACK_BLAZE_BUCKET_NAME

#     s3.upload_fileobj(file, bucket_name, s3_file_name)

#     s3_url = f"https://s3.us-east-005.backblazeb2.com/{bucket_name}/{s3_file_name}"
#     return s3_url
# # def open_back_blaze_s3_file(filepath):
#     """
#     Generate a presigned URL for viewing a file from Backblaze B2.
#     """
#     bucket = settings.BACK_BLAZE_BUCKET_NAME
    
#     # Debug: Print the original filepath
#     print(f"Original filepath: {filepath}")
    
#     # If the filepath doesn't contain the bucket name, it might already be just the key
#     if bucket not in str(filepath):
#         # If it's already a URL, return as is
#         if str(filepath).startswith('http'):
#             return filepath
#         # If it's just a key/path, use it directly
#         file_path = str(filepath)
#     else:
#         # Extract the key from the full S3 URL
#         file_path = str(filepath).split(f"{bucket}/")[-1]
    
#     # Debug: Print the extracted file path
#     print(f"Extracted file_path (key): {file_path}")
    
#     # Get content type based on file extension
#     content_type = "application/octet-stream"
#     suffix = pathlib.Path(file_path).suffix.lower()
    
#     content_type_mapping = {
#         ".pdf": "application/pdf",
#         ".mp4": "video/mp4",
#         ".jpg": "image/jpeg",
#         ".jpeg": "image/jpeg",
#         ".png": "image/png",
#         ".gif": "image/gif",
#         ".txt": "text/plain",
#         ".doc": "application/msword",
#         ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#         ".xls": "application/vnd.ms-excel",
#         ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     }
    
#     content_type = content_type_mapping.get(suffix, "application/octet-stream")
    
#     try:
#         s3 = get_backblaze_client()
        
#         # First, verify the object exists
#         try:
#             s3.head_object(Bucket=bucket, Key=file_path)
#             print(f"Object exists: {bucket}/{file_path}")
#         except ClientError as e:
#             print(f"Object not found: {bucket}/{file_path}, Error: {e}")
#             return filepath
        
#         # Generate presigned URL
#         url = s3.generate_presigned_url(
#             ClientMethod='get_object',
#             Params={
#                 'Bucket': bucket,
#                 'Key': file_path,
#                 "ResponseContentDisposition": "inline",
#                 "ResponseContentType": content_type
#             },
#             ExpiresIn=3600  # 1 hour
#         )
        
#         print(f"Generated presigned URL: {url}")
#         return url
        
#     except ClientError as e:
#         error_code = e.response.get('Error', {}).get('Code', 'Unknown')
#         error_message = e.response.get('Error', {}).get('Message', str(e))
#         print(f"ClientError - Code: {error_code}, Message: {error_message}")
#         logger.error(f"Presign error for {file_path}: {e}")
#         return filepath
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         logger.error(f"Unexpected error generating presigned URL for {file_path}: {e}")
#         return filepath

# Alternative function to test Backblaze connection
def test_backblaze_connection():
    """Test function to verify Backblaze connection and bucket access"""
    try:
        s3 = get_backblaze_client()
        bucket = settings.BACK_BLAZE_BUCKET_NAME
        
        # List objects in bucket (limit to 1 to test access)
        response = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        print(f"Successfully connected to bucket: {bucket}")
        print(f"Bucket contents sample: {response.get('Contents', [])}")
        return True
        
    except ClientError as e:
        print(f"Failed to connect to Backblaze: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error connecting to Backblaze: {e}")
        return False

# def open_back_blaze_s3_file(filepath):
    """
    Generate a presigned URL for viewing a file from Backblaze B2.
    """
    bucket = settings.BACK_BLAZE_BUCKET_NAME
    if bucket not in str(filepath):
        return filepath

    s3 = get_backblaze_client()
    file_path = str(filepath).split(f"{bucket}/")[-1]

    content_type = "application/octet-stream"
    suffix = pathlib.Path(file_path).suffix.lower()

    if suffix == ".pdf":
        content_type = "application/pdf"
    elif suffix == ".mp4":
        content_type = "video/mp4"

    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': file_path,
                "ResponseContentDisposition": "inline",
                "ResponseContentType": content_type
            },
            ExpiresIn=3600
        )
        return url
    except ClientError as e:
        print(f"Presign error: {e}")
        return filepath

# def upload_to_backblaze_s3(file, file_name, company_name=None):
    # path = company_name or "default"
    # s3_file_name = f"{path}/{file_name}"
    # bucket_name = settings.BACK_BLAZE_BUCKET_NAME
    # s3 = get_backblaze_client()

    # content_type, _ = mimetypes.guess_type(file_name)
    # extra_args = {'ContentType': content_type or 'application/octet-stream'}

    # s3.upload_fileobj(file, bucket_name, s3_file_name, ExtraArgs=extra_args)

    # return f"https://s3.us-east-005.backblazeb2.com/{bucket_name}/{s3_file_name}"
def delete_s3_file(filepath):
    """
    Delete a file from Backblaze B2.
    """
    bucket = settings.BACK_BLAZE_BUCKET_NAME
    file_name = str(filepath).split(f"{bucket}/")[-1]

    s3 = get_backblaze_client()

    try:
        s3.delete_object(Bucket=bucket, Key=file_name)
        return True
    except ClientError as e:
        print(f"Delete error: {e}")
        return False
