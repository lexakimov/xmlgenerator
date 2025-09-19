import os
import shutil
import subprocess
import sys
import time

from xmlgenerator import __version__

# --- Конфигурация сборки Nuitka ---

# Имя основного скрипта вашего приложения
main_script = "xmlgenerator/bootstrap.py"

# Имя выходного исполняемого файла (без расширения)
output_filename_base = "xmlgenerator"

# Директория для собранного файла
output_dir = "dist_native"

# Собрать в один файл? (True/False)
use_onefile = True

build_time = time.time()
build_time = str(int(build_time))

file_ver = f"{build_time[-4]}.{build_time[-3]}.{build_time[-2]}.{build_time[-1]}"

print(file_ver)

# Дополнительные опции Nuitka (добавляйте сюда нужные флаги)
extra_nuitka_options = [
    # "--show-progress",
    "--no-deployment-flag=self-execution", # Флаг для исправления ошибки
    "--standalone",
    # "--python-flag=no_site",
    # "--onefile-no-compression",
    "--follow-stdlib",
    # "--nofollow-import-to=tkinter",
    # "--include-package=some_package",

    "--product-name=xmlgenerator",
    f"--product-version={__version__}",
    f"--file-version={file_ver}",
    "--onefile-tempdir-spec={CACHE_DIR}/{PRODUCT}/{VERSION}",

    "--lto=yes",                  # Use link time optimizations (MSVC, gcc, clang).
    # "--static-libpython=yes",   # Use static link library of Python    undefined symbol: PyList_New

    # "--plugin-list",
    "--enable-plugin=anti-bloat",
    "--enable-plugin=pylint-warnings",
    "--enable-plugin=no-qt",
]

# --- Логика сборки ---

# Определяем базовое имя скрипта для имени директории сборки
main_script_basename = os.path.splitext(os.path.basename(main_script))[0]

# Определяем ПОТЕНЦИАЛЬНЫЕ имена сборочных директорий Nuitka
possible_temp_dirs = [
    # os.path.join(output_dir, f"{main_script_basename}.build"),
    # os.path.join(output_dir, f"{main_script_basename}.onefile-build"),
]

# Определяем полное имя выходного файла с расширением для текущей ОС
if sys.platform == "win32":
    output_filename = f"{output_filename_base}.exe"
elif sys.platform == "darwin":
    output_filename = output_filename_base
else: # Linux и другие
    output_filename = output_filename_base

# Формируем команду Nuitka
command = [
    sys.executable,  # Используем тот же python, что и для запуска скрипта
    "-m",
    "nuitka",
    f"--output-dir={output_dir}",
    f"--output-filename={output_filename}", # Указываем имя выходного файла
]

if use_onefile:
    command.append("--onefile")

# Добавляем дополнительные опции
command.extend(extra_nuitka_options)

# Добавляем главный скрипт в конец команды
command.append(main_script)

print("Запуск Nuitka со следующей командой:")
print(" ".join(command))
print("-" * 30)

# Запускаем сборку с Popen для потокового вывода
try:
    # --- Очистка выходной директории перед сборкой ---
    if os.path.exists(output_dir):
        print(f"Очистка существующей директории: {output_dir}")
        try:
            shutil.rmtree(output_dir)
            print("Директория успешно очищена.")
        except OSError as e:
            print(f"Ошибка при очистке директории {output_dir}: {e}")
            # Решаем, прерывать ли сборку, если очистка не удалась.
            # В данном случае, продолжим, т.к. makedirs может сработать.
    # ------------------------------------------------

    # Убедимся, что директория существует (или создаем ее после очистки)
    os.makedirs(output_dir, exist_ok=True)

    # Используем Popen и перенаправляем stderr в stdout для единого потока
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', bufsize=1)

    print("--- Вывод Nuitka --- ")
    # Читаем вывод построчно в реальном времени
    if process.stdout:
      for line in iter(process.stdout.readline, ''):
          # Выводим каждую строку немедленно
          sys.stdout.write(line)
          sys.stdout.flush()
      process.stdout.close()

    # Ждем завершения процесса и получаем код возврата
    return_code = process.wait()
    print("-" * 30)

    if return_code == 0:
        print(f"Сборка успешно завершена! Исполняемый файл: {os.path.join(output_dir, output_filename)}")

        # --- Удаление ВСЕХ известных сборочных директорий --- 
        print("Попытка удаления временных сборочных директорий...")
        for temp_dir_path in possible_temp_dirs:
            if os.path.exists(temp_dir_path):
                print(f"Найден и удаляется: {temp_dir_path}")
                try:
                    shutil.rmtree(temp_dir_path)
                    print(f"Успешно удалено: {temp_dir_path}")
                except OSError as e:
                    print(f"Ошибка при удалении {temp_dir_path}: {e}")
            # else:
                # Можно раскомментировать для отладки:
                # print(f"Директория не найдена: {temp_dir_path}")
        print("Очистка временных директорий завершена.")
        # --------------------------------------------------
    else:
        print(f"Ошибка во время сборки Nuitka (код возврата {return_code})")
        sys.exit(return_code) # Выходим с кодом ошибки Nuitka

except FileNotFoundError:
     print(f"Ошибка: Не удалось найти '{sys.executable} -m nuitka'. Убедитесь, что Nuitka установлена в вашем окружении.")
     sys.exit(1)
except Exception as e:
    print(f"Произошла непредвиденная ошибка: {e}")
    sys.exit(1) 
