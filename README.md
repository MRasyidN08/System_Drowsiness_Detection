System Drowsiness Detection — Raspberry Pi + YOLOv8 + Cloud

**A Real-Time Driver Drowsiness Detection System**
Powered by **Raspberry Pi 4**, **YOLOv8**, **Fault Tolerant**, and **Cloud Monitoring**

---

## 📌 Overview

Fatigue while driving is one of the leading causes of traffic accidents. **System Drowsiness Detection** is a smart embedded solution designed to detect signs of driver drowsiness in real-time using computer vision and cloud computing technologies. The system utilizes **YOLOv8 for classification**, runs locally on a **Raspberry Pi 4**, and features automatic **alert triggering**, **redundant safety mechanisms**, and **remote monitoring** via the cloud.

---

## Dataset

https://drive.google.com/file/d/1rQG-SR9zjZiq6uxMC7o5kDFpCLjjnoKP/view?usp=drive_link

## 🧠 Key Features

* 🎯 **YOLOv8-Based Drowsiness Classification**
  Accurate and efficient deep learning model for detecting eye closure and drowsy behavior.

* 🧩 **Runs Fully on Raspberry Pi 4**
  No external GPU required — compact, low-power, and portable setup.

* 🔔 **Real-Time Alerts**
  * Buzzer sounds when drowsiness is detected
  * Red LED lights up as a visual alert

* ☁️ **Cloud Integration**
  Live detection logs and monitoring through cloud platforms for tracking and analytics.

* 🔁 **Redundancy & Fault Tolerance**

  * Dual camera setup for higher reliability
  * Retry mechanisms for model inference
  * Graceful degradation if model fails or hardware glitches occur

---

## 🧰 Tech Stack

| Component       | Description                                      |
| --------------- | ------------------------------------------------ |
| 🔌 Hardware     | Raspberry Pi 4, IR/USB Camera, Buzzer, LED       |
| 🧠 AI Model     | YOLOv8 for facial landmark & eye state detection |
| 🌐 Cloud        | Remote dashboard / log storage                   |
| 🧪 Safety Logic | Retry system, backup camera, failover mechanisms |
| 💻 Backend      | Python (OpenCV, Flask, GPIO, Ultralytics)        |

---

## 📷 System Architecture

```text
Camera --> YOLOv8 --> Classification
                         ↓
                 [Drowsy Detected?]
                         ↓ Yes
               --> Trigger Buzzer & LED  
                         ↓
              Log to Cloud Monitoring System
```

---

## 🚀 How It Works

1. **Camera Feed**: Captures the driver's face in real-time.
2. **YOLOv8 Inference**: Runs locally on the Raspberry Pi to classify drowsy states.
3. **Alert System**: If drowsiness is detected:
   * A buzzer is triggered
   * A red LED flashes
   * Detection log is sent to the cloud
4. **Failover & Retry**: If the primary model or camera fails, the system automatically switches to backup logic or alerts the cloud.

---

## 🛡️ Reliability First

To ensure consistent performance, the system includes:

* Dual camera support for redundancy
* Retry logic for failed detections
* Graceful degradation mode to maintain minimal functionality even under failure

---

## 📊 Future Enhancements

* Mobile notification integration
* Sleep pattern analysis
* Night vision optimization
* Integration with vehicle telematics

---
## 💡 Use Case

This system is ideal for:

* 🚚 Truck drivers and fleet vehicles
* 🚌 Long-distance transportation
* 🚗 Personal vehicles with safety add-ons
* 🧪 Research on driver behavior and fatigue

---
