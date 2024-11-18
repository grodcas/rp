from flask import Flask, render_template, Response
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import smbus
import time

# Create Flask app
app = Flask(__name__)

# Set up I2C communication
bus = smbus.SMBus(1)  # I2C bus 1 (default for most Raspberry Pi models)
MPU6050_ADDR = 0x68  # MPU-6050 I2C address
MPU_ADDR = 0x68
GYRO_SCALE_MODIFIER = 131.0 
GYRO_XOUT_H = 0x43
GYRO_CONFIG = 0x1B
PWR_MGMT_1 = 0x6B

def read_word_2c(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)
    val = (high << 8) + low
    return val - 65536 if val >= 0x8000 else val

def write_register(reg, value):
    bus.write_byte_data(MPU_ADDR, reg, value)



# Calibration
def calibrate_gyroscope(samples=100):
    offsets = [0, 0, 0]
    for i in range(samples):
        offsets[0] += read_word_2c(GYRO_XOUT_H)
        offsets[1] += read_word_2c(GYRO_XOUT_H + 2)
        offsets[2] += read_word_2c(GYRO_XOUT_H + 4)
        time.sleep(0.01)
    return [offset / samples for offset in offsets]

gyro_offsets = calibrate_gyroscope()


# Initialize the MPU-6050
def init_mpu():
    # Wake up the MPU-6050 (it is in sleep mode when powered on)
    # Initialize MPU6000
    write_register(PWR_MGMT_1, 0)  # Wake up sensor
    write_register(GYRO_CONFIG, 0x18)  # Set full scale ±2000 °/s
    time.sleep(0.1)

# Function to read MPU-6050 data
def read_mpu():
    # Read Accelerometer data (6 bytes)
    accel_data = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)
    ax = (accel_data[0] << 8) + accel_data[1]
    ay = (accel_data[2] << 8) + accel_data[3]
    az = (accel_data[4] << 8) + accel_data[5]

    # Read Gyroscope data (6 bytes)
    # gyro_data = bus.read_i2c_block_data(MPU6050_ADDR, 0x43, 6)
    # gx = (gyro_data[0] << 8) + gyro_data[1]
    # gy = (gyro_data[2] << 8) + gyro_data[3]
    # gz = (gyro_data[4] << 8) + gyro_data[5]
    
    gx = read_word_2c(GYRO_XOUT_H) - gyro_offsets[0]
    gy = read_word_2c(GYRO_XOUT_H + 2) - gyro_offsets[1]
    gz = read_word_2c(GYRO_XOUT_H + 4) - gyro_offsets[2]
    return ax, ay, az, gx, gy, gz

# Initialize MPU
init_mpu()

# Data storage for plots (storing 100 data points per axis)
data_len = 100
accel_data_x = np.zeros(data_len)
accel_data_y = np.zeros(data_len)
accel_data_z = np.zeros(data_len)
gyro_data_x = np.zeros(data_len)
gyro_data_y = np.zeros(data_len)
gyro_data_z = np.zeros(data_len)

# Function to update the data
def update_data():
    ax, ay, az, gx, gy, gz = read_mpu()

    # Update the data buffers
    accel_data_x[:-1] = accel_data_x[1:]
    accel_data_y[:-1] = accel_data_y[1:]
    accel_data_z[:-1] = accel_data_z[1:]
    gyro_data_x[:-1] = gyro_data_x[1:]
    gyro_data_y[:-1] = gyro_data_y[1:]
    gyro_data_z[:-1] = gyro_data_z[1:]

    accel_data_x[-1] = ax
    accel_data_y[-1] = ay
    accel_data_z[-1] = az
    gyro_data_x[-1] = gx
    gyro_data_y[-1] = gy
    gyro_data_z[-1] = gz

# Set up Flask route
@app.route('/')
def index():
    return render_template('index.html')

# Function to generate the plots
def generate_plots():
    while True:
        update_data()

        # Create a figure for the plots
        fig, axs = plt.subplots(2, 3, figsize=(15, 10))

        # Plot accelerometer data
        axs[0, 0].plot(accel_data_x, label="Ax", color='r')
        axs[0, 0].set_title('Accelerometer X')
        axs[0, 1].plot(accel_data_y, label="Ay", color='g')
        axs[0, 1].set_title('Accelerometer Y')
        axs[0, 2].plot(accel_data_z, label="Az", color='b')
        axs[0, 2].set_title('Accelerometer Z')

        # Plot gyroscope data
        axs[1, 0].plot(gyro_data_x, label="Gx", color='r')
        axs[1, 0].set_title('Gyroscope X')
        axs[1, 1].plot(gyro_data_y, label="Gy", color='g')
        axs[1, 1].set_title('Gyroscope Y')
        axs[1, 2].plot(gyro_data_z, label="Gz", color='b')
        axs[1, 2].set_title('Gyroscope Z')

        # Adjust layout
        for ax in axs.flat:
            ax.set(xlabel='Time', ylabel='Value')
            ax.grid()

        # Save the plot to a file
        plt.tight_layout()
        plt.savefig('/tmp/plot.png')
        plt.close(fig)

        # Serve the image via Flask
        with open('/tmp/plot.png', 'rb') as f:
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + f.read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_plots(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
