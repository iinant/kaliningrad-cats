# -*- coding: utf-8 -*-
"""Генерирует data.js из data_source.csv (выгрузка Google Sheets)."""
import csv, json, re, io, sys

OUT = "data.js"

def clean_price(s):
    if not s:
        return None
    digits = re.sub(r"[^\d]", "", s.replace("\xa0", " "))
    if not digits:
        return None
    p = int(digits)
    return p if 300 <= p <= 100000 else None

def clean_rating(s):
    if not s:
        return None
    m = re.match(r"\s*(\d),(\d)\s*$", s.replace("\xa0", " "))
    if m:
        return float(m.group(1) + "." + m.group(2))
    if s.strip() == "5":
        return 5.0
    return None

def main():
    with open("data_source.csv", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    items = []
    for r in rows[1:]:
        r += [""] * (23 - len(r))
        price = clean_price(r[10])
        images = [u.strip() for u in r[1:6] if u.strip().startswith("http")]
        title = r[7].strip()
        if not price or not images or not title:
            continue
        items.append({
            "title": title,
            "address": r[13].strip(),
            "price": price,
            "rating": clean_rating(r[8]),
            "reviews": re.sub(r"[^\d]", "", r[9]) or None,
            "images": images,
            "link": r[0].strip(),
        })

    # минимум 4 фото у лота, сортировка по цене, убираем дубли по ссылке
    seen, uniq = set(), []
    for it in sorted(items, key=lambda x: x["price"]):
        if it["link"] in seen or len(it["images"]) < 4:
            continue
        seen.add(it["link"])
        uniq.append(it)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// Сгенерировано gen_data.py из таблицы объявлений Авито (Калининград)\n")
        f.write("window.GAME_DATA = ")
        json.dump(uniq, f, ensure_ascii=False)
        f.write(";\n")

    print("OK:", len(uniq), "lots; prices:", [it["price"] for it in uniq])

if __name__ == "__main__":
    main()
