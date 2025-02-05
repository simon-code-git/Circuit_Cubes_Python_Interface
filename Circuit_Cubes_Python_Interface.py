import os
import asyncio
from bleak import BleakClient, BleakScanner
import rich; from rich.panel import Panel; from rich.console import Console; from rich.live import Live
import keyboard

def constants(index): #Index ranges from 0 to 28 since there are 29 items. 
    BLUETOOTH_ADDRESS = 'FC:58:FA:CF:64:4D' #Address is unique to each Cube. All other values are the same for all Cubes. 

    CIRCUITCUBE_SERV = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
    TX_CHAR = '6e400002-b5a3-f393-e0a9-e50e24dcca9e' #Write-without-response. 
    RX_CHAR = '6e400003-b5a3-f393-e0a9-e50e24dcca9e' #Notify. 
    RX_CLIENT_CHAR_CONFIG_DESC = '00002902-0000-1000-8000-00805f9b34fb' #Handle 34. 

    GAP_SERV = '00001800-0000-1000-8000-00805f9b34fb'
    DEVICE_NAME_CHAR = '00002a00-0000-1000-8000-00805f9b34fb' #Read. 
    APPEARANCE_CHAR = '00002a01-0000-1000-8000-00805f9b34fb' #Read. 
    PERIPHERAL_PRIVACY_CHAR = '00002a02-0000-1000-8000-00805f9b34fb' #Read. 

    GATT_SERV = '00001801-0000-1000-8000-00805f9b34fb' 
    SERVICE_CHANGED_CHAR = '00002a05-0000-1000-8000-00805f9b34fb' #Indicate. 
    GATT_CLIENT_CHAR_CONFIG_DESC = '00002902-0000-1000-8000-00805f9b34fb' #Handle 11. 

    DEVICE_INFORMATION_SERV = '0000180a-0000-1000-8000-00805f9b34fb'
    SYSTEM_ID_CHAR = '00002a23-0000-1000-8000-00805f9b34fb' #Read. 
    MODEL_NUMBER_STR_CHAR = '00002a24-0000-1000-8000-00805f9b34fb' #Read. 
    SERIAL_NUMBER_STR_CHAR = '00002a25-0000-1000-8000-00805f9b34fb' #Read. 
    FIRMWARE_REV_STR_CHAR = '00002a26-0000-1000-8000-00805f9b34fb' #Read. 
    HARDWARE_REV_STR_CHAR = '00002a27-0000-1000-8000-00805f9b34fb' #Read. 
    SOFTWARE_REV_STR_CHAR = '00002a28-0000-1000-8000-00805f9b34fb' #Read. 
    MANUFACTURER_STR_CHAR = '00002a29-0000-1000-8000-00805f9b34fb' #Read. 
    IEEE_REGULATORY_LIST_CHAR = '00002a2a-0000-1000-8000-00805f9b34fb' #Read. 
    PLUGNPLAY_ID_CHAR = '00002a50-0000-1000-8000-00805f9b34fb' #Read. 

    UNKNOWN_SERV = 'f000ffc0-0451-4000-b000-000000000000'
    UNKNOWN_CHAR_1 = 'f000ffc1-0451-4000-b000-000000000000' #write-without-response, write, notify. 
    UNKNOWN_DESC_1 = '00002902-0000-1000-8000-00805f9b34fb' #Handle 4099.
    UNKNOWN_DESC_2 = '00002901-0000-1000-8000-00805f9b34fb' #Handle: 4100.
    UNKNOWN_CHAR_2 = 'f000ffc2-0451-4000-b000-000000000000' #write-without-response, write, notify. 
    UNKNOWN_DESC_3 = '00002902-0000-1000-8000-00805f9b34fb' #Handle 4103. 
    UNKNOWN_DESC_4 = '00002901-0000-1000-8000-00805f9b34fb' #Handle: 4104.
    
    constantsList = [BLUETOOTH_ADDRESS, #0.
                     
                     CIRCUITCUBE_SERV, TX_CHAR, RX_CHAR, RX_CLIENT_CHAR_CONFIG_DESC, #1,2,3,4.

                     GAP_SERV, DEVICE_NAME_CHAR, APPEARANCE_CHAR, PERIPHERAL_PRIVACY_CHAR, #5,6,7,8.

                     GATT_SERV, SERVICE_CHANGED_CHAR, GATT_CLIENT_CHAR_CONFIG_DESC, #9,10,11.

                     DEVICE_INFORMATION_SERV, SYSTEM_ID_CHAR, MODEL_NUMBER_STR_CHAR, SERIAL_NUMBER_STR_CHAR, #12,13,14,15.
                     FIRMWARE_REV_STR_CHAR, HARDWARE_REV_STR_CHAR, SOFTWARE_REV_STR_CHAR, #16,17,18.
                     MANUFACTURER_STR_CHAR, IEEE_REGULATORY_LIST_CHAR, PLUGNPLAY_ID_CHAR, #19,20,21.

                     UNKNOWN_SERV, UNKNOWN_CHAR_1, UNKNOWN_DESC_1, UNKNOWN_DESC_2, UNKNOWN_CHAR_2, UNKNOWN_DESC_3, UNKNOWN_DESC_4] #22,23,24,25,26,27,28.
                     
    return constantsList[index] 

