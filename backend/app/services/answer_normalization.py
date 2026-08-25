def normalize_answer(answer:str) -> str:
    return " ".join(
        answer.casefold().split(),
    )