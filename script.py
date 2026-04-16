import os
import serial
import time


def vpype_layout_paragraph(paragraph, text_size, width, height, font="futural", line_spacing=1.2, output_file="output.gcode"):
    words = paragraph.split()
    lines = []
    current_line = ""

    def estimate_text_width(text):
        return len(text) * (text_size * 0.6) / 2.2

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

    total_lines = len(lines)
    max_height = text_size * line_spacing * total_lines / 2.5

    if max_height > height:
        raise ValueError(f"The text can't fit in the given height: {height}")

    vpype_commands = [
        "vpype",
        "--config adjusted.toml"
    ]

    lines = lines[::-1]

    for i in range(len(lines)):
        if i == len(lines) - 1:
            vpype_commands.append(f'text -f {font} -s {text_size} "{lines[i]}" translate 0 6mm rotate 270')
        else:
            vpype_commands.append(f'text -f {font} -s {text_size} "{lines[i]}" translate 0 6mm')

    vpype_commands.append("layout 0mmx0mm")
    vpype_commands.append("gwrite")
    vpype_commands.append(output_file)

    command_string = " ".join(vpype_commands)
    os.system(command_string)

    print(f"Generated G-code written to {output_file}")


def send_gcode_file_to_printer(file_path, port, baudrate=115200, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to printer on {port} at {baudrate} baud.")
        time.sleep(5)

        with open(file_path, 'r') as gcode_file:
            for line in gcode_file:
                gcode = line.strip()
                if gcode:
                    ser.write((gcode + '\n').encode())
                    print(f"Sent G-code: {gcode}")

                    time.sleep(0.5)
                    while True:
                        response = ser.readline().decode().strip()
                        if response.startswith('ok'):
                            break
                        elif response:
                            print(f"Printer response: {response}")

        ser.close()
        print("Finished sending file. Connection closed.")

    except Exception as e:
        print(f"An error occurred: {e}")
