def insert(string: str, **kwargs) -> str:
    step1 = string.replace("{", "\u2345").replace("}", "\u5432")
    step2 = step1.replace("\u1234", "{").replace("\u4321", "}")
    step3 = step2.format(**kwargs)
    final = step3.replace("\u2345", "{").replace("\u5432", "}")
    return final
