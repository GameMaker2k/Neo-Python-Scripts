import sys
import time
import os
import subprocess

def format_time(seconds):
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m{secs:.3f}s"

def main():
    if len(sys.argv) < 2:
        print("Usage: python mytime.py command [args...]")
        sys.exit(1)

    command = sys.argv[1:]

    # Record start times
    start_wall = time.perf_counter()
    start_times = os.times()

    # Run the command
    try:
        subprocess.run(command)
    except Exception as e:
        print(f"Error running command: {e}")
        sys.exit(1)

    # Record end times
    end_wall = time.perf_counter()
    end_times = os.times()

    # Compute differences
    wall_time = end_wall - start_wall
    user_time = (end_times.user + end_times.children_user) - (start_times.user + start_times.children_user)
    sys_time = (end_times.system + end_times.children_system) - (start_times.system + start_times.children_system)

    # Output the results
    print(f"\nreal\t{format_time(wall_time)}")
    print(f"user\t{format_time(user_time)}")
    print(f"sys\t{format_time(sys_time)}")

if __name__ == "__main__":
    main()
