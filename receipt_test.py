import yaml
import os
from services.receipt_parser import ReceiptParser

def run_final_test():
    # 1. Загружаем твою Базу Знаний (убедись, что файл лежит рядом)
    #
    try:
        with open('knowledge_base/knowledge_base.yml', 'r', encoding='utf-8') as f:
            kb_data = yaml.safe_load(f)
        print("✅ База знаний (YAML) загружена.")
    except FileNotFoundError:
        print("❌ Ошибка: Файл knowledge_base.yml не найден!")
        return

    # 2. Инициализируем парсер с твоей БЗ
    parser = ReceiptParser(knowledge_base=kb_data)

    # 3. Укажи путь к твоему PDF файлу (тот, что ты скидывала)
    #
    file_path = "receipts/markformel.pdf" 


    if not os.path.exists(file_path):
        print(f"⚠️ Файл {file_path} не найден в папке. Проверь название!")
        return

    print(f"🔍 Начинаю обработку файла: {file_path}...")

    # 4. Вызываем метод, который сам поймет, что это PDF, и извлечет данные
    result = parser.parse_file(file_path)

    # 5. Вывод результатов
    print("\n" + "="*30)
    if result and "error" not in result:
        print(f"🏦 Банк: {result.get('bank')}")
        print(f"🛒 Торговая точка: {result.get('merchant')}")
        print(f"💰 Сумма: {result.get('amount')} BYN")
        print(f"📅 Дата: {result.get('date')}")
        
        # Проверка классификации по твоей БЗ
        category = result.get('category')
        print(f"🏷 Категория (из БЗ): {category}")
        
        if category == 'food':
            print("\n🌟 РЕЗУЛЬТАТ: Система успешно узнала 'EVROOPT' как категорию 'Еда'!")
        else:
            print(f"\n💡 Подсказка: Проверь, есть ли слово '{result.get('merchant')}' в твоем YAML в разделе 'food'.")
    else:
        print("❌ Не удалось распарсить чек. Проверь формат текста в PDF.")
    print("="*30)

if __name__ == "__main__":
    run_final_test()