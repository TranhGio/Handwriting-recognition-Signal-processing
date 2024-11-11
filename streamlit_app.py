import streamlit as st
import numpy as np
import cv2
from PIL import Image
import pyperclip
from streamlit_cropper import st_cropper


import module.process_image as dip
import ocr_app as ocr
import module.crop_text_line as SegmentImg


def init_session_var():
    if 'MODEL_OPTION' not in st.session_state:
        st.session_state.MODEL_OPTION = None

    if 'MODEL_INPUT' not in st.session_state:
        st.session_state.MODEL_INPUT = None

    if 'PREDICTION_STR' not in st.session_state:
        st.session_state.PREDICTION_STR = None

    if 'PREDICTION_MUL' not in st.session_state:
        st.session_state.PREDICTION_MUL = None

    if 'OPENCV_IMAGE' not in st.session_state:
        st.session_state.OPENCV_IMAGE = None

    if 'OLD_DIL' not in st.session_state:
        st.session_state.OLD_DIL = None

    if 'OLD_ERO' not in st.session_state:
        st.session_state.OLD_ERO = None

    if 'RESIZE_ENABLE' not in st.session_state:
        st.session_state.RESIZE_ENABLE = None

    if 'SIZE_PREDICT' not in st.session_state:
        st.session_state.SIZE_PREDICT = None

    if 'MULTILINE' not in st.session_state:
        st.session_state.MULTILINE = None

    if 'SEGMENTS_IMG' not in st.session_state:
        st.session_state.SEGMENTS_IMG = None

    if 'SEGMENTS_ARR' not in st.session_state:
        st.session_state.SEGMENTS_ARR = None

    if 'SEGMENTS_PRS' not in st.session_state:
        st.session_state.SEGMENTS_PRS = None

    # st.session_state.OLD_ERO = 0
    # st.session_state.OLD_DIL = 0


def reset():

    st.session_state.MODEL_OPTION = None
    st.session_state.MODEL_INPUT = None
    st.session_state.PREDICTION_STR = None
    st.session_state.PREDICTION_MUL = None
    st.session_state.OPENCV_IMAGE = None
    st.session_state.OLD_DIL = None
    st.session_state.OLD_ERO = None
    st.session_state.RESIZE_ENABLE = None
    st.session_state.SIZE_PREDICT = None
    st.session_state.MULTILINE = None
    st.session_state.SEGMENTS_IMG = None
    st.session_state.SEGMENTS_ARR = None
    st.session_state.SEGMENTS_PRS = None
    st.rerun()


