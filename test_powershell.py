import subprocess

# PowerShell 命令
ps_command = '''Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "LeagueClientUx.exe" } | Select-Object -ExpandProperty CommandLine'''

# 使用 subprocess 执行 PowerShell 命令并捕获输出
process = subprocess.Popen(["powershell", "-Command", ps_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

# 解码输出为字符串，使用正确的编码处理字节流
stdout = stdout.decode("utf-8", errors="replace").strip()  # 使用 "replace" 处理解码错误的字符
stderr = stderr.decode("utf-8", errors="replace").strip()

# 输出结果
if stderr:
    print(f"Error: {stderr}")
else:
    print(f"Command Line: {stdout}")
