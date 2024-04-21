import subprocess
import os
import shutil
import json
import requests


def load_voices():
    # Check if the file exists in the local directory
    if not os.path.exists("../voices.json"):
        # If the file does not exist, load it from the URL
        url = "https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4"
        response = requests.get(url)
        data = response.json()

        # Save the data to a local file
        with open("../voices.json", "w") as file:
            json.dump(data, file)
    else:
        # If the file exists locally, load it
        with open("../voices.json", "r") as file:
            data = json.load(file)

    # Create a list with all "ShortName"
    available_voices_short_names = [voice["ShortName"] for voice in data]

    return available_voices_short_names


# voices = {
#     "fr": 'fr-BE-CharlineNeural',
#     "en": 'en-GB-LibbyNeural',
# }

# command : "tts" or "playback"
def generate_mp3_file(
        input_text_file_path,
        output_mp3_file_path,
        voice,
        playback_rate_percentage=100,
        volume_percentage=100,
        pitch_hz=0,
        command='tts'):

    if command not in ('playback', 'tts'):
        print("invalid command")
        return

    volume_flag = generate_flag(volume_percentage, 'volume', '%')
    playback_rate_flag = generate_flag(playback_rate_percentage, 'rate', '%')
    pitch_flag = generate_pitch_flag(pitch_hz)

    # Command to install the edge-tts package using pip
    command_to_execute = ["pip", "install", "edge-tts"]
    # Execute the command
    try:
        result = subprocess.run(command_to_execute, capture_output=True, text=True)
        if result.returncode == 0:
            print("edge-tts installed successfully.")
        else:
            print("Failed to install edge-tts:", result.stderr)
    except Exception as e:
        print("Error:", e)

    command_to_execute = f"edge-{command}"
    if shutil.which(command_to_execute) is not None:
        print("'edge-tts' command is available in the PATH.")
    else:
        print("'edge-tts' command is not available in the PATH.")

    tts_path = shutil.which(command_to_execute)

    command_to_execute = [
        # "edge-tts",
        tts_path,
        "-f",
        f'"{input_text_file_path}"',
        "--write-media",
        f'"{output_mp3_file_path}"',
        "--voice",
        voice
    ]

    if volume_flag != '':
        command_to_execute.append(volume_flag)

    if playback_rate_flag != '':
        command_to_execute.append(playback_rate_flag)

    if pitch_flag != '':
        command_to_execute.append(pitch_flag)

    os_command = ' '.join(command_to_execute)
    print(os_command)
    exit_code = os.system(os_command)

    # Check the exit code to determine if the command was successful
    if exit_code == 0:
        print("Command executed successfully.")
    else:
        print("Error executing command.")


def generate_flag(percentage, flag_name, unit):
    if percentage == 100:
        return ""
    elif percentage == 0:
        return f"--{flag_name}=-100{unit}"
    elif percentage > 100:
        return f"--{flag_name}=+{percentage - 100}{unit}"
    else:
        return f"--{flag_name}=-{100 - percentage}{unit}"


def generate_pitch_flag(variation_hz=0):
    if variation_hz == 0:
        return ""

    #sign = "+" if variation_hz > 0 else "-"
    return f'--pitch={variation_hz}hz'
    #return f'--pitch={sign}{variation_hz}'




