from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

import streamlit as st

from PIL import Image
from PIL import ImageDraw

import time
import io


subscription_key = st.secrets['subscription_key']
endpoint = st.secrets['endpoint']

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

st.title('OCR')
uploaded_file = st.file_uploader('Chose an image...', type=['jpg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    draw = ImageDraw.Draw(img)
    # uploaded_fileをbaytes型に変更してバイナリーデータを取ってくる。
    bytes_data = uploaded_file.getvalue()
    # バイナリーデータをbaytesIO型に変更
    bytes_io = io.BytesIO(bytes_data)

    text = []

    read_response = computervision_client.read_in_stream(bytes_io, raw=True)
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower() not in ['notstarted', 'running']:
            break
        st.write('Waiting for result...')
        time.sleep(10)

    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                text.append(line.text)
                draw.rectangle([(min(line.bounding_box[0],line.bounding_box[6]) , min(line.bounding_box[1], line.bounding_box[3])), (max(line.bounding_box[2], line.bounding_box[4]), max(line.bounding_box[5],line.bounding_box[7]))],
                               fill=None, outline='green', width=5)
    st.image(img)

    text_line = '  \n'.join(text)
    st.markdown('**認識されたテキスト**')
    st.markdown(f'{text_line}')