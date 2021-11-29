import boto3, logging, os, threading, sys
from botocore.exceptions import ClientError



class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def upload_file(s3_client, file_path, object_name=None, key=None, bucket='6770-project'):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if key is None:
        key = {}

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_path
    try:
        response = s3_client.meta.client.upload_file(file_path, bucket, object_name, ExtraArgs={'Metadata': key}, Callback=ProgressPercentage(file_path))
        print()
    except ClientError as e:
        logging.error(e)
        return False
    return True

def upload_file2(s3_client, file_name, bucket, object_name=None):    
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    # s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(file_name))
        print('\n')
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == '__main__':
    # print('a')


    s3_client = boto3.client('s3')

    # print('a')
    for bucket in s3_client.buckets.all():
        print(bucket.name)

    # s3.meta.client.upload_file('/tmp/hello.txt', 'mybucket', 'hello.txt')

    # data = open('vids/Linux.png', 'rb')
    # file_path = 'vids/Linux.png'
    # s3_client.Bucket('6770-project').put_object(Key='cactus.jpg', Body=data)
    
    print('Uploading image...')  
    upload_file2(s3_client, 'vids/11-28-2021-21-49-09.avi', '6770-project')