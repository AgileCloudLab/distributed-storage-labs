import utils


def store_file(data, region):
    """
    Upload the file to AWS S3, to the given region

    :param data: The binary file contents
    :param region: S3 Region code (e.g. us-east-2), must be one of the valid codes listed at https://docs.aws.amazon.com/general/latest/gr/s3.html
    :return: The bucket name and random generated object key that identifies the uploaded file   
    """

    if len(data) > 5*1E9:
        # We will use the simple upload endpoint that supports data below 5 GB. 
        # Above it we'd have to use the more complicated multipart upload, which we do not implement now.
        raise ValueError("Data too large for S3 simple upload. Please select a file under 5 GB!")

    # Generate a long random object key for the file
    object_key = utils.random_string(20)

    # Check if we have a bucket in the requested region
    bucket_name = "files-{}".format(region)

    # TODO check if the target bucket exists, create if not

    # TODO upload the data 

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

    # TODO download the object

    data = bytearray([])
    return data
#