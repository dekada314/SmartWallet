import re

import pymorphy3


class TextProcessing:
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()

    def main_noun_searcher(self, text: str) -> list[str]:
        """
        Получает на вход строку, выдает список только существительных в их нормальной форме
        """
        output = []
        for word in text.split():
            parsed_word = self.morph.parse(word)[0]
            if parsed_word.tag.POS == "NOUN":
                output.append(parsed_word.normal_form)

        return output

    def number_searcher(self, text: str) -> float:
        number = re.search(r"\d+", text)
        return float(number.group())
