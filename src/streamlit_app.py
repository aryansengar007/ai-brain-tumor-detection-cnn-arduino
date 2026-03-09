from fpdf import FPDF
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from PIL import Image, ImageEnhance
import io
import time
import zipfile
import os
from datetime import datetime
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Add functions package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import robotics and AI features
from functions.risk_classification import calculate_risk_level, get_signal_description
from functions.serial_comm import safe_send_to_arduino, get_arduino_instance
from functions.qr_generator import generate_mobile_upload_qr, get_local_ip
from functions.email_sender import send_email_report


def save_plot_to_buffer(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", bbox_inches="tight")
    buf.seek(0)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_file.write(buf.read())
    temp_file.close()
    return temp_file.name


def generate_pdf_report(
    filename,
    prediction,
    confidence,
    categories,
    show_metadata,
    metadata,
    show_numpy,
    img_array,
    prediction_probs,
    preprocessed_img,
    grayscale_hist_img,
    prediction_dist_img,
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Brain Tumor Prediction Report", ln=True, align="C")
    pdf.ln(10)

    pdf.image(preprocessed_img, x=55, w=100)
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Prediction: {categories[prediction]}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence: {confidence:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"File: {filename}", ln=True)

    if show_metadata:
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, txt="Image Metadata:", ln=True)
        pdf.set_font("Arial", size=12)
        for k, v in metadata.items():
            pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)

    if show_numpy:
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, txt="Preprocessed Image Array (First 100 Values):", ln=True)
        pdf.set_font("Arial", size=10)
        flat_array_preview = str(img_array[0].flatten()[:100]) + " ..."
        pdf.multi_cell(0, 10, txt=flat_array_preview)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Raw Prediction Probabilities:", ln=True)
    pdf.set_font("Arial", size=12)
    for label, prob in zip(categories, prediction_probs[0]):
        pdf.cell(200, 10, txt=f"{label}: {prob*100:.2f}%", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Greyscale Histogram", ln=True)
    pdf.image(grayscale_hist_img, x=10, w=180)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Prediction Distribution", ln=True)
    pdf.image(prediction_dist_img, x=10, w=180)

    return pdf.output(dest="S").encode("latin1")


st.set_page_config(page_title="Brain Tumor Classifier", layout="wide", page_icon="🧠")
model = load_model(
    r"D:\My Projects\Brain Tumor Project (Robotics_aurdino)\brain_tumor_model.h5"
)
categories = ["Healthy", "Tumor"]

with st.sidebar:
    st.header("🔧 Settings")
    enhance_contrast = st.checkbox("Enhance Contrast", value=True)
    auto_resize = st.checkbox("Auto Resize to 128x128", value=True)
    show_numpy = st.checkbox("Show Preprocessed Array", value=False)
    show_metadata = st.checkbox("Show Image Metadata", value=True)
    show_original = st.checkbox("Show Original Image", value=True)
    show_dimensions = st.checkbox("Show Image Dimensions", value=False)
    flip_horizontal = st.checkbox("Flip Image Horizontally", value=False)
    flip_vertical = st.checkbox("Flip Image Vertically", value=False)
    normalize = st.checkbox("Normalize Pixels (0-1)", value=True)
    show_histogram = st.checkbox("Show Grayscale Histogram", value=False)
    download_preprocessed = st.checkbox(
        "Allow Preprocessed Image Download", value=False
    )
    enable_batch_mode = st.checkbox("Enable Batch Mode", value=True)

    # ROBOTICS & AI FEATURES SECTION
    st.markdown("---")
    st.subheader("🤖 Robotics & AI")

    # Mobile Upload QR Code Section
    st.markdown("#### 📱 Mobile Upload")
    if st.button("Generate QR Code"):
        try:
            qr_image, url = generate_mobile_upload_qr()
            st.image(
                qr_image,
                caption=f"Scan for Mobile Upload\n{url}",
                use_container_width=True,
            )
            st.caption(
                "Point your phone camera at this QR code to upload CT/MRI images"
            )
        except Exception as e:
            st.error(f"QR generation failed: {str(e)}")

    # Arduino Connection Section
    st.markdown("#### 🔌 Arduino Hardware")
    arduino_ports = [
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "/dev/ttyUSB0",
        "/dev/ttyACM0",
    ]
    default_port_index = 3  # COM6 is default
    arduino_port = st.selectbox(
        "Arduino Port",
        arduino_ports,
        index=default_port_index,
    )

    if st.button("🔗 Test Arduino Connection"):
        try:
            arduino = get_arduino_instance(port=arduino_port)
            success, message = arduino.connect()
            if success:
                st.success(message)
                # Test signals
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Send Test Signal"):
                        success, msg = arduino.send_signal("G")
                        st.info(msg)
                with col2:
                    if st.button("Disconnect"):
                        arduino.disconnect()
                        st.info("Disconnected from Arduino")
            else:
                st.warning(message)
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

    st.markdown("---\nDeveloped by Aryan Sengar")

if "history" not in st.session_state:
    st.session_state.history = []

single_tab, batch_tab, history_tab = st.tabs(
    ["📁 Single Image", "🗂 Batch Classification", "📜 History"]
)

with single_tab:
    uploaded_file = st.file_uploader(
        "📤 Upload CT/MRI Image", type=["jpg", "jpeg", "png"]
    )
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("L")
            if enhance_contrast:
                image = ImageEnhance.Contrast(image).enhance(2.0)
            if flip_horizontal:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            if flip_vertical:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)

            st.subheader("🖼 Original vs Preprocessed")
            col1, col2 = st.columns(2)
            if show_original:
                col1.image(image, caption="Original Image", use_container_width=True)

            img_resized = image
            if auto_resize:
                img_resized = image.resize((128, 128))
            elif image.size != (128, 128):
                st.warning("⚠ Please enable auto-resize or upload a 128x128 image.")
                st.stop()

            col2.image(
                img_resized, caption="Preprocessed (128x128)", use_container_width=True
            )

            metadata_info = {
                "File Name": uploaded_file.name,
                "Image Size": image.size,
                "Mode": image.mode,
                "Format": image.format or "PNG",
                "Uploaded At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if show_dimensions:
                st.write(f"📏 Image Dimensions: {image.size}")

            if show_metadata:
                st.markdown("### 🧾 Image Metadata")
                st.json(metadata_info)

            if show_histogram:
                hist = img_resized.histogram()
                plt.figure()
                plt.plot(hist)
                plt.title("Grayscale Histogram")
                st.pyplot(plt)

            img_array = img_to_array(img_resized).reshape(1, 128, 128, 1)
            if normalize:
                img_array /= 255.0

            if show_numpy:
                st.code(str(img_array[0].flatten()[:100]) + " ...")

            with st.spinner("🔍 Predicting..."):
                time.sleep(1)
                prediction = model.predict(img_array)
                class_index = np.argmax(prediction)
                confidence = prediction[0][class_index] * 100

            st.subheader("📊 Classification Result")
            st.metric("Prediction", categories[class_index])
            st.progress(int(confidence))
            st.info(f"📈 Confidence Score: {confidence:.2f}%")

            # FEATURE: Risk Level Classification
            risk_info = calculate_risk_level(prediction, class_index, categories)

            st.markdown("### 🚨 Risk Assessment")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Risk Level", risk_info["risk_level"])
            with col2:
                st.metric("Signal Code", risk_info["signal"])
            with col3:
                st.metric("Confidence %", f"{risk_info['confidence']:.2f}")

            # Display risk description with color
            st.markdown(
                f"<div style='padding: 10px; background-color: {risk_info['color']}20; border-left: 4px solid {risk_info['color']}; border-radius: 4px;'>"
                f"<b>{risk_info['emoji']} {risk_info['description']}</b></div>",
                unsafe_allow_html=True,
            )

            st.markdown("### 🔢 Raw Prediction Probabilities")
            st.json(
                {
                    categories[0]: f"{prediction[0][0]*100:.2f}%",
                    categories[1]: f"{prediction[0][1]*100:.2f}%",
                }
            )

            st.session_state.history.append(
                {
                    "File": uploaded_file.name,
                    "Prediction": categories[class_index],
                    "Confidence": f"{confidence:.2f}%",
                    "Risk Level": risk_info["risk_level"],
                    "Time": datetime.now().strftime("%H:%M:%S"),
                }
            )

            if st.button("📄 Download PDF Report"):
                preprocessed_path = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png"
                )
                img_resized.save(preprocessed_path.name)

                fig1, ax1 = plt.subplots()
                ax1.plot(img_resized.histogram())
                ax1.set_title("Grayscale Histogram")
                grayscale_hist_path = save_plot_to_buffer(fig1)
                plt.close(fig1)

                fig2, ax2 = plt.subplots()
                df = pd.DataFrame(st.session_state.history)
                df["Prediction"].value_counts().plot(
                    kind="bar", color=["green", "red"], ax=ax2
                )
                ax2.set_ylabel("Count")
                ax2.set_title("Prediction Distribution")
                prediction_dist_path = save_plot_to_buffer(fig2)
                plt.close(fig2)

                pdf_output = generate_pdf_report(
                    filename=uploaded_file.name,
                    prediction=class_index,
                    confidence=confidence,
                    categories=categories,
                    show_metadata=show_metadata,
                    metadata=metadata_info,
                    show_numpy=show_numpy,
                    img_array=img_array,
                    prediction_probs=prediction,
                    preprocessed_img=preprocessed_path.name,
                    grayscale_hist_img=grayscale_hist_path,
                    prediction_dist_img=prediction_dist_path,
                )
                st.download_button(
                    "📄 Save PDF",
                    data=pdf_output,
                    file_name="tumor_report.pdf",
                    mime="application/pdf",
                )

            # FEATURE: Email Report System
            st.markdown("### 📧 Send Report via Email")
            email_col1, email_col2 = st.columns([2, 1])
            with email_col1:
                patient_email = st.text_input(
                    "📨 Enter email to receive report",
                    placeholder="patient@example.com",
                )
            with email_col2:
                if st.button("📤 Send Report to Email", key="email_send"):
                    if patient_email and "@" in patient_email:
                        try:
                            with st.spinner("🚀 Sending email..."):
                                # Generate PDF first
                                preprocessed_path = tempfile.NamedTemporaryFile(
                                    delete=False, suffix=".png"
                                )
                                img_resized.save(preprocessed_path.name)

                                fig1, ax1 = plt.subplots()
                                ax1.plot(img_resized.histogram())
                                ax1.set_title("Grayscale Histogram")
                                grayscale_hist_path = save_plot_to_buffer(fig1)
                                plt.close(fig1)

                                fig2, ax2 = plt.subplots()
                                df = pd.DataFrame(st.session_state.history)
                                df["Prediction"].value_counts().plot(
                                    kind="bar", color=["green", "red"], ax=ax2
                                )
                                ax2.set_ylabel("Count")
                                ax2.set_title("Prediction Distribution")
                                prediction_dist_path = save_plot_to_buffer(fig2)
                                plt.close(fig2)

                                pdf_output = generate_pdf_report(
                                    filename=uploaded_file.name,
                                    prediction=class_index,
                                    confidence=confidence,
                                    categories=categories,
                                    show_metadata=show_metadata,
                                    metadata=metadata_info,
                                    show_numpy=show_numpy,
                                    img_array=img_array,
                                    prediction_probs=prediction,
                                    preprocessed_img=preprocessed_path.name,
                                    grayscale_hist_img=grayscale_hist_path,
                                    prediction_dist_img=prediction_dist_path,
                                )

                                success, message = send_email_report(
                                    recipient_email=patient_email,
                                    pdf_bytes=pdf_output,
                                    patient_name=uploaded_file.name.split(".")[0],
                                )
                                if success:
                                    st.success(f"✅ {message}")
                                else:
                                    st.error(f"❌ {message}")
                        except Exception as e:
                            st.error(
                                f"Email error: {str(e)}\nMake sure EMAIL_ADDRESS and EMAIL_PASSWORD environment variables are set."
                            )
                    else:
                        st.warning("⚠️ Please enter a valid email address")

            # FEATURE: Arduino Hardware Integration
            st.markdown("### 🤖 Send Result to Hardware")
            arduino_col1, arduino_col2 = st.columns([2, 1])
            with arduino_col1:
                arduino_ports = [
                    "COM3",
                    "COM4",
                    "COM5",
                    "COM6",
                    "COM7",
                    "/dev/ttyUSB0",
                    "/dev/ttyACM0",
                ]
                default_port_index = 3  # COM6 is default
                arduino_port_select = st.selectbox(
                    "Select Arduino Port",
                    arduino_ports,
                    index=default_port_index,
                    key="arduino_port_select",
                )
            with arduino_col2:
                if st.button("🚀 Send to Arduino", key="arduino_send"):
                    try:
                        with st.spinner("📡 Connecting to Arduino..."):
                            success, message = safe_send_to_arduino(
                                signal=risk_info["signal"], port=arduino_port_select
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.info(
                                    f"Signal Sent: {get_signal_description(risk_info['signal'])}"
                                )
                            else:
                                st.warning(f"⚠️ {message}")
                    except Exception as e:
                        st.error(f"Hardware error: {str(e)}")

            if download_preprocessed:
                buf = io.BytesIO()
                img_resized.save(buf, format="PNG")
                st.download_button(
                    "⬇ Download Preprocessed Image",
                    buf.getvalue(),
                    file_name="preprocessed_image.png",
                )

            if st.session_state.history:
                with st.expander("📊 Show Prediction Distribution"):
                    df = pd.DataFrame(st.session_state.history)
                    fig, ax = plt.subplots()
                    df["Prediction"].value_counts().plot(
                        kind="bar", color=["green", "red"], ax=ax
                    )
                    ax.set_ylabel("Count")
                    ax.set_title("Prediction Distribution")
                    st.pyplot(fig)

            with st.expander("📐 View Model Summary"):
                summary_lines = []
                model.summary(print_fn=lambda x: summary_lines.append(x))
                st.code("\n".join(summary_lines))

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with batch_tab:
    if enable_batch_mode:
        st.subheader("🗂 Upload ZIP for Batch Prediction")
        zip_file = st.file_uploader("Upload ZIP of Images", type="zip", key="zip")
        if zip_file is not None:
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = os.path.join(tmp_dir, "batch.zip")
                with open(zip_path, "wb") as f:
                    f.write(zip_file.read())
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmp_dir)
                    results = []
                    for file_name in zip_ref.namelist():
                        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                            try:
                                img = Image.open(
                                    os.path.join(tmp_dir, file_name)
                                ).convert("L")
                                img = img.resize((128, 128))
                                arr = img_to_array(img).reshape(1, 128, 128, 1) / 255.0
                                pred = model.predict(arr)
                                idx = np.argmax(pred)
                                conf = pred[0][idx] * 100
                                results.append(
                                    {
                                        "File": file_name,
                                        "Prediction": categories[idx],
                                        "Confidence": f"{conf:.2f}%",
                                    }
                                )
                            except Exception as e:
                                results.append({"File": file_name, "Error": str(e)})
                    df = pd.DataFrame(results)
                    st.success("Batch classification complete!")
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download Results CSV",
                        csv,
                        file_name="batch_results.csv",
                        mime="text/csv",
                    )
    else:
        st.info(
            "Batch Mode is disabled. Enable it from the Settings to use this feature."
        )

with history_tab:
    st.subheader("📜 Prediction History")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history[::-1])
        st.table(df)
    else:
        st.info("No history yet. Upload an image to begin.")
