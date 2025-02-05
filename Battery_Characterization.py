import os
import asyncio
from bleak import BleakClient
import csv
import time
import numpy as np

def constants(index): 
    BLUETOOTH_ADDRESS = 'FC:58:FA:CF:64:4D'
    TX_CHAR = '6e400002-b5a3-f393-e0a9-e50e24dcca9e' 
    RX_CHAR = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
    constants_list = [BLUETOOTH_ADDRESS, TX_CHAR, RX_CHAR]
    return constants_list[index]

async def connect_cube(address): 
    client = BleakClient(address)
    try:
        await client.connect()
        if client.is_connected:
            print("Circuit Cube connected. ")
            return client
    except Exception as e:
        print(f"Failed to connect: {e}")
        quit()

async def motor_command(client, speed): 
    try: 
        A_command_string = f'{'+'}{speed:03}{chr(ord('a') + 0)}'
        B_command_string = f'{'+'}{speed:03}{chr(ord('a') + 1)}'
        await client.write_gatt_char(constants(1), A_command_string.encode())
        await client.write_gatt_char(constants(1), B_command_string.encode())
    except Exception as e: 
        print(f'Motor command failed: {e}')
        quit()

async def read_voltage(client): 
    try:
        await client.write_gatt_char(constants(1), bytes('b', 'utf-8'))
        voltage = await client.read_gatt_char(constants(2))
        return voltage.decode('utf-8')
    except Exception as e:
        print(f"Failed to read voltage: {e}")
        quit()

async def main():
    try: 
        interval = 5 
        cwd = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(cwd, 'Voltage_Data.csv')
        with open(file_path, mode='w', newline='') as file: 
            writer = csv.writer(file)
            writer.writerow(['Seconds', 'Voltage (Motors Off)', 'Voltage (Motors On)'])
        client = await connect_cube(constants(0))
        seconds = 0
        print("'Seconds'  'Voltage (Motors Off)'  'Voltage (Motors On)' ")
        while True: 
            await motor_command(client, 0)
            await asyncio.sleep(interval*0.2)
            off_voltage = await read_voltage(client)

            await motor_command(client, 255)
            await asyncio.sleep(interval*0.8)
            on_voltage = await read_voltage(client)

            with open(file_path, mode='a', newline='') as file: 
                writer = csv.writer(file)
                writer.writerow([seconds, off_voltage, on_voltage])
                file.flush()
            print(f'{seconds:04d}s  {off_voltage}V  {on_voltage}V')
            seconds += interval
    except Exception as e: 
        print(e)
        await motor_command(client, 0)
        quit()

asyncio.run(main())