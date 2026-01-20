from soft_log2 import SoftLog as sl

sl = sl()

for el in range(10):
    sl.log("BOOT", f"Initializing mesh scan {el}")

sl.log("INFO", "Mesh scan in progress...")
sl.log("DEBUG", "Scanning node 1")
sl.log("WARN", "Node 2 response delayed")
sl.log("ERROR", "Node 3 failed to respond")
sl.log("SUCCESS", "Mesh scan complete.")