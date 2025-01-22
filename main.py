import tkinter as tk
from tkinter import filedialog
import base64
import os

def create_bat_with_embedded_zip(zip_file_path, output_dir):
    bat_file_path = os.path.join(output_dir, 'extract_zip.bat')

    # 读取文件并将其分块编码为Base64
    def encode_file_in_chunks(file_path, chunk_size=3 * 1024 * 1024):  # 每块大小为3MB
        encoded_chunks = []
        with open(file_path, 'rb') as file:
            while chunk := file.read(chunk_size):
                encoded_chunks.append(base64.b64encode(chunk).decode('utf-8'))
        return encoded_chunks

    encoded_chunks = encode_file_in_chunks(zip_file_path)

    with open(bat_file_path, 'w') as bat_file:
        bat_file.write('@echo off\n')
        bat_file.write('echo Extracting ZIP file...\n')
        bat_file.write('if exist temp_zip.zip del temp_zip.zip\n')

        # 写入Base64编码的ZIP文件
        for i, chunk in enumerate(encoded_chunks):
            temp_file = f'temp_zip_base64_part_{i}.txt'
            with open(os.path.join(output_dir, temp_file), 'w') as temp:
                temp.write(chunk)
            bat_file.write(f'type {temp_file} >> temp_zip_base64.txt\n')
            bat_file.write(f'del {temp_file}\n')

        # 解码Base64为ZIP文件
        bat_file.write('certutil -decode temp_zip_base64.txt temp_zip.zip\n')
        bat_file.write('del temp_zip_base64.txt\n')

        # 使用PowerShell脚本来显示进度条并解压ZIP文件
        bat_file.write('powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference=\'Continue\';\n')
        bat_file.write('$zipfile = \'temp_zip.zip\';\n')
        bat_file.write('$destination = \'.\';\n')
        bat_file.write('$shell = New-Object -ComObject shell.application;\n')
        bat_file.write('$zip = $shell.NameSpace($zipfile);\n')
        bat_file.write('$items = $zip.Items();\n')
        bat_file.write('$count = $items.Count;\n')
        bat_file.write('for ($i = 0; $i -lt $count; $i++) {\n')
        bat_file.write('    $shell.NameSpace($destination).CopyHere($items.Item($i));\n')
        bat_file.write('    Write-Progress -Activity \'Extracting\' -Status "$($i+1)/$count" -PercentComplete (($i+1)/$count*100);\n')
        bat_file.write('}\n')
        bat_file.write('"\n')

        bat_file.write('del temp_zip.zip\n')
        bat_file.write('echo Extraction complete.\n')
        bat_file.write('exit /b\n')

    print(f'BAT file created at: {bat_file_path}')

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
    if file_path:
        file_path_var.set(file_path)

def browse_directory():
    output_dir = filedialog.askdirectory()
    if output_dir:
        output_dir_var.set(output_dir)

def generate_bat():
    zip_file_path = file_path_var.get()
    output_dir = output_dir_var.get()
    if zip_file_path and output_dir:
        create_bat_with_embedded_zip(zip_file_path, output_dir)
        result_label.config(text="BAT文件已生成！")
    else:
        result_label.config(text="请选择ZIP文件和输出目录。")

# 创建主窗口
root = tk.Tk()
root.title("ZIP打包成BAT工具")

# ZIP文件路径选择
file_path_var = tk.StringVar()
file_label = tk.Label(root, text="选择ZIP文件:")
file_label.pack()
file_entry = tk.Entry(root, textvariable=file_path_var, width=50)
file_entry.pack()
file_button = tk.Button(root, text="浏览", command=browse_file)
file_button.pack()

# 输出目录选择
output_dir_var = tk.StringVar()
output_label = tk.Label(root, text="选择输出目录:")
output_label.pack()
output_entry = tk.Entry(root, textvariable=output_dir_var, width=50)
output_entry.pack()
output_button = tk.Button(root, text="浏览", command=browse_directory)
output_button.pack()

# 生成BAT文件按钮
generate_button = tk.Button(root, text="生成BAT文件", command=generate_bat)
generate_button.pack()

# 结果标签
result_label = tk.Label(root, text="")
result_label.pack()

# 运行主循环
root.mainloop()