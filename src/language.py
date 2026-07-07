import json
import os
import random

class LanguageSystem:
    def __init__(self):
        self.dictionary = {}
        self.load_dictionary()

    def load_dictionary(self):
        """Загружает словарь из JSON файла."""
        file_path = os.path.join("assets", "data", "dictionary.json")
        try:
            # Важно использовать utf-8 для корректного чтения кириллицы
            with open(file_path, 'r', encoding='utf-8') as f:
                self.dictionary = json.load(f)
            print(f"LanguageSystem: Успешно загружено {len(self.dictionary)} категорий слов.")
        except FileNotFoundError:
            print(f"LanguageSystem Error: Файл {file_path} не найден.")
        except json.JSONDecodeError:
            print(f"LanguageSystem Error: Ошибка синтаксиса в файле {file_path}.")
        except Exception as e:
            print(f"LanguageSystem Error: {e}")

    def get_word(self, category):
        """Возвращает случайное слово из указанной категории."""
        if category in self.dictionary and self.dictionary[category]:
            return random.choice(self.dictionary[category])
        return f"[{category} not found]"

    def generate_thought(self):
        """Генерирует случайную мысль, комбинируя слова."""
        # Для начала просто возвращаем готовую фразу или простую комбинацию
        templates = [
            lambda: self.get_word("phrases"),
            lambda: f"{self.get_word('greetings')} Я {self.get_word('emotions')}.",
            lambda: f"Этот {self.get_word('nouns')} отлично {self.get_word('verbs')}."
        ]

        chosen_template = random.choice(templates)
        return chosen_template()
