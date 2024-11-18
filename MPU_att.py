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

P, X, Q, R, av = None, None, None, None, None


start_time =time.time()

def read_word_2c(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)
    val = (high << 8) + low
    return val - 65536 if val >= 0x8000 else val

def write_register(reg, value):
    bus.write_byte_data(MPU_ADDR, reg, value)



def estimator_init():
    qa = 0.0001  # Bruit d'état orientation
    ra = 1  # Bruit de mesure accéléro
    rg = 100  # Bruit de mesure gyro
    Q = np.diag(np.array([qa, qa]))
    R = np.diag(np.array([ra, ra, rg]))
    X = np.array([0, 0]).T  # État : rotation selon x (rad)
    P = (10 * np.pi / 180) ** 2  # Variance initiale
    values = []

    # For loop to append values
    for i in range(100):
        ax, ay, az, gx, gy, gz = read_mpu()
        values.append(np.sqrt(ax**2 + az**2))  # Append the square of each number
    
    av = np.mean(np.array(values))

    return Q, R, X, P, av


def estimator(Y, P, X, Q, R, av, start_time):
    end_time = time.time()
    dt = end_time - start_time
    if dt < 0:
        dt = 1
    start_time = time.time()

    # Predict
    F = np.array([[1, dt], [0, 1]])
    X = np.dot(F, X)
    P = np.dot(np.dot(F, P), F.T) + Q

    # Update
    if not np.isnan(Y).any():  # Ensure Y doesn't contain NaN values
        Y = Y.T
        H = [[-np.sin(X[1]) * av, 0], [np.cos(X[1]) * av, 0], [0, 1]]
        C = [[np.cos(X[1]) * av, 0], [np.sin(X[1]) * av, 0], [0, 1]]
        Yhat = C
        S = np.dot(np.dot(H, P), H.T) + R
        K = np.dot(np.dot(P, H.T), np.linalg.inv(S))
        X = X + np.dot(K, (Y - Yhat))
        P = np.dot(np.dot(F, P), F.T) + Q

    # Update Visualisation:
    theta = X[1]
    thetap = X[2]
    return theta, thetap, P, X, Q, av, start_time


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
    write_register(PWR_MGMT_1, 0)  # Wake up sensor
    write_register(GYRO_CONFIG, 0x18)  # Set full scale ±2000 °/s
    time.sleep(0.1)


# Function to read MPU-6050 data
def read_mpu():
    accel_data = bus.read_i2c_block_data(MPU6050_ADDR, 0x3B, 6)
    ax = (accel_data[0] << 8) + accel_data[1]
    ay = (accel_data[2] << 8) + accel_data[3]
    az = (accel_data[4] << 8) + accel_data[5]

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

Q, R, X, P, av = estimator_init()

# Function to update the data
def update_data(start_time, P, X, Q, R, av):
    ax, ay, az, gx, gy, gz = read_mpu()
    Y = np.array([ax, az, gy])
    theta, thetap, P, X, Q, av, start_time = estimator(Y, P, X, Q, R, av, start_time)

    # Update the data buffers
    accel_data_x[:-1] = accel_data_x[1:]
    accel_data_y[:-1] = accel_data_y[1:]
    accel_data_z[:-1] = accel_data_z[1:]
    gyro_data_x[:-1] = gyro_data_x[1:]
    gyro_data_y[:-1] = gyro_data_y[1:]
    gyro_data_z[:-1] = gyro_data_z[1:]

    accel_data_x[-1] = ax
    accel_data_y[-1] = az
    accel_data_z[-1] = theta
    gyro_data_x[-1] = gy
    gyro_data_y[-1] = gz
    gyro_data_z[-1] = gz

    return start_time


# Set up Flask route
@app.route('/')
def index():
    return render_template('index.html')


# Function to generate the plots
def generate_plots():
    start_time = time.time()
    while True:
        start_time = update_data(start_time, P, X, Q, R, av)

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
