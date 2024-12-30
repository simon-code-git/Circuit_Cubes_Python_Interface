import os
import asyncio
from bleak import BleakClient, BleakScanner
import rich; from rich.panel import Panel; from rich.console import Console; from rich.live import Live
import keyboard

def setup(): #Clear terminal, display program header. 
    os.system('cls')
    Console().print(
        Panel("[bold dodger_blue2]Code for Finding Circuit Cube Bluetooth Address by [italic]simon_code[/italic] [/bold dodger_blue2]", 
              style="bold white"))

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
                rich.print(f'      Cube found at: [bold green]{str(cubeDevice[0])[:17]}[/bold green]. ')
                address = str(cubeDevice[0])[:17]
            else: 
                rich.print('      [red]Bluetooth Circuit Cube not found. [/red]')
                quit()
    except Exception as e: 
        rich.print(f'      [red not bold]{e}[/red not bold]')
        quit()
    return address

async def main(): 
    setup()
    address = await scanner()

asyncio.run(main())