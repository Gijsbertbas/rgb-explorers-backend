import boto3
import io
import pickle

S3_BUCKET_NAME = 's3-rgb-explorers'


def send_instance(input_data, s3_name):
    s3 = boto3.resource("s3")
    serialized = pickle.dumps(input_data)
    s3.Object(S3_BUCKET_NAME, s3_name).put(Body=serialized)


def read_instance(s3_input_name):
    s3 = boto3.resource("s3")
    mem_file = io.BytesIO()
    s3.Bucket(S3_BUCKET_NAME).download_fileobj(s3_input_name, mem_file)
    return pickle.load(mem_file)


# if __name__ == '__main__':
#     import numpy
#     o = numpy.ones(10, dtype=numpy.int64)
#     send_instance(o, "test-numpy-ones")
#     read_instance("test-numpy-ones")
