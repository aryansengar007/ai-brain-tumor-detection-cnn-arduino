# 🧠 AI Powered Brain Tumor Detection System
### Deep Learning + Medical Image Analysis + Embedded Hardware

![Python](https://img.shields.io/badge/Python-3.10-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Deep%20Learning-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)
![Arduino](https://img.shields.io/badge/Arduino-Hardware-green)
![CNN](https://img.shields.io/badge/Model-CNN-purple)

An **AI-driven medical imaging system** designed to detect brain tumors from **MRI and CT scan images** using a **Convolutional Neural Network (CNN)**.  
The system integrates **machine learning, computer vision, and embedded hardware** to provide **real-time diagnostic indicators using Arduino-controlled components**.

This project demonstrates how **Artificial Intelligence and IoT-based hardware systems** can be combined to build intelligent healthcare assistance tools.

---

# 🚀 Project Overview

Brain tumor diagnosis typically requires expert radiologists to analyze MRI or CT scans. This process can be **time-consuming, expensive, and dependent on specialist availability**.

This project proposes an **AI-assisted diagnostic system** that:

✔ Automatically analyzes brain scans  
✔ Detects tumor presence using deep learning  
✔ Displays results via **web interface and hardware indicators**

The system uses a trained **CNN model** to classify images into:

- 🟢 **Healthy Brain**
- 🔴 **Tumor Detected**

Prediction results are delivered through:

- **Streamlit Web Interface**
- **Arduino Hardware Indicators**
- **Automated diagnostic outputs**

---

# ⭐ Key Features

- 🧠 **Deep Learning Based Tumor Detection**
- 🖼 **MRI & CT Image Classification**
- 🌐 **Interactive Streamlit Web Interface**
- ⚡ **Real-time prediction results**
- 🤖 **Arduino Hardware Integration**
- 💡 **LED risk-level indicators**
- 📟 **LCD display for diagnosis output**
- ⚙ **Servo motor for severity indication**
- 📊 **Automated diagnostic reporting**
- 🔗 **Serial communication between Python and Arduino**

---

# 🏗 System Architecture

    ┌───────────────────────────┐
    │   User Interface Layer    │
    │   Streamlit Web App       │
    │   Image Upload            │
    └──────────────┬────────────┘
                   │
                   ▼
    ┌───────────────────────────┐
    │ Machine Learning Layer    │
    │ CNN Model (TensorFlow)    │
    │ Image Processing (OpenCV) │
    └──────────────┬────────────┘
                   │
                   ▼
    ┌───────────────────────────┐
    │ Hardware Control Layer    │
    │ Arduino + Sensors         │
    │ LEDs | LCD | Servo Motor  │
    └───────────────────────────┘
    
---

# 🧠 Machine Learning Model

The system uses a **Convolutional Neural Network (CNN)** trained on brain scan datasets.

### Model Architecture

Input Image (128x128 Grayscale)
│
Convolution Layer (32 Filters)
│
Max Pooling Layer
│
Convolution Layer (64 Filters)
│
Max Pooling Layer
│
Flatten Layer
│
Dense Layer (128 Neurons)
│
Dropout Layer
│
Softmax Output Layer


### Image Preprocessing

- Grayscale Conversion
- Image Resizing (128 × 128)
- Pixel Normalization

📊 **Model Accuracy:** ~96%

---

# 🔌 Hardware Components

| Component | Purpose |
|--------|--------|
| Arduino UNO | Main hardware controller |
| Ultrasonic Sensor | Detects user presence |
| LCD Display (16x2) | Displays diagnosis results |
| LEDs (Red, Yellow, Green) | Indicates risk level |
| Servo Motor (SG90) | Shows severity level |
| Potentiometer | LCD contrast control |
| Jumper Wires | Circuit connections |

---

# 🛠 Tech Stack

| Category | Technology |
|--------|--------|
| Programming | Python |
| Deep Learning | TensorFlow / Keras |
| Image Processing | OpenCV |
| Web Interface | Streamlit |
| Hardware Programming | Arduino IDE |
| Simulation | Tinkercad |

---

# ⚙ Project Workflow

User Uploads MRI/CT Image
│
▼
Image Preprocessing
(Grayscale + Resize)
│
▼
CNN Model Prediction
│
▼
Result Displayed on Web Interface
│
▼
Serial Communication with Arduino
│
▼
Hardware Indicators Activated
(LED + LCD + Servo)


---

# 📊 Example Output

| Condition | LED Indicator | Servo Angle |
|--------|--------|--------|
| Healthy Brain | 🟢 Green | 0° |
| Possible Tumor | 🟡 Yellow | 90° |
| High Risk Tumor | 🔴 Red | 180° |


---

# 🔮 Future Improvements

- Multi-class tumor classification
- Integration with hospital medical databases
- Edge AI deployment
- Mobile healthcare diagnostic system
- Real-time patient monitoring

---

# 📦 Model Not Included 
To run the app, download the trained model file from:  
[Google Drive Link](https://drive.google.com/file/d/1yshagIhfq15iDHo_0-3SRw33lavghMiT/view?usp=sharing)

Then place it in the project directory as `brain_tumor_model.h5`.

---
© 2025 Aryan Sengar – All Rights Reserved  
Unauthorized copying is strictly prohibited.
---
