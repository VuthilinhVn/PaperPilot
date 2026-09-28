"""
Đọc trực tiếp file CSV dataset arXiv (Kaggle) và insert vào MySQL
bảng `papers` của project papers_app.

Cột CSV dùng tới (các cột khác trong file sẽ được bỏ qua):
    paper_id, title, abstract, first_author, primary_category,
    submitted_date, arxiv_url, pdf_url

Chạy sau khi đã:
1. Chạy semanticscholar_migration.sql (tạo DB papers_app + toàn bộ bảng)
2. Tải file CSV dataset arXiv về, đổi tên/đường dẫn ở CSV_FILE bên dưới

Cần cài: pip install pymysql
"""

import csv
import pymysql

# ============================================
# Cấu hình kết nối DB - SỬA LẠI cho đúng máy bạn
# ============================================
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",  # <-- đổi thành mật khẩu MySQL thật của bạn
    "database": "papers_app",
    "charset": "utf8mb4",
}

CSV_FILE = "arxiv_ai_ml_papers.csv"

ALLOWED_CATEGORIES = {
    "cs.CV": "Computer Vision",
    "cs.LG": "Machine Learning",
    "cs.CL": "Computation and Language (NLP)",
    "cs.AI": "Artificial Intelligence",
    "cs.RO": "Robotics",
    "cs.IR": "Information Retrieval",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.SE": "Software Engineering",
    "cs.HC": "Human-Computer Interaction",
    "cs.MM": "Multimedia",
    "cs.CR": "Cryptography and Security",
    "cs.GR": "Graphics",
    "eess.IV": "Image and Video Processing",
    "eess.SP": "Signal Processing",
    "stat.ML": "Machine Learning (Statistics)",
}


def get_or_create_category_id(cursor, category_map: dict, category_name: str) -> int:
    """Trả về category_id, tự tạo mới trong DB nếu category_name chưa từng thấy.

    arXiv có hàng trăm primary_category (cs.CV, cs.LG, cs.CL, ...) nên không seed sẵn
    trong file .sql, mà tự động thêm khi gặp trong lúc import.
    """
    if category_name in category_map:
        return category_map[category_name]

    cursor.execute(
        "INSERT IGNORE INTO paper_primary_category (name) VALUES (%s)",
        (category_name,),
    )
    cursor.execute(
        "SELECT id FROM paper_primary_category WHERE name = %s",
        (category_name,),
    )
    category_id = cursor.fetchone()[0]
    category_map[category_name] = category_id
    return category_id


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    category_map: dict = {}
    inserted, skipped = 0, 0

    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("title") or "").strip()
            abstract = (row.get("abstract") or "").strip()
            if not title or not abstract:
                skipped += 1
                continue

            category_code = row.get("primary_category") or ""
            if category_code not in ALLOWED_CATEGORIES:
                # Bỏ qua các paper thuộc category ngoài danh sách quan tâm
                # (arXiv có ~100 category, chỉ giữ lại các category AI/ML/CS liên quan)
                skipped += 1
                continue

            category_name = ALLOWED_CATEGORIES[category_code]
            category_id = get_or_create_category_id(cursor, category_map, category_name)

            sql = """
                INSERT IGNORE INTO papers
                    (paper_id, title, abstract, pdf_url, arxiv_url, first_author,
                     category_id, submitted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            # INSERT IGNORE: nếu paper_id đã tồn tại (chạy script 2 lần), bỏ qua thay vì lỗi trùng key
            values = (
                row.get("paper_id") or None,
                title,
                abstract,
                row.get("pdf_url") or None,
                row.get("arxiv_url") or None,
                row.get("first_author") or None,
                category_id,
                row.get("submitted_date") or None,
            )

            try:
                cursor.execute(sql, values)
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1  # đã tồn tại (paper_id trùng)
            except pymysql.err.IntegrityError as e:
                print(f"  [!] Lỗi insert '{title[:40]}...': {e}")
                skipped += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Đã tạo/dùng {len(category_map)} category: {list(category_map.keys())[:10]}"
          f"{' ...' if len(category_map) > 10 else ''}")
    print(f"Xong. Insert thành công: {inserted} bài. Bỏ qua/trùng: {skipped} bài.")


if __name__ == "__main__":
    main()
