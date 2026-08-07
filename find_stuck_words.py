import json
import re

with open('chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

# Regex to match words that contain at least one Vietnamese diacritic
# and are longer than 7 characters, which are likely stuck words if they only contain letters
vn_chars = "áàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
vn_chars_upper = vn_chars.upper()
all_vn_chars = vn_chars + vn_chars_upper

pattern = re.compile(r'[A-Za-z' + all_vn_chars + r']+')

stuck_words = set()
for chunk in chunks:
    if not chunk['source'].startswith("Chuong"):
        continue
    text = chunk['text']
    words = pattern.findall(text)
    for w in words:
        # Check if it has a vietnamese character
        has_vn = any(c in all_vn_chars for c in w)
        if has_vn:
            # Let's count potential syllables by checking vowels? 
            # Or just check if length > 7 (since max single vn syllable is 7 like 'nghiêng')
            # Wait, what if it's like 'dữliệu' (6 chars) -> 'dữ' + 'liệu'
            # Let's just find any word that has 2 or more uppercase letters inside, or is in a known bad list
            # Actually, to find 'dữliệu', we can check if it contains multiple vowels separated by consonants.
            pass

        # Better: just use a list of common stuck words I can find by inspecting all words with vn chars
        if has_vn and len(w) >= 6:
            stuck_words.add(w.lower())

for w in sorted(list(stuck_words)):
    print(w)
