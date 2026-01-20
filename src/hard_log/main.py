from soft_log import SoftLog as sl

sl = sl()

for el in range(10):
    line = sl.log("BOOT", f"Initializing mesh scan {el}", "bright_red")
    sl.console.print(line)