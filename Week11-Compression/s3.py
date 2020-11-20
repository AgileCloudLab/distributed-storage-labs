import utils
import logging
import io

import boto3
from botocore.exceptions import ClientError

def s3_list_buckets(region):
    """
    Retrieve the list of existing buckets

    :param region: 
    :return: A list of Bucket dictionaries
    """

    try:
        s3_client = boto3.client('s3', region_name=region)
        response = s3_client.list_buckets()
        return response['Buckets']
    except ClientError as cle:
        logging.error("Boto3 error listing S3 buckets in region %s: %s", region, cle)
        return False
    except Exception as e:
        logging.error(e)
        return False
#

def s3_create_bucket(bucket_name, region):
    """
    Create an S3 bucket in a specified region

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    try:
        s3_client = boto3.client('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(
            Bucket=bucket_name, 
            CreateBucketConfiguration=location)
        return True
    except ClientError as cle:
        logging.error("Boto3 error creating bucket %s in region %s: %s" % (bucket_name, region, cle))
        return False
    except Exception as e:
        logging.error(e)
        return False
#

def s3_upload_object(data, bucket_name, object_key, content_type):
    """
    Upload a new Object to an S3 bucket

    :param data: The object data
    :param object_key: S3 object key.
    :param bucket: Bucket to upload to
    :param content_type: MIME type of the object data 
    :return: True if object was uploaded, else False
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.upload_fileobj(
            io.BytesIO(data),
            bucket_name, object_key, 
            ExtraArgs={'ContentType': content_type})
        return True
    except ClientError as cle:
        logging.error("Boto3 error uploading object %s/%s: %s" % (bucket_name, object_key, cle))
        return False
    except Exception as e:
        logging.error(e)
        return False
#

def s3_download_object(region, bucket_name, object_key):
    s3_client = boto3.client('s3', region)
    try:
        s3_response_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        object_content = s3_response_object['Body'].read()
        return bytearray(object_content)
    except ClientError as e:
        logging.error("Boto3 error downloading object %s/%s: %s" % (bucket_name, object_key, cle))
        return False
    except Exception as e:
        logging.error(e)
        return False
#
    

def store_file(data, region, content_type):
    """
    Upload the file to AWS S3, to the given region

    :param data: The binary file contents
    :param region: S3 Region code (e.g. us-east-2), must be one of the valid codes listed at https://docs.aws.amazon.com/general/latest/gr/s3.html
    :para content_type: The MIME type of the file, will be set as the Content-Type metadata field of the S3 object
    :return: The bucket name and random generated object key that identifies the uploaded file   
    """

    if len(data) > 5*1E9:
        # We will use the simple upload endpoint that supports data below 5 GB. 
        # Above it we'd have to use the more complicated multipart upload, which 
        # we do not implement now.
        raise ValueError("Data too large for S3 simple upload. Please select a file under 5 GB!")

    # Check if there is a bucket in the target region, create if not
    buckets = s3_list_buckets(region)
    logging.info("Buckets in the %s region: \n%s" % (region, buckets))
    if not buckets:
        # There are no buckets in this region, create one 
        # (uppercase characters not allowed)
        bucket_name = "au-ds-lab-10-{randstring}".format(
            randstring=utils.random_string(10).lower()
        )
        print("Creating bucket %s" % bucket_name)
        if not s3_create_bucket(bucket_name, region):
            # Failed to create the bucket :(
            return False
        print("Done.")
    else:
        # There is a bucket in this region
        bucket_name = buckets[0]['Name']
    print("Bucket in %s region: %s" % (region, bucket_name))

    # Generate a long random object key for the file (uppercase characters not allowed)
    object_key = utils.random_string(20).lower()

    # Upload the data 
    if not s3_upload_object(data, bucket_name, object_key, content_type):
        return False

    return bucket_name, object_key
#

def get_file(region, bucket_name, object_key):
    """
    Download a file stored in S3

    :param region: AWS region code where the bucket is located
    :param bucket_name: The bucket name where the file is stored
    :param object_key: Key of the object within the bucket that stores the file contents
    :return: The downloaded file contents
    """

    # Download the object
    data = s3_download_object(region, bucket_name, object_key)
    return data
#
