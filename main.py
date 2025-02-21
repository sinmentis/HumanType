#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import sys
import argparse
import threading

try:
    import pyautogui
    import keyboard
except ImportError:
    print("Please install the required dependencies first:")
    print("  pip install pyautogui keyboard")
    sys.exit(1)

# For playing Beep sound on Windows
try:
    import winsound
    PLAY_SOUND = True
except ImportError:
    PLAY_SOUND = False

# --------------------
# Global variables
# --------------------
STOPPED = False       # Indicates if typing has been stopped
TYPING_ACTIVE = False # Indicates if typing is currently active
i = 0                 # Tracks how many characters have been typed so far
lock = threading.Lock()
typing_thread = None

# We will run a small loop in main() that checks if we need to exit
should_exit = False   # Once typing is done or stopped, we'll set this to True

def play_beep(freq=800, duration=200):
    """
    Play a short beep sound (only works on Windows by default).
    """
    if PLAY_SOUND:
        winsound.Beep(freq, duration)

def calc_delay_per_char(text_length, wpm=None, duration=None):
    """
    Calculate the base average delay (seconds per character) based on:
    - wpm: words per minute
    OR
    - duration: how many total seconds to finish typing all characters

    If both wpm and duration are None, a default (wpm=40) is used.
    """
    if wpm is None and duration is None:
        wpm = 40  # default

    if wpm is not None:
        # Convert wpm -> characters/minute (assuming 1 word = 5 characters)
        # Then characters/second -> delay per character
        chars_per_minute = wpm * 5
        chars_per_second = chars_per_minute / 60.0
        if chars_per_second <= 0:
            return 0.3
        else:
            return 1.0 / chars_per_second
    else:
        # Use the duration to evenly distribute the typing time
        if text_length <= 0 or duration <= 0:
            return 0.3
        return float(duration) / float(text_length)

def typing_worker(
    text,
    base_delay,
    mistake_prob,
    mistake_len_min,
    mistake_len_max,
    random_delay_char,
    random_delay_space,
    random_jitter
):
    """
    The logic for typing in a separate thread:
      - Type characters one by one.
      - With probability `mistake_prob`, simulate a "mistake":
        * Type 1~6 random chars, then backspace them, then type the correct char.
      - Also insert random additional delays:
        * random_delay_char for each normal character
        * random_delay_space for a space character
        * plus some random jitter in [0, random_jitter]
      - If STOPPED=True is detected, print the leftover text and exit the loop.
      - If completed normally, print a message that it's all done.
    """
    global i, STOPPED, TYPING_ACTIVE, should_exit

    # Play "start typing" beep
    play_beep()

    while i < len(text):
        # Check if we were stopped
        if STOPPED:
            leftover = text[i:]
            print("\n==========")
            print("[Stopped] The following text was NOT typed yet:\n", leftover)
            break

        char = text[i]

        # 1) Simulate mistake with some probability
        if random.random() < mistake_prob:
            # choose a random length of mistake
            mistake_len = random.randint(mistake_len_min, mistake_len_max)
            # generate random wrong chars
            candidates = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;!?@#$%^&*"
            wrong_chars = ''.join(random.choice(candidates) for _ in range(mistake_len))
            pyautogui.typewrite(wrong_chars)
            # then backspace them
            for _ in range(mistake_len):
                pyautogui.press('backspace')

        # 2) Type the correct character
        pyautogui.typewrite(char)
        i += 1

        # 3) Calculate a random delay to simulate more human-like typing
        #    base_delay is from wpm/duration
        #    if char == ' ', add a bigger pause
        #    plus some random jitter
        delay = base_delay
        if char == ' ':
            delay += random_delay_space
        else:
            delay += random_delay_char

        # Add some small random jitter, e.g. up to random_jitter
        delay += random.uniform(0, random_jitter)

        # Sleep
        time.sleep(delay)

    else:
        # If the while loop ended without a break,
        # it means the entire text was typed successfully
        print("\n==========")
        print("[Completed] All text has been typed.")

    # Cleanup after finishing or stopping
    TYPING_ACTIVE = False
    STOPPED = True  # Mark as "done" so main loop can exit
    play_beep()  # Play end beep
    should_exit = True  # We'll use this to ensure we exit main