def main():
    # init session state
    init_session_var()

    st.set_page_config(
        'Vietnamese Handwritten Recognition (OCR)', './img_streamlit/logo.ico')
    message_container = st.empty()
    st.title("Vietnamese Handwritten Recognition")
    st.markdown('<div style="margin-top:2rem"></div>',
                unsafe_allow_html=True)  # Insert a blank line
    # st.markdown('<p style="text-align: justify; font-size:20px;">Hướng dẫn sử dụng: Upload ảnh cần nhận diện sau đó chọn xử lý ảnh đầu vào.' +
    #             ' Người dùng có thể thay đổi kích thước (resize) hoặc sử dụng phép co giãn (erosion/dilation) để tăng mức độ chính xác,' +
    #             ' ngoài ra sau khi dự đoán người dùng có thể chỉnh sửa kết quả cho chính xác hơn.</p>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:2rem"></div>', unsafe_allow_html=True)

    IMAGE_UPLOAD = st.file_uploader(
        "Allowed formats: JPG, PNG, JPEG - resolution 2200x200", type=['png', 'jpg', 'jpeg'])
    # Display image
    if IMAGE_UPLOAD is not None:
        st.image(IMAGE_UPLOAD, caption='Image uploaded', use_container_width=True)
        if st.session_state.RESIZE_ENABLE == True:

            img = Image.open(IMAGE_UPLOAD)
            cropped_img = st_cropper(
                img, realtime_update=True, box_color='#0000FF', aspect_ratio=None)
            np_image = np.asarray(cropped_img)
            # Chuyển đổi định dạng hình ảnh từ RGB sang BGR
            st.session_state.OPENCV_IMAGE = cv2.cvtColor(
                np_image, cv2.COLOR_RGB2BGR)

            if st.button("Cancel"):
                st.session_state.RESIZE_ENABLE = False
                st.rerun()
        else:
            if st.button("Resize"):
                st.session_state.MODEL_INPUT = None
                st.session_state.RESIZE_ENABLE = True
                st.rerun()

    processed_image_container = st.empty()
    if st.session_state.MODEL_INPUT is not None and st.session_state.SEGMENTS_IMG is None:
        processed_image_container.image(st.session_state.MODEL_INPUT,
                                        caption='Processed Image')

    if st.session_state.MODEL_INPUT is None and st.session_state.SEGMENTS_IMG is not None:
        processed_image_container.image(st.session_state.SEGMENTS_IMG,
                                        caption='Processed Image')

    st.markdown('<div style="margin-top:2rem"></div>', unsafe_allow_html=True)
    st.header("Result")
    st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)

    if st.session_state.PREDICTION_STR is not None:
        st.text(
            "Click [Copy and reset]")
        st.session_state.PREDICTION_STR = st.text_input(
            "Kết quả dự đoán", st.session_state.PREDICTION_STR)
        if st.button("Copy and reset", type="secondary", key=123):
            pyperclip.copy(st.session_state.PREDICTION_STR)
            st.session_state.IMG_DATA = None
            st.session_state.MODEL_INPUT = None
            st.session_state.PREDICTION_STR = None
            st.rerun()

    if st.session_state.PREDICTION_MUL is not None:
        st.text(
            "Click [Copy and reset] để sao chép và reset lại toàn bộ ứng dụng")
        st.session_state.PREDICTION_MUL = st.text_area(
            "Kết quả dự đoán", value=st.session_state.PREDICTION_MUL, height=400)
        if st.button("Copy and reset", type="secondary", key=345):
            pyperclip.copy(st.session_state.PREDICTION_MUL)
            st.session_state.IMG_DATA = None
            st.session_state.MODEL_INPUT = None
            st.session_state.SIZE_PREDICT = None
            st.session_state.PREDICTION_MUL = None
            st.session_state.OPENCV_IMAGE = None
            st.rerun()

    # Sidebar
    with st.sidebar:

        st.title("Functional")
        st.session_state.MULTILINE = st.checkbox('Multiple segment')

        if st.sidebar.button("Image processing", type="primary"):
            # Xử lý khi nút [Tự động xử lý ảnh] được nhấn

            if IMAGE_UPLOAD is not None:

                if st.session_state.RESIZE_ENABLE is None or st.session_state.RESIZE_ENABLE == False:

                    img_array = np.frombuffer(IMAGE_UPLOAD.read(), np.uint8)
                    st.session_state.OPENCV_IMAGE = cv2.imdecode(
                        img_array, cv2.IMREAD_COLOR)

                # segmentation if check multiline
                if (st.session_state.MULTILINE is not None and st.session_state.MULTILINE == True):
                    st.session_state.SEGMENTS_IMG, st.session_state.SEGMENTS_ARR = SegmentImg.segmentation_text_line(
                        st.session_state.OPENCV_IMAGE)
                    # get model and size
                    st.session_state.MODEL_INPUT, st.session_state.SEGMENTS_PRS, st.session_state.SIZE_PREDICT = dip.process_multi(
                        st.session_state.SEGMENTS_ARR)
                    # display
                    with processed_image_container.container():
                        st.image(
                            st.session_state.SEGMENTS_IMG, caption='Processed image')
                        i = 0
                        for img_prs in st.session_state.SEGMENTS_PRS:

                            st.image(img_prs, 'Segments: {}'.format(i))
                            i += 1
                else:
                    st.session_state.MODEL_INPUT = dip.process_image(
                        st.session_state.OPENCV_IMAGE)
                    processed_image_container.image(
                        dip.process_image(st.session_state.OPENCV_IMAGE), caption='Processed image')
                # process_image if no option checked

            else:
                message_container.error('Please upload image')

        if st.sidebar.button("Reset"):
            reset()
            st.rerun()

        #  # Giá trị của slider 1
        # param1 = st.sidebar.slider(
        #     "Erosion", 1, 8, 1, help="Increase or decrease kernel", key=1)
        # if (st.session_state.MODEL_INPUT is not None
        #         and st.session_state.OLD_ERO != param1 and st.session_state.MULTILINE == False):
        #     st.session_state.OLD_ERO = param1
        #     st.session_state.MODEL_INPUT = dip.erosion_dilation_image(st.session_state.MODEL_INPUT,
        #                                                               param1, True)
        #     processed_image_container.image(st.session_state.MODEL_INPUT)
        #
        # # Giá trị của slider 2
        # param2 = st.sidebar.slider(
        #     "Dilation", 1, 8, 1, help="Increase or decrease kernel", key=2)
        # if (st.session_state.MODEL_INPUT is not None
        #         and st.session_state.OLD_DIL != param2 and st.session_state.MULTILINE == False):
        #     st.session_state.OLD_DIL = param2
        #     st.session_state.MODEL_INPUT = dip.erosion_dilation_image(st.session_state.MODEL_INPUT,
        #                                                               param2, False)
        #     processed_image_container.image(st.session_state.MODEL_INPUT)

        option = st.selectbox('Model selection',
                              ('CRNN + LTSM + CTC', 'TransformerOCR'))
        if st.sidebar.button("Proceed to recognition", type="primary"):
            if (option == 'CRNN + LTSM + CTC'):
                # Xử lý khi nút [Nhận diện văn bản] được nhấn
                if st.session_state.MODEL_INPUT is not None:

                    if st.session_state.MULTILINE:
                        processed_image_container.image(st.session_state.SEGMENTS_IMG,
                                                        caption='Processed image')
                        with processed_image_container.container():
                            st.image(
                                st.session_state.SEGMENTS_IMG, caption='Processed image')
                            i = 0
                            for img_prs in st.session_state.SEGMENTS_PRS:
                                st.image(img_prs, 'Segments: {}'.format(i))
                                i += 1
                        st.session_state.PREDICTION_MUL = ocr.prediction_multiline(st.session_state.MODEL_INPUT,
                                                                                   st.session_state.SIZE_PREDICT)
                    else:
                        processed_image_container.image(
                            st.session_state.MODEL_INPUT, caption='Processed image')
                        # Dự đoán chuỗi
                        st.session_state.PREDICTION_STR = ocr.prediction_ocr_crnn_ctc(
                            dip.convert_img_to_input(st.session_state.MODEL_INPUT))
                    st.rerun()
                else:
                    message_container.error(
                        'Please upload image')
            else:
                if IMAGE_UPLOAD is not None:
                    if st.session_state.MULTILINE:
                        with processed_image_container.container():
                            st.image(
                                st.session_state.SEGMENTS_IMG, caption='Processed image')
                            i = 0
                            for img_prs in st.session_state.SEGMENTS_PRS:
                                st.image(img_prs, 'Segments: {}'.format(i))
                                i += 1
                        st.session_state.PREDICTION_MUL = ocr.prediction_ocr_vietocr_mul(
                            st.session_state.SEGMENTS_ARR)
                    else:
                        image = Image.open(IMAGE_UPLOAD)
                        st.session_state.PREDICTION_STR = ocr.prediction_ocr_vietocr(
                            image)
                    st.rerun()
                else:
                    message_container.error(
                        'Please upload image')

        st.title("Members")
        st.text("23MSE33006 - Nguyễn Đăng Vĩnh")
        st.text("23MSE33009 - Hoàng Chí Nhân")
        st.title("Professor: Dr. Nguyễn Thị Khánh Hồng")


if __name__ == "__main__":
    main()