def setup(): #Clear terminal, display program header, prompt user to choose program mode. 
    os.system('cls')
    Console().print(
        Panel("[bold dodger_blue2]Python Control for Circuit Cubes Bluetooth Battery Cube by [italic]simon_code[/italic] [/bold dodger_blue2]", 
              style="bold white"))
    rich.print('[bold dodger_blue2]\n   Setting up: [/bold dodger_blue2]')
    mode = input('      Type "n" for normal mode, "d" for debug mode. \n')
    if mode not in ['n', 'd']: 
        rich.print('      [red]Invalid mode selected. [/red]')
        quit()
    if mode == 'n': 
        rich.print('      [underline]Normal[/underline] mode selected. ')
        mode = 'normal'
    if mode == 'd':
        rich.print('      [underline]Debug[/underline] mode selected. ')
        mode = 'debug'
    motorCode = input('      Select which two motor ports are being used. Type one of: "ab", "bc", "ca". \n')
    if motorCode not in ['ab', 'bc', 'ca']: 
        rich.print('      [red]Invalid motors selected. [/red]')
        quit()
    if motorCode == 'ab': 
        motors = [0, 1]
        rich.print('      Motors [underline]A+B[/underline] selected. ')
    if motorCode == 'bc': 
        motors = [1, 2]
        rich.print('      Motors [underline]B+C[/underline] selected. ')
    if motorCode == 'ca': 
        motors = [2, 0]
        rich.print('      Motors [underline]C+A[/underline] selected. ')
    return mode, motors

async def scanner(): #Scan for BLE (Bluetooth Low Energy) devices, identify Circuit Cube and return Bluetooth MAC address. 
    rich.print('[bold dodger_blue2]\n   Scanning for Bluetooth Battery Cube: [/bold dodger_blue2]')
    devices = await BleakScanner.discover()
    try: 
        if len(devices) == 0: 
            print('      No devices discovered. Make sure Bluetooth is turned on. ')
        else: 
            print(f'      {len(devices)} devices discovered. ')
            cubeDevice = [j for j in devices if 'Tenka' in str(j)] #Circuit Cube must be named "Tenka" in order to be detected. 
            for device in devices:
                print(f'         {device}')
            if len(cubeDevice) != 0: 
                print(f'      Cube found at: {str(cubeDevice[0])[:17]}. ') 
                address = str(cubeDevice[0])[:17]
            else: 
                rich.print('      [red]Bluetooth Circuit Cube not found. [/red]')
                quit()
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()
    return address

async def connectCube(address): #Attempt to connect to Cube. 
    rich.print('[bold dodger_blue2]\n   Establishing connection to Cube: [/bold dodger_blue2]')
    client = BleakClient(address)
    try: 
        print(f'      Connecting to Cube. ')
        await client.connect()
        print('      Initial connection successful. ')
        return client
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()
    
async def readDeviceInformation(client): #Read some device information from known GATT characteristics. 
    rich.print('[bold dodger_blue2]\n   Reading device information: [/bold dodger_blue2]')
    try:
        deviceName = await client.read_gatt_char(constants(6))
        deviceName = deviceName.decode('utf-8')
        print(f'      Name: {deviceName}. ')

        deviceAppearance = await client.read_gatt_char(constants(7))
        deviceAppearance = int.from_bytes(deviceAppearance, 'big')
        print(f'      Appearance code: {deviceAppearance}. ')

        serialNumber = await client.read_gatt_char(constants(15))
        serialNumber = serialNumber.decode('utf-8')
        print(f'      Serial number: {serialNumber}. ')

        firmware = await client.read_gatt_char(constants(16))
        firmware = firmware.decode('utf-8')
        print(f'      Firmware: {firmware}. ')

        hardware = await client.read_gatt_char(constants(17))
        hardware = hardware.decode('utf-8')
        print(f'      Hardware: {hardware}. ')

        software = await client.read_gatt_char(constants(18))
        software = software.decode('utf-8')
        print(f'      Software: {software}. ')

        tx = constants(2) 
        rx = constants(3)
        await client.write_gatt_char(tx, bytes('b', 'utf-8'))
        voltage = await client.read_gatt_char(rx)
        print(f'      Battery voltage: {voltage.decode("utf-8")}')
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()

