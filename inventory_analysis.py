import csv
from pathlib import Path
import re

DATA_FILE = Path(__file__).parent / "inventory_data.csv"


def parse_int(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    normalized = text.lower()
    if normalized in {"out of stock", "out-of-stock", "none", "n/a", "na"}:
        return 0
    # Remove commas and dollar signs
    cleaned = re.sub(r"[,$]", "", text)
    # Try integer parse first
    try:
        return int(float(cleaned))
    except ValueError:
        match = re.search(r"(-?\d+)", cleaned)
        if match:
            return int(match.group(1))
    return None


def load_inventory(csv_path):
    with csv_path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stock_raw = str(row.get("stock_level", "")).strip()
            threshold_raw = str(row.get("reorder_threshold", "")).strip()
            yield {
                "product_id": row.get("product_id", "").strip(),
                "category": row.get("category", "").strip(),
                "stock_level": parse_int(stock_raw),
                "stock_display": stock_raw or "",
                "reorder_threshold": parse_int(threshold_raw),
                "threshold_display": threshold_raw or "",
                "unit_price": str(row.get("unit_price", "")).strip(),
            }


def find_reorder_items(items):
    for item in items:
        stock = item["stock_level"]
        threshold = item["reorder_threshold"]
        if stock is None or threshold is None:
            continue
        if stock < threshold:
            yield item


def print_table(rows):
    headers = ["product_id", "category", "stock_level", "reorder_threshold", "unit_price"]
    values = [headers]
    for item in rows:
        values.append([
            item["product_id"],
            item["category"],
            item["stock_display"],
            item["threshold_display"],
            item["unit_price"],
        ])

    widths = [max(len(str(value[i])) for value in values) for i in range(len(headers))]
    header_row = " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
    separator = "-+-".join("-" * widths[i] for i in range(len(headers)))

    print(header_row)
    print(separator)
    for row in values[1:]:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Inventory file not found: {DATA_FILE}")

    reorder_items = list(find_reorder_items(load_inventory(DATA_FILE)))

    print("Items needing reorder:")
    if not reorder_items:
        print("No items currently need reordering.")
        return

    print_table(reorder_items)


if __name__ == "__main__":
    main()
