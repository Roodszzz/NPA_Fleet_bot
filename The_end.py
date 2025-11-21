

import os
import shutil
from tqdm import tqdm
import win32com.client as win32

# Путь к основной папке
base_dir = r"C:\Users\OleRud441\OneDrive - Norwegian People's Aid\Desktop\NPA_Fleet_bot\Result\Shyroke"

# Папка назначения
end_dir = os.path.join(base_dir, "the end")
os.makedirs(end_dir, exist_ok=True)

excel_files = []

# Собираем список всех Excel файлов в подпапках
for folder_name in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith((".xls", ".xlsx")):
                source_file = os.path.join(folder_path, file_name)
                excel_files.append(source_file)

print(f"Найдено Excel файлов: {len(excel_files)}")
print("Начинаю копирование и конвертацию...\n")

# Запускаем Excel COM объект через DispatchEx
excel = win32.DispatchEx("Excel.Application")

for source_file in tqdm(excel_files, desc="Обработка файлов", ncols=80):
    file_name = os.path.basename(source_file)
    dest_file = os.path.join(end_dir, file_name)

    # Копирование Excel
    shutil.copy2(source_file, dest_file)

    # Путь для PDF
    pdf_file = os.path.join(end_dir, os.path.splitext(file_name)[0] + ".pdf")

    # Конвертация в PDF
    wb = excel.Workbooks.Open(os.path.abspath(dest_file))
    wb.ExportAsFixedFormat(0, pdf_file)
    wb.Close()

# Закрываем Excel
excel.Quit()

print("\n====================================")
print("====  КОПИРОВАНИЕ + PDF ГОТОВО!  ====")
print("====================================")
