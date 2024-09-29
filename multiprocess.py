import os
import time
import re
import logging
from collections import defaultdict
from multiprocessing import Process, Lock, Manager

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_keywords_in_files(files, keywords, result_dict, lock):
    """
    Паралельно шукає ключові слова в кожному файлі зі списку файлів.

    Аргументи:
    files (list): Список шляхів до файлів.
    keywords (list): Список ключових слів для пошуку.
    result_dict (DictProxy): Словник для збереження результатів.
    lock (Lock): Лок для забезпечення потокобезпеки при оновленні результатів.
    """
    for file_path in files:
        try:
            with open(file_path, "r") as fh:
                text = fh.read()
            logging.info(f"Обробляємо файл: {file_path}")
            with lock:  # Providing safe work with dictionary
                for keyword in keywords:
                    result = re.search(keyword, text, re.IGNORECASE)
                    if result:
                        result_dict[keyword].append(file_path)
        except FileNotFoundError:
            logging.error(f"Файл не знайдено: {file_path}")
        except Exception as e:
            logging.error(f"Помилка при обробці файлу {file_path}: {str(e)}")


def get_files_list(dir, extension='.txt'):
    """
    Отримує список файлів із заданої директорії з відповідним розширенням.

    Аргументи:
    dir (str): Шлях до директорії.
    extension (str, optional): Розширення файлів для вибірки. За замовчуванням '.txt'.

    Повертає:
    list: Список шляхів до файлів із вказаним розширенням.
    """
    try:
        files = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith(extension)]
        logging.info(f"Знайдено {len(files)} файлів у директорії {dir}")
        return files
    except FileNotFoundError:
        logging.error(f"Директорія не знайдена: {dir}")
        return []
    except Exception as e:
        logging.error(f"Помилка при читанні директорії {dir}: {str(e)}")
        return []


def processes_search(files, keywords, num_process):
    """
    Виконує паралельний пошук ключових слів у файлах за допомогою процесів.

    Аргументи:
    files (list): Список файлів для пошуку.
    keywords (list): Список ключових слів для пошуку.
    num_process (int): Кількість процесів для обробки файлів.

    Повертає:
    DictProxy: Словник з результатами пошуку.
    """
    start_time = time.time()
    
    chunk_size = len(files) // num_process
    processes = []
    results = defaultdict(list)

    with Manager() as manager:
        result_dict = manager.dict({word: manager.list([]) for word in keywords})
        lock = Lock()

        for i in range(num_process):
            start_index = i * chunk_size
            end_index = (i + 1) * chunk_size if i != num_process - 1 else len(files)
            proc_files = files[start_index:end_index]
            proc = Process(target=search_keywords_in_files, args=(proc_files, keywords, result_dict, lock))
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        for key, value in result_dict.items():
            results[key] = list(value)

    logging.info(f"Час виконання: {time.time() - start_time} секунд")
    
    return dict(results)


if __name__ == "__main__":
    dir = "./my_files"  
    keywords = ["kitchen", "career", "subject", "miss"]

    files = get_files_list(dir)

    if files:
        results = processes_search(files, keywords, num_process=4)
        
        print("-" * 80)
        print("multiprocessing")
        for key, value in results.items():
            print(f"{key}: {list(value)}")
        print("-" * 80)
            
    else:
        logging.info("Файли не знайдено для обробки.")