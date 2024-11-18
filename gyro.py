import smbus
import time

# MPU6000 I2C address and registers
MPU_ADDR = 0x68
GYRO_XOUT_H = 0x43
GYRO_CONFIG = 0x1B
PWR_MGMT_1 = 0x6B

# Initialize I2C
bus = smbus.SMBus(1)

def read_word_2c(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)
    val = (high << 8) + low
    return val - 65536 if val >= 0x8000 else val

def write_register(reg, value):
    bus.write_byte_data(MPU_ADDR, reg, value)

# Initialize MPU6000
write_register(PWR_MGMT_1, 0)  # Wake up sensor
write_register(GYRO_CONFIG, 0x18)  # Set full scale ±2000 °/s

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
print("Gyroscope offsets:", gyro_offsets)

# Apply offsets to gyroscope readings
while True:
    gyro_x = read_word_2c(GYRO_XOUT_H) - gyro_offsets[0]
    gyro_y = read_word_2c(GYRO_XOUT_H + 2) - gyro_offsets[1]
    gyro_z = read_word_2c(GYRO_XOUT_H + 4) - gyro_offsets[2]
    print(f"Gyroscope: X={gyro_x}, Y={gyro_y}, Z={gyro_z}")
    time.sleep(0.1)
