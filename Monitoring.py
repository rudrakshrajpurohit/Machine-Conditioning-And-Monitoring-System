import serial
import pandas as pd
import time
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report

# Suppress specific sklearn warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

def collect_training_data(serial_port, num_samples=1000, timeout=60):
    """
    Collect training data from Arduino.
    
    Returns: DataFrame with vibration data and labels.
    """
    ser = serial.Serial(serial_port, 9600, timeout=2)
    time.sleep(2)  # Allow Arduino to reset
    
    print("Preparing to collect training data...")

    def read_valid_samples(ser, target_samples, condition_label):
        samples = []
        start_time = time.time()

        while len(samples) < target_samples:
            if time.time() - start_time > timeout:
                print(f"Timeout for {condition_label} condition. Collected {len(samples)} samples.")
                break
            
            try:
                # Read line and strip whitespace
                line = ser.readline().decode().strip()
                if ',' not in line:
                    continue
                
                # Parse the line into two floats
                vib1, vib2 = map(float, line.split(','))

                # Depending on the condition, append only the relevant vibration
                if condition_label == "Good":
                    samples.append([vib1])
                    print(f"Good sample {len(samples)}: Vibration1 = {vib1}")
                elif condition_label == "Faulty":
                    samples.append([vib2])
                    print(f"Faulty sample {len(samples)}: Vibration2 = {vib2}")
                
            except Exception as e:
                print(f"Error collecting {condition_label} sample: {e}")
                continue
        
        return samples

    # Collect good condition data
    input("Ensure one fan is in good condition. Press Enter to start collecting good condition data...")
    good_samples = read_valid_samples(ser, num_samples // 2, "Good")

    # Collect faulty condition data
    input("\nEnsure one fan has a damaged blade. Press Enter to start collecting faulty condition data...")
    faulty_samples = read_valid_samples(ser, num_samples // 2, "Faulty")

    ser.close()

    # Create DataFrame with labels
    data = good_samples + faulty_samples

    if not data:
        raise ValueError("No samples collected. Check Arduino connection and sensor setup.")

    labels = [0] * len(good_samples) + [1] * len(faulty_samples)
    
    df = pd.DataFrame(data, columns=['vibration'])
    df['condition'] = labels

    return df

def train_model(data):
    """
    Train SVM model on the collected data.
    
    Returns: trained model and scaler.
    """
    if len(data) < 2 or len(data['condition'].unique()) < 2:
        raise ValueError("Insufficient data for training. Ensure you've collected samples for both good and faulty conditions.")

    X = data[['vibration']]
    y = data['condition']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = SVC(kernel='rbf', probability=True, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    print("\nModel Evaluation:")
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return model, scaler

def real_time_monitoring(model, scaler, serial_port):
    """
    Real-time monitoring and classification of fan condition sequentially for multiple fans.
    """
    ser = serial.Serial(serial_port, 9600, timeout=1)
    time.sleep(2)

    num_fans = int(input("Enter the number of fans to monitor: "))
    monitoring_time = int(input("Enter the monitoring time for each fan (in seconds): "))

    for fan_number in range(1, num_fans + 1):
        print(f"\nStarting real-time monitoring for Fan {fan_number}...")
        start_time = time.time()

        while time.time() - start_time < monitoring_time:
            try:
                # Read and process vibration data
                line = ser.readline().decode().strip()
                if ',' not in line:
                    continue

                vib1, vib2 = map(float, line.split(','))

                # Use only the vibration data relevant to the fan
                if fan_number % 2 == 1:  # Good fan
                    print(f"Fan {fan_number} Vibration: Vibration1 = {vib1}")
                    input_data = scaler.transform([[vib1]])
                else:  # Faulty fan
                    print(f"Fan {fan_number} Vibration: Vibration2 = {vib2}")
                    input_data = scaler.transform([[vib2]])

                prediction_probabilities = model.predict_proba(input_data)[0]
                prediction_classification = model.predict(input_data)[0]

                condition_label = "Good" if prediction_classification == 0 else "Faulty"
                confidence_score = prediction_probabilities[prediction_classification]

                print(f"Fan {fan_number} condition: {condition_label} (Confidence: {confidence_score:.2f})")

            except Exception as e:
                print(f"Error in monitoring Fan {fan_number}: {e}")
                continue

        print(f"Completed monitoring for Fan {fan_number}.")

    print("\nFinished monitoring all fans.")
    ser.close()

if __name__ == "__main__":
    SERIAL_PORT = 'COM9'  # Replace with your Arduino's serial port

    try:
        print("Collecting training data...")
        training_data = collect_training_data(SERIAL_PORT)

        training_data.to_csv('vibration_training_data.csv', index=False)

        print("\nTraining model...")
        model, scaler = train_model(training_data)

        real_time_monitoring(model, scaler, SERIAL_PORT)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
