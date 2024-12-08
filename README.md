# Machine-Conditioning-And-Monitoring-System

This project provides a predictive maintenance solution for machines using vibration analysis and machine learning. The system monitors fan conditions, identifies potential faults, and ensures timely intervention to prevent major failures.

## Features

- **Data Collection**: Real-time vibration data acquisition from ADXL335 accelerometers connected to an Arduino Mega.
- **Machine Learning**: Uses Support Vector Machine (SVM) for classifying machine conditions (Good or Faulty).
- **Real-Time Monitoring**: Continuous condition monitoring of multiple fans with fault detection and confidence scores.
- **Predictive Maintenance**: Provides insights for early fault detection and preventive maintenance.

---

## Hardware Requirements

- **Microcontroller**: Arduino Mega
- **Sensors**: Two ADXL335 accelerometers
- **Relays**: 4-channel relay module
- **Other Components**: Breadboard, jumper wires, power supply
- **System**: A computer with Python installed for data analysis


## Software Requirements

- **Arduino IDE** (for programming the Arduino)
- **Python** (tested with version 3.8+)
- Required Python libraries:
  - `serial`
  - `pandas`
  - `scikit-learn`

Install dependencies using:

```bash
pip install -r requirements.txt
