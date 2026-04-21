import re

import pymorphy3


class TextProcessing:
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()

    def main_noun_searcher(self, text: str) -> list[str]:
        output = []
        for word in text.split():
            parsed_word = self.morph.parse(word)[0]
            if parsed_word.tag.POS == "NOUN":
                output.append(parsed_word.normal_form)

        return output

    def extract_amount(self, input_text: str) -> float:
        input_text = input_text.lower()
        
        number_pattern = r"(\d+[.,]?\d*)"
        patterns = [
            rf"{number_pattern}\s*(?:р|руб|byn|\$)?",
            rf"(?:за|стоимость|цена)\s+{number_pattern}",
            number_pattern
        ]
        for pattern in patterns:
            match = re.search(pattern=pattern, text=input_text)
            if match:
                return float(match.group(1).replace(",", "."))
            
        return None
