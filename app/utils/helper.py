def kannada_to_english_digits(text: str) -> str:
    kn_to_en = str.maketrans("೦೧೨೩೪೫೬೭೮೯", "0123456789")
    return text.translate(kn_to_en)
