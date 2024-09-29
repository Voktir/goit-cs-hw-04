import os
import random
from faker import Faker

def create_files_with_faker(directory, num_files, min_words=10, max_words=20):
  """
  Створює задану кількість текстових файлів у вказаній директорії з випадковими словами, згенерованими за допомогою Faker.

  Args:
    directory: Шлях до директорії, де будуть створені файли.
    num_files: Кількість файлів для створення.
    min_words: Мінімальна кількість слів у файлі.
    max_words: Максимальна кількість слів у файлі.
  """

  # Створення директорії, якщо її ще не існує
  os.makedirs(directory, exist_ok=True)

  fake = Faker()

  # Створення файлів
  for i in range(num_files):
    filename = f"file_{i+1}.txt"
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
      for _ in range(random.randint(min_words, max_words)):
        f.write(fake.word() + ' ')

if __name__ == "__main__":
  
  create_files_with_faker(directory = "my_files", num_files  = 10, min_words  = 10, max_words  = 20)
