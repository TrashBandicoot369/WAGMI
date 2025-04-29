#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import datetime

def log(message):
    """Write a timestamped log message to both console and file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # Also write to log file
    with open("watchdog.log", "a") as log_file:
        log_file.write(log_message + "\n")

def main():
    """Main watchdog function that keeps qwant3.py running forever"""
    log("Starting watchdog for qwant3.py")
    
    restart_count = 0
    max_restarts = 999999  # Effectively unlimited restarts
    
    while restart_count < max_restarts:
        try:
            # Start qwant3.py and wait for it to finish (which should only happen if it crashes)
            log(f"Starting qwant3.py (restart #{restart_count})")
            
            # Make sure to pass through all output to the console
            process = subprocess.Popen(
                [sys.executable, "qwant3.py"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line, end="")  # Print each line as it comes
                
            # Process has ended
            return_code = process.wait()
            
            log(f"qwant3.py exited with code {return_code}")
            
            # If it exited with code 0, it was a clean exit - still restart
            restart_count += 1
            
            # Small delay before restart
            time.sleep(5)
            
        except KeyboardInterrupt:
            log("Watchdog stopped by user (Ctrl+C)")
            break
        except Exception as e:
            log(f"Error in watchdog: {e}")
            restart_count += 1
            time.sleep(10)  # Longer delay if the watchdog itself has an error
    
    log(f"Watchdog exiting after {restart_count} restarts")

if __name__ == "__main__":
    main() 