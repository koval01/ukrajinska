import re

class Ukrajinska:
    def __init__(self):
        self.cyr_consonants = set("бвгґджзклмнпрстфхцчшщ")

        self.fwd_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'ğ', 'ґ': 'g',
            'д': 'd', 'е': 'e', 'є': 'je', 'ж': 'ž', 'з': 'z',
            'и': 'y', 'і': 'i', 'ї': 'ï', 'й': 'j', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
            'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
            'х': 'x', 'ц': 'c', 'ч': 'č', 'ш': 'š', 'щ': 'ŝ',
            'ь': 'j', 'ю': 'ju', 'я': 'ja', "'": "'"
        }

        self.bwd_direct = {
            "je": "є", "ju": "ю", "ja": "я", "ȷ": "ь",
            "a": "а", "b": "б", "c": "ц", "č": "ч", "d": "д", "e": "е", "f": "ф",
            "g": "ґ", "ğ": "г", "i": "і", "ï": "ї", "k": "к", "l": "л", "m": "м",
            "n": "н", "o": "о", "p": "п", "r": "р", "s": "с", "š": "ш", "ŝ": "щ",
            "t": "т", "u": "у", "v": "в", "x": "х", "y": "и", "z": "з", "ž": "ж", "'": "'"
        }

        self.bwd_prime = {
            k + "'": v for k, v in self.bwd_direct.items() if v in self.cyr_consonants
        }

        self.tokens = sorted(
            list(self.bwd_prime.keys()) +
            list(self.bwd_direct.keys()) + ["j'", "j"],
            key=len, reverse=True
        )

    @staticmethod
    def _apply_case_fwd(source_char: str, target_str: str, prev_char: str, next_char: str) -> str:
        if not target_str:
            return ""
        if source_char.isupper():
            if prev_char.isupper() or next_char.isupper():
                return target_str.upper()
            return target_str.capitalize()
        return target_str.lower()

    @staticmethod
    def _apply_case_bwd(source_slice: str, target_str: str) -> str:
        if not target_str:
            return ""
        if source_slice.isupper():
            return target_str.upper()
        if source_slice.istitle() or (len(source_slice) == 1 and source_slice.isupper()):
            return target_str.capitalize()
        return target_str.lower()

    def to_latin(self, text: str) -> str:
        result = []
        n = len(text)

        for i in range(n):
            char = text[i]
            lower_char = char.lower()

            if lower_char not in self.fwd_map:
                result.append(char)
                continue

            lat = self.fwd_map[lower_char]
            prev_char = text[i-1] if i-1 >= 0 else " "
            next_char = text[i+1] if i+1 < n else " "

            if lower_char in self.cyr_consonants and next_char.lower() == 'й':
                lat += "'"
            elif lower_char == 'й' and next_char.lower() in ['а', 'е', 'у']:
                lat = "j'"
            elif lower_char == 'ь':
                if next_char.lower() in ['а', 'е', 'у']:
                    lat = "j'"
                elif not prev_char.isalpha() and not next_char.isalpha():
                    lat = "ȷ"

            result.append(self._apply_case_fwd(char, lat, prev_char, next_char))

        return "".join(result)

    def _word_to_cyrillic(self, text: str) -> str:
        result = []
        i = 0
        n = len(text)
        prev_base_cons = False

        while i < n:
            matched = False
            for token in self.tokens:
                tok_len = len(token)
                if i + tok_len > n:
                    continue

                source_slice = text[i:i+tok_len]

                if source_slice.lower() == token:
                    remainder = text[i+tok_len:].lower()
                    cyr_target = None
                    is_base_cons = False

                    if token in self.bwd_prime:
                        is_before_j = remainder.startswith("j'") or (
                            remainder.startswith("j") and not re.match(r'^j[aeu]', remainder)
                        )
                        if is_before_j:
                            cyr_target = self.bwd_prime[token]
                            is_base_cons = False
                        else:
                            continue

                    elif token in ["j", "j'"]:
                        cyr_target = "ь" if prev_base_cons else "й"
                    else:
                        cyr_target = self.bwd_direct[token]
                        is_base_cons = cyr_target in self.cyr_consonants

                    if cyr_target:
                        result.append(self._apply_case_bwd(source_slice, cyr_target))
                        prev_base_cons = is_base_cons
                        i += tok_len
                        matched = True
                        break

            if not matched:
                result.append(text[i])
                prev_base_cons = False
                i += 1

        return "".join(result)

    def to_cyrillic(self, text: str) -> str:
        tokens = re.split(r"([A-Za-zğïčšŝžȷĞÏČŠŜŽ']+)", text)
        result = []

        for token in tokens:
            if not token:
                continue
            if re.match(r"^[A-Za-zğïčšŝžȷĞÏČŠŜŽ']+$", token):
                if re.search(r'[qwhQWH]', token):
                    result.append(token)
                else:
                    result.append(self._word_to_cyrillic(token))
            else:
                result.append(token)

        return "".join(result)
