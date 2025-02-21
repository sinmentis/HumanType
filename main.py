#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulated human typing script with random delays and mistakes.
Press the designated hotkey to start and stop the typing process.
"""

import time
import random
import sys
import argparse
import threading
from dataclasses import dataclass

try:
    import pyautogui
    import keyboard
except ImportError:
    print("Install required dependencies: pip install pyautogui keyboard")
    sys.exit(1)

try:
    import winsound
    PLAY_SOUND = True
except ImportError:
    PLAY_SOUND = False


def play_beep(freq: int = 800, duration: int = 200) -> None:
    """Play a beep sound on Windows if available."""
    if PLAY_SOUND:
        winsound.Beep(freq, duration)


def calc_delay_per_char(text_length: int, wpm: float = None,
                        duration: float = None) -> float:
    """
    Calculate delay per character based on words per minute or total duration.
    If neither wpm nor duration is provided, defaults to 40 wpm.
    """
    if wpm is None and duration is None:
        wpm = 40
    if wpm is not None:
        chars_per_min = wpm * 5
        chars_per_sec = chars_per_min / 60.0
        return 1.0 / chars_per_sec if chars_per_sec > 0 else 0.3
    return float(duration) / text_length if text_length > 0 and duration > 0 else 0.3


@dataclass
class TypingConfig:
    """
    Configuration parameters for the typing simulation.
    """
    base_delay: float
    mistake_prob: float
    mistake_len_min: int
    mistake_len_max: int
    random_delay_char: float
    random_delay_space: float
    random_jitter: float


class Typer:
    """Manages the state and logic of the simulated typing process."""
    def __init__(self):
        self.stopped = False
        self.typing_active = False
        self.exit_flag = False
        self.typing_thread = None
        self.lock = threading.Lock()

    def typing_worker(self, text: str, config: TypingConfig) -> None:
        """Worker thread that simulates human typing."""
        play_beep()
        index = 0
        while index < len(text):
            if self.stopped:
                leftover = text[index:]
                print("\n==========\n[Stopped] Remaining text:\n", leftover)
                break
            char = text[index]
            if random.random() < config.mistake_prob:
                mistake_len = random.randint(config.mistake_len_min,
                                             config.mistake_len_max)
                candidates = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                              ".,:;!?@#$%^&*")
                wrong_chars = ''.join(random.choice(candidates)
                                      for _ in range(mistake_len))
                pyautogui.typewrite(wrong_chars)
                for _ in range(mistake_len):
                    pyautogui.press('backspace')
            pyautogui.typewrite(char)
            index += 1
            delay = config.base_delay + (
                config.random_delay_space if char == ' ' else config.random_delay_char)
            delay += random.uniform(0, config.random_jitter)
            time.sleep(delay)
        else:
            print("\n==========\n[Completed] All text typed.")
        self.typing_active = False
        self.stopped = True
        play_beep()
        self.exit_flag = True

    def on_toggle_hotkey(self, text: str, config: TypingConfig) -> None:
        """
        Hotkey callback to start or stop the typing process.
        Starts a new thread if not active; otherwise, stops the current process.
        """
        with self.lock:
            if not self.typing_active:
                self.typing_active = True
                self.stopped = False
                self.typing_thread = threading.Thread(
                    target=self.typing_worker, args=(text, config), daemon=True)
                self.typing_thread.start()
            else:
                self.stopped = True


def main() -> None:
    """Parse arguments, set up hotkey, and run the typing simulation."""
    parser = argparse.ArgumentParser(
        description=("Simulate human typing with random delays and mistakes. "
                     "Press the designated hotkey to start/stop the process."))
    parser.add_argument('--text', type=str, required=True, help='Text to type.')
    parser.add_argument('--wpm', type=float, default=None,
                        help='Typing speed (words per minute).')
    parser.add_argument('--duration', type=float, default=None,
                        help='Total time (seconds) to finish typing.')
    parser.add_argument('--mistake-prob', type=float, default=0.02,
                        help='Probability of making a mistake.')
    parser.add_argument('--mistake-len-min', type=int, default=1,
                        help='Minimum mistake length.')
    parser.add_argument('--mistake-len-max', type=int, default=6,
                        help='Maximum mistake length.')
    parser.add_argument('--random-delay-char', type=float, default=0.03,
                        help='Extra delay for each character.')
    parser.add_argument('--random-delay-space', type=float, default=0.1,
                        help='Extra delay for space characters.')
    parser.add_argument('--random-jitter', type=float, default=0.05,
                        help='Maximum random jitter.')
    parser.add_argument('--hotkey', type=str, default='ctrl+f9',
                        help='Hotkey to toggle typing.')
    args = parser.parse_args()

    text = args.text
    base_delay = calc_delay_per_char(len(text), wpm=args.wpm,
                                     duration=args.duration)
    config = TypingConfig(base_delay=base_delay,
                          mistake_prob=args.mistake_prob,
                          mistake_len_min=args.mistake_len_min,
                          mistake_len_max=args.mistake_len_max,
                          random_delay_char=args.random_delay_char,
                          random_delay_space=args.random_delay_space,
                          random_jitter=args.random_jitter)

    typer = Typer()
    keyboard.add_hotkey(args.hotkey, typer.on_toggle_hotkey, args=(text, config))
    print("Script is running.\n=======================================")
    print("1) Place the cursor where you want the text to appear.")
    print(f"2) Press {args.hotkey.upper()} to start typing.")
    print(f"3) Press {args.hotkey.upper()} to stop typing (remaining text will be shown).")
    print("=======================================")
    print("Press Ctrl+C to terminate the script.\n")

    while True:
        time.sleep(0.2)
        if typer.exit_flag and not typer.typing_active:
            keyboard.unhook_all()
            print("[Exiting] Typing process finished or stopped.\n")
            sys.exit(0)


if __name__ == '__main__':
    main()
