import subprocess


import os

def vpype_layout_paragraph(paragraph, text_size, width, height, font="futural", line_spacing=1.2, output_file="output.gcode"):
    words = paragraph.split()
    lines = []
    current_line = ""
    # Dummy function to estimate text width (you can make it more accurate based on the font's properties)
    def estimate_text_width(text):
        return len(text) * (text_size * 0.6) / 2.2 # Assuming each character is 0.6 times the text size wide
    
    # Break the paragraph into lines that fit the specified width
    for word in words:
        if estimate_text_width(current_line + " " + word) <= width:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Calculate vertical spacing (line_spacing is a multiplier for text_size)
    total_lines = len(lines)
    max_height = text_size * line_spacing * total_lines / 2.5
     
    if max_height > height:
        raise ValueError(f"The text can't fit in the given height: {height}")
    
    # vpype command construction
    vpype_commands = [
        "vpype",
        "--config adjusted.toml"
    ]
    
    current_y = 1.2+text_size  # Start from the top
    
    lines = lines[::-1]
    #current_y = height

    switch = True
    test = 50

    # vpype_commands.append(f'text -f {font} -s {text_size} "." translate -- -20mm')
    #vpype_commands.append(f'text -f {font} -s {text_size} "." translate 20mm 0mm')
    # vpype_commands.append(f'text -f {font} -s {text_size} "." rotate 90 translate 0 0') # Move up by line height
    #vpype_commands.append(f'text -f {font} -s {text_size} "." rotate -- -90') # Move up by line height

    for i in range(len(lines)):
        if i == len(lines) - 1:
            vpype_commands.append(f'text -f {font} -s {text_size} "{lines[i]}" translate 0 6mm rotate 270') # Move up by line height
        else:
            vpype_commands.append(f'text -f {font} -s {text_size} "{lines[i]}" translate 0 6mm') # Move up by line height
        print(current_y)
    # Add layout (if needed) and save output
    width = 0
    height = 0
    vpype_commands.append(f"layout {width}mmx{height}mm")
    vpype_commands.append("gwrite")
    vpype_commands.append(output_file)

    # Run vpype
    command_string = " ".join(vpype_commands)
    print(vpype_commands)
    os.system(command_string)
    
    print(f"Generated G-code written to {output_file}")
    pass


# Example Usage
# paragraph = "Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines.Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines.Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines.Hello, World! This is a test paragraph that will be laid out using vpype in multiple lines. Hello, World! "
# vpype_layout_paragraph(paragraph, text_size=15, width=200, height=200)



import serial
import time

def send_gcode_file_to_printer(file_path, port, baudrate=115200, timeout=1):
    try:
        # Open serial connection to the printer
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to printer on {port} at {baudrate} baud.")
        time.sleep(5)
        
        # Open the G-code file
        with open(file_path, 'r') as gcode_file:
            for line in gcode_file:
                gcode = line.strip()
                if gcode:
                    # Send each line of G-code
                    ser.write((gcode + '\n').encode())
                    print(f"Sent G-code: {gcode}")
                    
                    # Wait for the printer's response
                    time.sleep(0.5)  # Adjust the delay if needed
                    while True:
                        response = ser.readline().decode().strip()
                        if response.startswith('ok'):
                            break
                        elif response:
                            print(f"Printer response: {response}")
        
        # Close the serial connection
        ser.close()
        print("Finished sending file. Connection closed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    pass

# Example usage:
gcode_file_path = "output.gcode"  # Replace with your file path
port = "/dev/ttyUSB0"  # Adjust for your printer's port
send_gcode_file_to_printer(gcode_file_path, port)
