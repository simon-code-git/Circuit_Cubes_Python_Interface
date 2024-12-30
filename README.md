# Python-Circuit-Cubes-Interface
A beginner-friendly Python interface for controlling the Circuit Cubes Bluetooth Battery Cube via Bluetooth Low Energy (BLE). 

# Usage 
## Dependencies
In order for this project to work, three packages are required: bleak, keyboard, and rich.  
Install these to your Python environment with `$ pip install bleak`, `$ pip install keyboard`, and `$ pip install rich`. 
## Connecting to Circuit Cube
Each Circuit Cube has a unique Bluetooth hardware address.  
In order to find it, run the file `GetBluetoothAddress.py`. This program will only work as expected if your Circuit Cube is named "Tenka".  
Then, make sure that you copy your Bluetooth address into line 240 of `CircuitCubePythonInterface.py`. 

# Credits
I would like to acknowledge the work of [blockninja124](https://github.com/blockninja124), [asperka](https://github.com/asperka), and [repkovsky](https://github.com/repkovsky). 
