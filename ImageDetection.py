#Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
import json

def detect_faces(photo, bucket):

    client=boto3.client('rekognition')

    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},Attributes=['ALL'])

    print('Detected faces for ' + photo)    
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low']) 
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')

        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))

		# Access predictions for individual face details and print them
        print("Gender: " + str(faceDetail['Gender']))
        print("Smile: " + str(faceDetail['Smile']))
        print("Eyeglasses: " + str(faceDetail['Eyeglasses']))
        print("Emotions: " + str(faceDetail['Emotions'][0]))

    return len(response['FaceDetails'])

def compare_faces(sourceFile, targetFile):

    client=boto3.client('rekognition')
   
    imageSource=open(sourceFile,'rb')
    imageTarget=open(targetFile,'rb')

    response=client.compare_faces(SimilarityThreshold=80,
                                  SourceImage={'Bytes': imageSource.read()},
                                  TargetImage={'Bytes': imageTarget.read()})
    
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        print('The face at ' +
               str(position['Left']) + ' ' +
               str(position['Top']) +
               ' matches with ' + similarity + '% confidence')

    imageSource.close()
    imageTarget.close()     
    return len(response['FaceMatches'])  

def moderate_image(photo, bucket):

    client=boto3.client('rekognition')

    response = client.detect_moderation_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}})

    print('Detected labels for ' + photo)    
    for label in response['ModerationLabels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))
        print (label['ParentName'])
    return len(response['ModerationLabels'])


def violence_detection(photo, bucket):

    client=boto3.client('rekognition')

    response = client.detect_moderation_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
    
    violence_count = 0
    violence_list = []
    violence_conf = 0
    violence_conf_list = []
    
    for label in response['ModerationLabels']:
        
        if 'Violence' in label['Name'] or 'Violence' in label['ParentName']:
            violence_count += 1
            violence_list.append(label['Name'])
            violence_conf_list.append(label['Confidence'])

    if len(violence_conf_list):
        violence_conf = max(violence_conf_list)
    else:
        violence_conf = 0
        
    return violence_count, violence_conf



import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor

def show_faces(photo,bucket):
     

    client=boto3.client('rekognition')

    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)
    
    #Call DetectFaces 
    response = client.detect_faces(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        Attributes=['ALL'])

    imgWidth, imgHeight = image.size  
    draw = ImageDraw.Draw(image)  
                    

    # calculate and display bounding boxes for each detected face       
    print('Detected faces for ' + photo)    
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low']) 
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        
        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
                

        print('Left: ' + '{0:.0f}'.format(left))
        print('Top: ' + '{0:.0f}'.format(top))
        print('Face Width: ' + "{0:.0f}".format(width))
        print('Face Height: ' + "{0:.0f}".format(height))

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)

        )
        draw.line(points, fill='#00d400', width=2)

        # Alternatively can draw rectangle. However you can't set line width.
        #draw.rectangle([left,top, left + width, top + height], outline='#00d400') 

    image.show()

    return len(response['FaceDetails'])
    

def detect_faces2(client, photo, bucket):

    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},Attributes=['ALL'])
    return len(response['FaceDetails'])




# def main():
#     photo=''
#     bucket='6770-project'
#     face_count=detect_faces(photo, bucket)
#     print("Faces detected: " + str(face_count))

# def main():
#     photo='Linux.png'
#     bucket='6770-project'
#     client = boto3.client('rekognition')
#     face_count=detect_faces2(client, photo, bucket)
#     if face_count:
#         print("Faces detected: " + str(face_count))
#     else:
#         print('No face detected.')

# def main():
#     source_file='vids/buffer/target.jpg'
#     target_file='vids/12-01-2021-19-44-13.jpg'
#     face_matches=compare_faces(source_file, target_file)
#     print("Face matches: " + str(face_matches))

# def main():
#     bucket="6770-project"
#     photo="12-01-2021-19-44-13.jpg"

#     faces_count=show_faces(photo,bucket)
#     print("faces detected: " + str(faces_count))

def main():
    photo='2021-12-05-180834_pic.jpg'
    photo = 'weapon2.jpeg'
    bucket='6770-project'
    label_count, prob=violence_detection(photo, bucket)
    print("Labels detected: " + str(label_count), '\nProbability: ' + str(prob))


if __name__ == "__main__":
    main()