import subprocess
import time
import os
import sys
from colorama import Fore, Style, init
from pyfiglet import Figlet
from datetime import datetime
import threading

init(autoreset=True)

PING_COUNT = 4
PING_INTERVAL = 3
CHANGE_THRESHOLD = 50
CHECK_TIMES = 5
PACKET_LOSS_THRESHOLD = 25

exit_flag = False

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def clear_last_line():
    sys.stdout.write('\x1b[1A')  # Move cursor up one line
    sys.stdout.write('\x1b[2K')  # Clear entire line
    sys.stdout.flush()

def print_header():
    clear_screen()
    f = Figlet(font='slant')
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    app_name_ascii = f.renderText(script_name)
    print(Fore.CYAN + app_name_ascii + Style.RESET_ALL)
    print(Fore.RED + "by DoomSlayer".center(80) + Style.RESET_ALL)
    print("\n" + "-" * 80)

def run_ping(host):
    try:
        result = subprocess.run(
            ["ping", "-c", str(PING_COUNT), host],
            capture_output=True, text=True
        )
        output = result.stdout

        times = []
        lost_packets = 0

        for line in output.splitlines():
            if "packet loss" in line:
                loss_part = line.split(",")[2].strip()
                lost_packets = float(loss_part.split("%")[0])
            if "time=" in line:
                part = line.split("time=")[1]
                time_ms = part.split()[0]
                times.append(float(time_ms))

        avg_ping = sum(times) / len(times) if times else None
        return avg_ping, lost_packets, output
    except Exception as e:
        return None, None, str(e)

def loading_animation(seconds):
    animation = ['|', '/', '-', '\\']
    msg = Fore.YELLOW + "Waiting to ping... " + Style.RESET_ALL
    for i in range(seconds * 4):
        if exit_flag:
            break
        print("\r" + msg + animation[i % len(animation)], end='', flush=True)
        time.sleep(0.25)
    print("\r" + " " * (len(msg) + 1) + "\r", end='')

def input_listener():
    global exit_flag
    while True:
        user_input = input().strip().lower()
        if user_input in ['exit', 'quit']:
            exit_flag = True
            print(Fore.RED + "\nExit command received, stopping..." + Style.RESET_ALL)
            break

def main():
    global exit_flag
    print_header()
    host = input(f"Enter host to ping (default: {Fore.YELLOW}google.com{Style.RESET_ALL}): ").strip()
    if not host:
        host = "google.com"

    print(f"\nPinging {Fore.YELLOW}{host}{Style.RESET_ALL} every {PING_INTERVAL} seconds. Type {Fore.RED}exit{Style.RESET_ALL} or {Fore.RED}quit{Style.RESET_ALL} to quit anytime.\n")

    ping_history = []

    # Start input listener thread for exit command
    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

    try:
        while not exit_flag:
            avg_ping, lost_packets, output = run_ping(host)
            now = datetime.now().strftime("%H:%M:%S")

            if avg_ping is None:
                print(Fore.RED + f"[{now}] Ping failed or host unreachable." + Style.RESET_ALL)
            else:
                print(Fore.GREEN + f"[{now}] Avg {Fore.YELLOW}Ping{Fore.GREEN}: {avg_ping:.2f} ms | Packet Loss: {lost_packets}%" + Style.RESET_ALL)
                ping_history.append(avg_ping)

                if len(ping_history) > CHECK_TIMES:
                    old_ping = ping_history[-(CHECK_TIMES + 1)]
                    diff = abs(avg_ping - old_ping)

                    if diff > CHANGE_THRESHOLD or lost_packets > PACKET_LOSS_THRESHOLD:
                        print(Fore.RED + f"WARNING: Possible network attack detected! Ping changed by {diff:.2f} ms or high packet loss." + Style.RESET_ALL)

                if len(ping_history) > CHECK_TIMES + 10:
                    ping_history.pop(0)

            loading_animation(PING_INTERVAL)

        print(Fore.CYAN + "Thx for using that" + Style.RESET_ALL)
        time.sleep(3)
        clear_last_line()

    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Exiting... Goodbye!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
