import threading
import os
import time
import re
import logging
from collections import defaultdict

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_keywords_in_files(files, keywords, result_dict, lock):
    """
    Паралельно шукає ключові слова в кожному файлі зі списку файлів.

    Аргументи:
    files (list): Список шляхів до файлів.
    keywords (list): Список ключових слів для пошуку.
    result_dict (defaultdict): Словник для збереження результатів.
    lock (threading.Lock): Лок для забезпечення потокобезпеки при оновленні результатів.
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


def threads_search(files, keywords, num_threads):
    """
    Виконує паралельний пошук ключових слів у файлах за допомогою потоків.

    Аргументи:
    files (list): Список файлів для пошуку.
    keywords (list): Список ключових слів для пошуку.
    num_threads (int): Кількість потоків для обробки файлів.

    Повертає:
    defaultdict: Словник з результатами пошуку.
    """
    start_time = time.time()
    
    chunk_size = len(files) // num_threads
    threads = []
    result_dict = defaultdict(list)
    lock = threading.Lock()

    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size if i != num_threads - 1 else len(files)
        thread_files = files[start_index:end_index]
        thread = threading.Thread(target=search_keywords_in_files, args=(thread_files, keywords, result_dict, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logging.info(f"Час виконання: {time.time() - start_time} секунд")
    
    return result_dict


if __name__ == "__main__":
    dir = "./my_files"  
    keywords = ["kitchen", "career", "subject", "miss"]

    files = get_files_list(dir)

    if files:
        results = threads_search(files, keywords, num_threads=4)
        
        print("-" * 80)
        print("multithreading")
        for key, value in results.items():
            print(f"{key}: {value}")
        print("-" * 80)
            
    else:
        logging.info("Файли не знайдено для обробки.")