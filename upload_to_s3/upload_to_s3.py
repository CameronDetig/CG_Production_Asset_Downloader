import os
import boto3
import argparse
from botocore.exceptions import NoCredentialsError

def upload_directory(local_dir, bucket_name, s3_prefix=""):
    s3 = boto3.client('s3')
    
    print(f"Starting upload from '{local_dir}' to bucket '{bucket_name}'...")
    
    files_to_upload = []
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            files_to_upload.append(os.path.join(root, file))

    total_files = len(files_to_upload)
    print(f"Found {total_files} files to upload.")

    for i, local_path in enumerate(files_to_upload):
        # Calculate S3 Key
        relative_path = os.path.relpath(local_path, local_dir)
        # Verify path separators for S3 (always /)
        s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")
        
        print(f"[{i+1}/{total_files}] Uploading {relative_path} -> s3://{bucket_name}/{s3_key}")
        
        try:
            s3.upload_file(local_path, bucket_name, s3_key)
        except NoCredentialsError:
            print("Error: AWS credentials not found. Please run 'aws configure'.")
            return
        except Exception as e:
            print(f"Failed to upload {local_path}: {e}")

    print("Upload complete!")


def main():
    parser = argparse.ArgumentParser(description="Upload a directory to an S3 bucket.")
    parser.add_argument("bucket", help="Name of the S3 bucket")
    parser.add_argument("--dir", default="spring_assets", help="Local directory to upload (default: spring_assets)")
    parser.add_argument("--prefix", default="spring_project", help="S3 prefix (folder) to upload into")

    args = parser.parse_args()
    
    if not os.path.exists(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist.")
        return

    upload_directory(args.dir, args.bucket, args.prefix)

if __name__ == "__main__":
    main()