def on_toggle_hotkey(*args):
    """
    Callback for pressing the toggle hotkey (by default CTRL+F9).
      - If typing is not active, start it in a new thread.
      - If typing is active, we set STOPPED to True so that the worker breaks.
    """
    global STOPPED, TYPING_ACTIVE, typing_thread, i

    with lock:
        if not TYPING_ACTIVE:
            # If we previously typed some chars and then stopped,
            # and want to re-start from the beginning, reset i if you want:
            # i = 0
            TYPING_ACTIVE = True
            STOPPED = False
            # The arguments are passed in by the hotkey,
            # they contain the text, delays, etc.
            (text,
             base_delay,
             mistake_prob,
             mistake_len_min,
             mistake_len_max,
             random_delay_char,
             random_delay_space,
             random_jitter) = args

            typing_thread = threading.Thread(
                target=typing_worker,
                args=(
                    text,
                    base_delay,
                    mistake_prob,
                    mistake_len_min,
                    mistake_len_max,
                    random_delay_char,
                    random_delay_space,
                    random_jitter
                ),
                daemon=True
            )
            typing_thread.start()
        else:
            # If typing is active, let's stop
            STOPPED = True
            # i is NOT reset, so if you want to resume from the middle next time,
            # you can re-comment the i=0 above. But for now, let's just let it end.
            # We'll also set should_exit so the script can terminate
            # (the worker sees STOPPED and prints leftover)
            # The worker will set should_exit = True
            pass

def main():
    parser = argparse.ArgumentParser(description="Simulate human typing with random delays and mistakes. Press CTRL+F9 once to start, then press again to stop.")
    parser.add_argument('--text', type=str, required=True,
                        help='The text to type.')
    parser.add_argument('--wpm', type=float, default=None,
                        help='Typing speed in words per minute (optional).')
    parser.add_argument('--duration', type=float, default=None,
                        help='Total time (seconds) to finish typing all text (optional).')

    # Probability & length of mistakes
    parser.add_argument('--mistake-prob', type=float, default=0.02,
                        help='Probability of making a mistake (default=0.02).')
    parser.add_argument('--mistake-len-min', type=int, default=1,
                        help='Minimum length of a random mistake (default=1).')
    parser.add_argument('--mistake-len-max', type=int, default=6,
                        help='Maximum length of a random mistake (default=6).')

    # Additional random delays
    parser.add_argument('--random-delay-char', type=float, default=0.03,
                        help='Extra delay (seconds) added for each character (default=0.03).')
    parser.add_argument('--random-delay-space', type=float, default=0.1,
                        help='Extra delay (seconds) added for space character (default=0.1).')
    parser.add_argument('--random-jitter', type=float, default=0.05,
                        help='Maximum random jitter (seconds) added each time (default=0.05).')

    # Hotkey
    parser.add_argument('--hotkey', type=str, default='ctrl+f9',
                        help='Hotkey to start/stop typing (default="ctrl+f9").')

    args = parser.parse_args()

    text = args.text
    base_delay = calc_delay_per_char(len(text), wpm=args.wpm, duration=args.duration)

    # Register the hotkey to toggle start/stop
    keyboard.add_hotkey(
        args.hotkey,
        on_toggle_hotkey,
        args=(
            text,
            base_delay,
            args.mistake_prob,
            args.mistake_len_min,
            args.mistake_len_max,
            args.random_delay_char,
            args.random_delay_space,
            args.random_jitter
        )
    )

    print("Script is running.")
    print("=======================================")
    print(" 1) Place your cursor/focus where you want the text to be typed.")
    print(f" 2) Press {args.hotkey.upper()} the first time to START typing.")
    print(f" 3) Press {args.hotkey.upper()} the second time to STOP typing.")
    print("    (Any remaining text will be printed to the console.)")
    print("=======================================")
    print("Press Ctrl+C here to terminate the script if needed.\n")

    # Instead of keyboard.wait(), let's do a small loop
    # that checks if we are done (STOPPED + not TYPING_ACTIVE).
    while True:
        time.sleep(0.2)
        if STOPPED and not TYPING_ACTIVE:
            # We can unhook the hotkey to avoid re-triggering
            keyboard.unhook_all()
            print("[Exiting] The typing thread has finished or was stopped.\n")
            sys.exit(0)

if __name__ == '__main__':
    main()
