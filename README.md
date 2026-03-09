# AI Powered Brain Tumor Detection System

An AI-based medical image analysis system that detects brain tumors from MRI and CT scan images using a Convolutional Neural Network (CNN).  
The system integrates machine learning with Arduino hardware to provide real-time visual diagnosis indicators.

---

## Project Overview

Brain tumor diagnosis normally requires expert analysis of MRI or CT scans. This project aims to assist medical diagnostics by automating the detection process using artificial intelligence.

The system uses a trained CNN model to classify brain scans as:

- Healthy Brain
- Tumor Detected

The prediction results are displayed through a Streamlit web interface and hardware indicators connected to an Arduino.

---

## Key Features

- CNN based brain tumor detection model
- Supports MRI and CT scan image classification
- Streamlit web interface for easy image upload
- Real-time prediction results
- Arduino hardware integration
- LED indicators for risk level
- LCD display for diagnosis output
- Servo motor for severity indication
- Automated diagnostic report generation

---

## System Architecture

The system is divided into three layers:

1. User Interface Layer  
   - Streamlit web application for uploading images.

2. Machine Learning Layer  
   - CNN model processes MRI/CT scan images and predicts tumor presence.

3. Hardware Control Layer  
   - Arduino receives signals and activates LEDs, LCD, and servo motor.

---

## Machine Learning Model

The model is a Convolutional Neural Network (CNN) trained on brain scan images.

Model Architecture:

- Convolution Layer (32 filters)
- Max Pooling Layer
- Convolution Layer (64 filters)
- Max Pooling Layer
- Flatten Layer
- Dense Layer (128 neurons)
- Dropout Layer
- Output Layer (Softmax)

Image preprocessing includes:

- Grayscale conversion
- Image resizing (128 × 128)
- Normalization

Model Accuracy: **~96%**

---

## Hardware Components

- Arduino UNO
- Ultrasonic Sensor (HC-SR04)
- Servo Motor (SG90)
- LCD Display (16x2)
- LED Indicators (Red, Yellow, Green)
- Jumper Wires
- Potentiometer

---

## Software & Tools

- Python
- TensorFlow / Keras
- OpenCV
- Streamlit
- Arduino IDE
- Tinkercad

---

## Project Workflow

1. User uploads MRI/CT image via Streamlit interface
2. Image is preprocessed and sent to CNN model
3. Model predicts tumor presence
4. Prediction is displayed on web interface
5. Arduino receives signal via serial communication
6. Hardware indicators display diagnosis results

---

## Example Output

Healthy Brain  
LED: Green  
Servo Angle: 0°

Possible Tumor  
LED: Yellow  
Servo Angle: 90°

High Risk Tumor  
LED: Red  
Servo Angle: 180°

---

## Future Improvements

- Multi-class tumor classification
- Integration with hospital databases
- Deployment on edge AI hardware
- Larger medical dataset training
- Real-time hospital monitoring system

---

## 📦 Model Not Included 
To run the app, download the trained model file from:  
[Google Drive Link](https://drive.google.com/file/d/1yshagIhfq15iDHo_0-3SRw33lavghMiT/view?usp=sharing)

Then place it in the project directory as `brain_tumor_model.h5`.

---
© 2025 Aryan Sengar – All Rights Reserved  
Unauthorized copying is strictly prohibited.
---

> 💬 *Feel free to drop a ⭐ if you find this helpful!*

## License

This project is for educational and research purposes.
