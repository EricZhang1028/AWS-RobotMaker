import boto3

def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    rekognition = boto3.client('rekognition')
    
    # The bucket store faces.
    bucket_name = '<YOUR_BUCKET_NAME>'
    bucket = s3.Bucket(bucket_name)
    # All of the faces image in the 'photos' folder.
    objs = bucket.objects.filter(Prefix = 'photos')
    
    # Create rekognition collection if not exist.
    collection_name = '<YOUR_COLLECTION>'
    collection_list = rekognition.list_collections()
    if collection_name not in collection_list['CollectionIds']:
        response = rekognition.create_collection(
            CollectionId = collection_name
        )

    # Retrieve each photo.
    for obj in objs:
        # Get file extension.
        file_extension = obj.key.split('.')[-1]
        # Get face name
        face_name = obj.key.split('/')[-1].split('.')[0]
        
        # Check file extension.
        if file_extension in ['jpg', 'jpeg', 'png']:
            
            # Build index face in collection.
            rekognition.index_faces(
                CollectionId = collection_name,
                Image = {
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': obj.key
                    }
                },
                ExternalImageId = face_name,
                DetectionAttributes = ['ALL']
            )
    
    # List all of face.
    face_list = rekognition.list_faces(
        CollectionId = collection_name,
        MaxResults = 123
    )
    print(face_list)
    
    # ---------Create stream processor
    response = rekognition.create_stream_processor(
        Input = {
            'KinesisVideoStream':{
                'Arn': '<YOUR_VIDEO_STREAM_ARN>'
            }
        },
        Output={
            'KinesisDataStream': {
                'Arn': '<YOUR_DATA_STREAM_ARN>'
            }
        },
        Name='RobomakerProcessor',
        Settings={
            'FaceSearch': {
                'CollectionId': collection_name,
                'FaceMatchThreshold': 70.0
            }
        },
        RoleArn='<YOUR_ROLE_ARN>'
    )
    print(response)