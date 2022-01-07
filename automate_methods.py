import logging
from botocore.exceptions import ClientError
from secret import access_key, secret_access_key
import boto3


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name='us-east-1')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

# def check():
#   # To install: pip install requests
#
#     url = create_presigned_url('smarttracmusic', 'Ascend.mp3')
#     if url is not None:
#         return requests.get(url)