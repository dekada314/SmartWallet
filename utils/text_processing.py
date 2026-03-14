import re

import pymorphy3

morph = pymorphy3.MorphAnalyzer()

def noun_searcher(text: str) -> list[str]:
    """
    Получает на вход строку, выдает список только существительных в их нормальной форме
    """
    output = []
    for word in text.split():
        parsed_word = morph.parse(word)[0]
        if parsed_word.tag.POS == 'NOUN':
            output.append(parsed_word.normal_form)
            
    return output

def number_searcher(text: str) -> float:
    """
    Ищет число в строке и возвращает его
    """
    number = re.search(r'\d+', text)
    return float(number.group())
    
    
if __name__ == '__main__':
    parsed = morph.parse('коффе')
    for p in parsed:
        print(p)