def motorCommand(motor, velocity): #Construct motor command as three digit string. 
    if motor == 'A': 
        motor = 0 
    elif motor == 'B': 
        motor = 1
    elif motor == 'C': 
        motor = 2
    sign = '-' if velocity < 0 else '+'
    magnitude = abs(velocity)
    if magnitude == 0: 
        magnitude = 0
    else: 
        magnitude = 55+abs(velocity)
    commandString = f'{sign}{magnitude:03}{chr(ord('a') + motor)}'
    return commandString

async def keyboardControlLoop(client, motors): #Control motor velocities using arrow keys. 
    rich.print('[bold dodger_blue2]\n   Starting keyboard motor control: [/bold dodger_blue2]')
    if motors == [0, 1]: 
        one = 'A' 
        two = 'B'
    if motors == [1, 2]: 
        one = 'B'
        two = 'C'
    if motors == [2, 0]: 
        one = 'C'
        two = 'A'

    try: 
        print(f'      Use up and down arrow keys to control motor {one}. ')
        print(f'      Use left and right arrow keys to control motor {two}. ')
        print('      Press the space key to halt both motors. ')
        print('      Press escape key to end keyboard motor control. \n')
        tx = constants(2)
        velocity_one = velocity_two = 0
        
        with Live(f'      Motor {one} velocity: [bold green]{int(velocity_one/2)}%[/bold green]      Motor {two} velocity: [bold green]{int(velocity_two/2)}%[/bold green]') as live:
            while True: 
                if keyboard.is_pressed('up'): 
                    velocity_one -= 20
                if keyboard.is_pressed('down'): 
                    velocity_one += 20
                if keyboard.is_pressed('esc'):
                    break
                if velocity_one < -200: 
                    velocity_one = -200
                if velocity_one > 200: 
                    velocity_one = 200
                await client.write_gatt_char(tx, motorCommand(one, velocity_one).encode())
                
                if keyboard.is_pressed('left'): 
                    velocity_two -= 20
                if keyboard.is_pressed('right'): 
                    velocity_two += 20
                if keyboard.is_pressed('esc'):
                    break
                if velocity_two < -200: 
                    velocity_two = -200
                if velocity_two > 200: 
                    velocity_two = 200
                await client.write_gatt_char(tx, motorCommand(two, velocity_two).encode())

                if keyboard.is_pressed('space'): 
                    velocity_one = velocity_two = 0 

                live.update(f'      Motor {one} velocity: [bold green]{int(velocity_one/2)}%[/bold green]      Motor {two} velocity: [bold green]{int(velocity_two/2)}%[/bold green]')
                await asyncio.sleep(0.05)

    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()

async def discoverDeviceUUIDs(client): #Use bleak to discover all client services/characteristics/descriptors. 
    rich.print('[bold dodger_blue2]\n   Listing GATT service/characteristic/descriptor UUIDs from Cube: [/bold dodger_blue2]')
    services = client.services
    try: 
        for service in services:
            print(f'      Service: {service.uuid}')
            for characteristic in service.characteristics:
                print(f'         Characteristic: {characteristic.uuid} (Properties: {characteristic.properties})')
                for descriptor in characteristic.descriptors:
                    print(f'            Descriptor: {descriptor}')
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()

async def readDescriptors(client): #Read descriptor values. 
    rich.print('[bold dodger_blue2]\n   Reading GATT descriptors from Cube: [/bold dodger_blue2]')
    try: 
        handles = [11, 34, 4099, 4100, 4103, 4104]
        for i in range(len(handles)): 
            descriptor = await client.read_gatt_descriptor(handles[i])
            print(f'      {descriptor}')
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()

async def disconnectCube(client): #Halt all motors and properly disconnect Circuit Cube. 
    rich.print('[bold dodger_blue2]\n\n   Terminating connection to Cube: [/bold dodger_blue2]')
    try: 
        tx = constants(2)
        print('      Stopping all motors. ')
        await client.write_gatt_char(tx, motorCommand('A', 0).encode())
        await client.write_gatt_char(tx, motorCommand('B', 0).encode())
        await client.write_gatt_char(tx, motorCommand('C', 0).encode())
        print(f'      Ending connection to Bluetooth Battery Cube. ')
        await client.disconnect()
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()

async def main(): 
    mode, motors = setup()
    if mode == 'normal': 
        address = 'FC:58:FA:CF:64:4D' #THIS BLUETOOTH ADDRESS MUST BE CHANGED, IT IS UNIQUE TO EACH CUBE! 
        client = await connectCube(address)
        await keyboardControlLoop(client, motors)
        await disconnectCube(client)
    if mode == 'debug': 
        address = await scanner()
        client = await connectCube(address)
        await readDeviceInformation(client)
        await discoverDeviceUUIDs(client)
        await readDescriptors(client)
        await keyboardControlLoop(client, motors)
        await disconnectCube(client) 

asyncio.run(main())
