import re

import pdfplumber
import pytesseract
from PIL import Image


class ReceiptParser:
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base

    def parse_file(self, file_path: str):
        """Основной метод: принимает путь к файлу, извлекает текст и парсит его"""
        text = ""
        extension = file_path.split('.')[-1].lower()

        try:
            if extension == 'pdf':
                text = self._extract_text_from_pdf(file_path)
            elif extension in ['jpg', 'jpeg', 'png', 'bmp']:
                text = self._extract_text_from_image(file_path)
            else:
                print(f"❌ Формат {extension} не поддерживается")
                return None
            
            if not text:
                return None
                
            return self.detect_bank_and_parse(text)
        except Exception as e:
            print(f"❌ Ошибка при обработке файла: {e}")
            return None

    def _extract_text_from_pdf(self, file_path):
        """Извлечение текста из PDF-файла"""
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        return full_text

    def _extract_text_from_image(self, file_path):
        """Извлечение текста из картинки (OCR)"""
        # Если ты на Windows, раскомментируй строку ниже и укажи путь к tesseract.exe
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        image = Image.open(file_path)
        return pytesseract.image_to_string(image, lang='rus+eng')

    def parse_alfa(self, text: str) -> dict:
        """Парсинг специфического формата Альфа-Банка"""
        result = {
            "bank": "Alfa-Bank",
            "merchant": None,
            "amount": 0.0,
            "date": None,
            "category": "unknown"
        }

        # Очистка текста от лишних кавычек и переносов, которые бывают в PDF
        clean_text = text.replace('"', '').replace('\r', '')

        # 1. Поиск суммы
        amount_match = re.search(r"Сумма\s*(\d+[.,]\d{2})\s*BYN", clean_text)
        if not amount_match: # Запасной вариант
            amount_match = re.search(r"(\d+[.,]\d{2})\s*BYN", clean_text)
            
        if amount_match:
            result["amount"] = float(amount_match.group(1).replace(',', '.'))

        # 2. Поиск магазина (после 'Наименование получателя')
        merchant_match = re.search(r"Наименование получателя\s*(.*)", clean_text)
        if merchant_match:
            result["merchant"] = merchant_match.group(1).strip()
            result["category"] = self._get_category(result["merchant"])

        # 3. Поиск даты
        date_match = re.search(r"(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})", clean_text)
        if date_match:
            result["date"] = date_match.group(1)

        return result

    def _get_category(self, merchant_name: str) -> str:
        if not self.kb:
            return "unknown"
        
        name_upper = merchant_name.upper()
        for cat_id, data in self.kb.get_lexicon().items(): 
            if any(key.upper() in name_upper for key in data.get('keywords', [])):
                return cat_id
        return "unknown"

    def detect_bank_and_parse(self, text: str):
        if "Альфа" in text or "ALFA" in text.upper():
            return self.parse_alfa(text)
        return {"error": "Bank not recognized", "raw_text": text[:100]}