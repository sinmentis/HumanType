# HumanType ✨

<div align="center">
    <img src="resource/logo.webp" width="256">
</div>

**HumanType** is a realistic typing simulator that mimics human typing behavior by typing one character at a time with random delays, occasional simulated mistakes, and configurable parameters. It’s perfect for automating typing in applications like Overleaf or any text editor while preserving a human-like behavior. 😎⌨️


## Features 🚀

- **Realistic Typing Simulation:**
  Mimics human typing by adding random delays between keystrokes, extra pauses for spaces, and even simulates mistakes with auto-backspacing.

- **Fully Configurable:**
  Customize typing speed (`wpm`), overall duration, mistake probability, random delay jitter, and more via command-line arguments.

- **Cross-Language Support:**
  Works with multiple languages (e.g. English, Chinese). Just ensure your system input method is set correctly. 🌐

- **Hotkey Start/Stop:**
  Start typing with a single hotkey (default: `CTRL+F9`) and stop anytime with the same hotkey. 🛑

- **Visual and Audio Feedback:**
  Plays a beep sound at the start and end (Windows only) to indicate when typing begins or stops.


## Demo 📽️

Below is a short demo of how HumanType works:

1. **Place the cursor** where you want the text to be typed.
2. **Press `CTRL+F9`** to start typing.
3. **Press `CTRL+F9` again** to stop the simulation, and the remaining text will be printed in the console.

<div align="center">
    <img src="resource/demo.gif" width="500">
</div>


## Installation 🛠️

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/sinmentis/HumanType.git
   cd HumanType
   ```

2. **Install dependency**
   ```bash
   python -m venv .venv  # Optional
   pip install -U -r requirements.txt
   ```


## Usage 💡

Run the script with your desired parameters:


```bash
python main.py.py --text "Hello, this is a demo of HumanType!" --wpm 40
```

## Command-line Parameters ⚙️
| Parameter | Description & Effect |
| --- | --- |
| --text "..." 📜 | The text to type (Required). |
| --wpm ⚡ | Typing speed in words per minute. Higher = faster typing. (Default: 40) |
| --duration ⏳ | Total time (seconds) to finish typing. Overrides --wpm. |
| --mistake-prob 🎭 | Probability of making a mistake (Default: 0.02, or 2%). Higher = more typos. |
| --mistake-len-min 🔠 | Minimum length of a mistake (Default: 1 character). |
| --mistake-len-max 🔡 | Maximum length of a mistake (Default: 6 characters). |
| --random-delay-char ⌛ | Extra delay (seconds) for each character (Default: 0.03s). |
| --random-delay-space ⏸️ | Extra delay (seconds) for spaces, simulating thinking pauses (Default: 0.1s). |
| --random-jitter 🎲 | Additional random time jitter per key press (Default: 0.05s). |
| --hotkey 🎹 | Hotkey to start/stop typing (Default: ctrl+f9). |


## Example Configurations 🎯
1️⃣ **Normal speed typing:**

```bash
python main.py.py --text "This is a demo." --wpm 50
```
2️⃣ **Typing in exactly 10 seconds:**

```bash
python main.py.py --text "This is a timed test." --duration 10
```
3️⃣ **More realistic mistakes (5% chance, max 3 chars per mistake):**

```bash
python main.py.py --text "Human-like typos." --mistake-prob 0.05 --mistake-len-max 3
```
4️⃣ **Slower typing with pauses at spaces:**

```bash
python main.py.py --text "Thinking... like a human." --random-delay-space 0.3
```

## Contributing 🤝
Contributions are welcome! Feel free to open issues or submit pull requests if you have ideas to improve **HumanType** .


## License 📄
This project is licensed under the [MIT License](https://github.com/sinmentis/HumanType/blob/main/LICENSE) .

