import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import controller.userController as usrc
import av  
from PIL import Image
import torch
import numpy as np
import time

usrc.create()
@st.cache
def model():
    return torch.hub.load('ultralytics/yolov5', 'custom', path="best.pt",force_reload=True) 

model=model()
class VideoProcessor:
    def _init_(self):
        self.res=None
        self.confidence=0.5

    def getRes(self):
        #time.sleep(5)
        return self.res

    def recv(self, frame):
 
        model.conf=self.confidence
        img = frame.to_ndarray(format="bgr24")
        
        # vision processing
        flipped = img[:, ::-1, :]

        # model processing
        im_pil = Image.fromarray(flipped)
        results = model(im_pil, size=112)
        self.res=results
        bbox_img = np.array(results.render()[0])

        
        return av.VideoFrame.from_ndarray(bbox_img, format="bgr24")

st.title("Cold Drinks Inventory Management System")

modes=['None','Staff','Admin']
option=st.selectbox('Mode',modes)

if option=='Staff':
    st.title('Staff')

    with st.sidebar:
        date = st.date_input('Date')

        confidence=st.slider('Confidence threshold',0.00,1.00,0.8)

        vmodes=['📹video','📊data','🖼️image']
        view_mode=st.radio('View Mode',vmodes)

        if view_mode=='📊data':
            dmodes=['None','Excel','CSV']
            download_mode=st.radio('Download Mode',dmodes)

    with st.container():
        if view_mode=='📊data':
            st.title('📊data')

            table=usrc.read()
            st.table(table)
            count=usrc.count_drinks()
            st.table(count)

            if download_mode=='CSV':
                usrc.csvformat(table)
                st.write('Data is written successfully to CSV File.')

            if download_mode=='Exel':
                usrc.excelformat(table)
                st.write('Data is written successfully to Excel File.')

        if view_mode=='🖼️image':
            st.title("🖼️ Object detection image")
            image=st.file_uploader('Image',type=['png','jpg','jpeg'])
            if image:
                model.conf=confidence
                img = np.array(Image.open(image))

                # model processing
                im_pil = Image.fromarray(img)
                results = model(im_pil, size=112)
                bbox_img = np.array(results.render()[0])
                st.image(bbox_img, caption=f"Processed image", use_column_width=True,)
                
                count = results.pandas().xyxy[0]['name'].value_counts()
                with st.sidebar:
                    count
                if(st.button('Store')):
                    for row in count.index:
                        usrc.insert(date,row,int(count[row]))
    

        if view_mode=='📹video':
            st.title('📹Object detection video')

            RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            
            webrtc_ctx = webrtc_streamer(
                key="webcam",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                video_processor_factory=VideoProcessor,
                async_processing=True,
            )
            if webrtc_ctx.state.playing:
                    webrtc_ctx.video_processor.confidence=confidence
            if st.checkbox('Show the detected labels'):
                empty=st.empty()
                store=st.button('Store')
                if webrtc_ctx.state.playing:
                    while True:
                        if webrtc_ctx.video_processor:
                            result = webrtc_ctx.video_processor.getRes()
                            if result!= None:
                                count = result.pandas().xyxy[0]['name'].value_counts()
                                empty.write(count)
                                for row in count.index:
                                    if store:
                                        usrc.insert(date,row,int(count[row]))
                                        time.sleep(5)
                            else:
                                empty.write("No labels detected")  
                        else:
                            break
                            
 else:
    st.header("Admin")
    choice=['View inventory','update product','delete product','Create user']
    mode=st.selectbox(" ",choice)
    if mode=='View inventory':
        table=usrc.read()
        st.table(table)
        count=usrc.count_drinks()
        st.table(count)
