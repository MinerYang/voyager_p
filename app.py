import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import time, json
import threading
from utils.printer import print_label
from utils.logger import logger
from utils.config import get_default_printer

pg = st.navigation([st.Page("admin.py"), st.Page("log.py")])

q_url = 'https://sqs.eu-north-1.amazonaws.com/613860947073/testq'
region_name = 'eu-north-1'

def s3():
    return boto3.client('s3')

def sqs():
    return boto3.client('sqs', region_name=region_name)

def handle_new_file(bucket, key):
    logger.info(f"New file detected: {key}")
    # load printer name
    printer = get_default_printer()
    logger.debug(f"get default printer {printer}")
    # Download file
    local_filename = key.split('/')[-1]
    try:
        s3().download_file(bucket, key, local_filename)
        logger.info(f"Downloaded {local_filename}")
    except Exception as e:
        logger.error(f"Download failed: {e}")
    # Print file
    logger.info(f"start print file {local_filename}")
    success, error = print_label(local_filename, printer)
    if success:
        logger.info(f"Print {local_filename} successfully!")
    else:
        logger.error(f"Print {local_filename} failed with error {error}")


def poll_sqs():
    logger.info("Polling SQS for messages...")
    while True:
        response = sqs().receive_message(
            QueueUrl=q_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=10
        )
        messages = response.get('Messages', [])

        for message in messages:
            body = json.loads(message['Body'])
            # If it's an S3 event, handle it
            if 'Records' in body:
                for record in body['Records']:
                    if record['eventSource'] == 'aws:s3':
                        bucket = record['s3']['bucket']['name']
                        key = record['s3']['object']['key']
                        handle_new_file(bucket, key)

            # Delete the message from the queue
            sqs().delete_message(
                QueueUrl=q_url,
                ReceiptHandle=message['ReceiptHandle']
            )

        time.sleep(1)


# Add sidebar elements
with st.sidebar:
    # Add company info at the top
    st.markdown("### About Info")
    st.markdown("""
    - **Name:** a.a
    - **Version:** 0.0.1
    - **Contact:** me@gmail.com
    """)
    
    # Add a divider
    st.markdown("---")
    
    # Create a container for the image that fills remaining space
    image_container = st.container()
    image_path = "utils/fixtures/fun.jpg"
    with image_container:
        # Use CSS to make the image fill the container
        st.markdown("""
            <style>
            .stImage > div {
                width: 100%;
                height: calc(100vh - 200px);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .stImage > div > img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            </style>
        """, unsafe_allow_html=True)
        st.image(image_path, use_container_width=True)


pg.run()
if 'sqs_thread_started' not in st.session_state:
    st.session_state.sqs_thread_started = True
    thread = threading.Thread(target=poll_sqs, daemon=True)
    thread.start()
    print("Started background SQS poller")


