import random

def zalgo_text(text):
    # Combining diacritical marks to overlay on characters
    zalgo_chars = [
        '\u0300', '\u0301', '\u0302', '\u0303', '\u0304',
        '\u0305', '\u0306', '\u0307', '\u0308', '\u0309',
        '\u030A', '\u030B', '\u030C', '\u030D', '\u030E',
        '\u030F', '\u0310', '\u0311', '\u0312', '\u0313',
        '\u0314', '\u0315'
    ]

    corrupted_text = ""
    for char in text:
        corrupted_text += char
        if char != " ":
            for _ in range(random.randint(0, 3)):  # Number of diacritical marks added to each char
                corrupted_text += random.choice(zalgo_chars)

    return corrupted_text
