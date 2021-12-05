# import json
# import urllib.parse
import boto3
from botocore.exceptions import ClientError
from email_sender import email_raw



TARGETIMAGE = 'target.jpg'
    

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
        return len(response['FaceMatches'])
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
        print('Faces detected: %d' % (faces_count))
        # if there is face detected
        if faces_count:
            # compare faces in the pic to see if there are strangers
            familiar_count = compare_faces(client, photo, bucket)
            # if the house owner is detected then we assume strangers are the house owner's friends.
            if familiar_count:
                stranger_count = 0
            else:
                stranger_count = faces_count - familiar_count
            print('Strangers detected: %d' % (stranger_count))
            # if there are strangers, detect offensive contents
            if stranger_count:
                # detect weapons or violence behaviors
                violence_count, violence_prob = violence_detect(client, photo, bucket)
                print('Violence detected: %d Probability: %d' % (violence_count, violence_prob))

        return faces_count, stranger_count, violence_count, violence_prob
        
    except ClientError as e:
        print(e.response['Error']['Message'])



# def lambda_handler(event, context):
if __name__ == '__main__':
    
    rek = boto3.client('rekognition')


    # Get the object from the event and show its content type
    bucket = '6770-project'
    key = '2021-12-05-173322_vid.avi'
    prefix_pic = key[:-7]
    
    # print(face_analysis(rek, 'weapon2.jpeg', bucket))
    # face_analysis(rek, 'weapon2.jpeg', bucket)
    
    # images uploaded with the video
    pic_name = prefix_pic + 'pic.jpg'
    print(pic_name)
    faces_count, stranger_count, violence_count, violence_prob = face_analysis(rek, pic_name, bucket)
    # stranger_count = 1
    # violence_prob = 0.8
    if stranger_count>0:
        response = email_raw(bucket, key, pic_name, stranger_count, violence_prob)
    else:
        print(faces_count, stranger_count)
