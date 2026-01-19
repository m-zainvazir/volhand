# 🖐️ Aura Control

Hand Gesture Volume Control
A real-time computer vision application that allows you to control your system volume using hand gestures.

[Click here to watch the video (1)](https://drive.google.com/file/d/1wgoZ3YghRwfZPgYzKI-PqDOGqrdM-fm3/view?usp=sharing)

[Click here to watch the video (2)](media/VolHand_Control_Final_HD.mp4)

---

## ✨ Features

- **Intuitive Volume Control** – Adjust system volume by changing the distance between thumb and index finger  
- **Smart Lock Feature** – Toggle volume lock by lifting your pinky finger  
- **Real-time Feedback** – Visual indicators for volume level and lock status  
- **Cross-Platform Ready** – Works on Windows (via `pycaw`), adaptable for other OS  
- **Customizable** – Adjust sensitivity, thresholds, and visual settings  

---

## 🚀 Usage

Run the application:
```bash
python 10_VolumeHandControl.py
```

---

## ✋ Gesture Controls

| Gesture | Action | Visual Indicator |
|-------|-------|-----------------|
| ✌️ Thumb–Index Distance | Adjust volume | Purple line |
| ☝️ Pinky up | Toggle lock | Red status box |
| ✊ Pinky down | Volume adjustable | Green status box |

### Volume Range
- **Min:** Fingers close → 0% volume  
- **Max:** Fingers apart → 100% volume  
- **Lock:** Lift pinky to toggle  

---

## 📊 How It Works

### Hand Tracking
- Uses **MediaPipe Hands**
- Tracks:
  - Thumb tip → Landmark **4**
  - Index tip → Landmark **8**
  - Pinky tip → Landmark **20**

### Volume Logic
- **Distance Calculation:** Euclidean distance between fingertips  
- **Mapping:** 50–200 px → 0–100% volume  
- **System Control:** Windows audio via `pycaw`

### Lock Mechanism
```python
if prev_pinky_state == "down" and current_pinky_state == "up":
    volume_locked = not volume_locked

if not volume_locked:
    # Adjust volume
```

---
## 🛠️ Installation

### Prerequisites
- Python **3.8+** (Recommended: **Python 3.11**)
- Webcam
- Windows OS (for system volume control)

---

### Step-by-Step Setup

#### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/hand-volume-control.git
cd hand-volume-control
```

#### 2️⃣ Create and activate a virtual environment

**Using Conda (recommended):**
```bash
conda create -n hand-volume python=3.11
conda activate hand-volume
```

**Using venv:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

#### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📦 Requirements

`requirements.txt`
```txt
mediapipe==0.10.31
opencv-python==4.11.0.86
opencv-contrib-python==4.11.0.86
numpy==1.26.4
comtypes==1.4.13
pycaw==20230322
```

---

## 🤝 Contributing

1. Fork the repo  
2. Create branch (`git checkout -b feature/NewFeature`)  
3. Commit (`git commit -m "Add feature"`)  
4. Push (`git push origin feature/NewFeature`)  
5. Open Pull Request  

---

## 📝 License
MIT License

---

## 🙏 Acknowledgments
- MediaPipe
- OpenCV
- pycaw

---

⭐ If you found this project useful, please give it a star!
