# import json
# import urllib.parse
import boto3
from botocore.exceptions import ClientError



TARGETIMAGE = 'target.jpg'


def send_email(bucket, key, violence_prob=0):
    """
    Send email to the house owner
    Inputs:
    - bucket: name of the s3 bucket storing pics and videos
    - key: the name of the file
    - mode: '1' is normal mode, '2' means violence detected
    """
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    SENDER = "HouseNotificationSystem <sunxhbill@gmail.com>"
    
    RECIPIENT = "xs2445@columbia.edu"
    
    AWS_REGION = "us-east-2"
    
    # The subject line for the email.
    SUBJECT = "Project-6770-test"
    
    # Create a new SES resource and specify a region.
    email_client = boto3.client('ses',region_name=AWS_REGION)
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Received video</h1>
      <p>Your AWS S3 bucket {bucket} received an object {object}.</p>
    </body>
    </html>
    """.format(bucket=bucket, object=key)         
    
    response = email_client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
        
    return response
    
    

def detect_faces(client, photo, bucket):
    try:
        response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},Attributes=['ALL']) 
        return len(response['FaceDetails'])
    except ClientError as e:
        print(e.response['Error']['Message'])
    
    
def compare_faces(client, photo, bucket):
    try:
        response = client.compare_faces(
            SourceImage={'S3Object':{'Bucket':bucket,'Name':photo}}, 
            TargetImage={'S3Object':{'Bucket':bucket,'Name':TARGETIMAGE}}
            )
        return len(response['UnmatchedFaces'])
    except ClientError as e:
        print(e.response['Error']['Message'])


def violence_detect(client, photo, bucket):
    try:

        response = client.detect_moderation_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
    
        violence_count = 0
        violence_list = []
        violence_conf_list = []
        
        for label in response['ModerationLabels']:
            
            if 'Violence' in label['Name'] or 'Violence' in label['ParentName']:
                violence_count += 1
                violence_list.append(label['Name'])
                violence_conf_list.append(label['Confidence'])
        
        if len(violence_conf_list):
            violence_prob = max(violence_conf_list)
        else:
            violence_prob = 0
                
        return violence_count, violence_prob
        
    except ClientError as e:
        print(e.response['Error']['Message'])


def face_analysis(client, photo, bucket):
    try:
    
        faces_count = 0
        stranger_count = 0
        violence_count = 0
        violence_prob = 0
        
        # see if there is a face in the frame
        # we need to do that because compare_faces function will report an error if there is no face detected
        faces_count = detect_faces(client, photo, bucket)
        # if there is face detected
        if faces_count:
            # compare faces in the pic to see if there are strangers
            stranger_count = compare_faces(client, photo, bucket)
            # if there are strangers, detect offensive contents
            if stranger_count:
                # detect weapons or violence behaviors
                violence_count, violence_prob = violence_detect(client, photo, bucket)
                
        return faces_count, stranger_count, violence_count, violence_prob
        
    except ClientError as e:
        print(e.response['Error']['Message'])



# def lambda_handler(event, context):
if __name__ == '__main__':
    
    rek = boto3.client('rekognition')


    # Get the object from the event and show its content type
    bucket = '6770-project'
    key = '12-02-2021-18-56-56_vid.avi'
    prefix_pic = key[:-7]
    
    # print(face_analysis(rek, 'weapon2.jpeg', bucket))
    # face_analysis(rek, 'weapon2.jpeg', bucket)
    
    

    for i in range(6):
        # images uploaded with the video
        pic_name = prefix_pic + 'pic_' + str(i) + '.jpg'
        print(pic_name)
        faces_count, stranger_count, violence_count, violence_prob = face_analysis(rek, pic_name, bucket)
        if violence_count:
            print('violence_detected!')
            # response = send_email(bucket, key, violence_prob)
            break
        else:
            print(faces_count, stranger_count)
