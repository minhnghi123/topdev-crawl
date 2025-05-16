import json

# Đường dẫn file job_data.json
job_data_file = "job_data.json"
job_links_file = "job_links.json"

# Đọc dữ liệu từ job_data.json
with open(job_data_file, "r", encoding="utf-8") as f:
    job_data = json.load(f)

# Tách các link từ job_data
all_links = set()  # Sử dụng set để loại bỏ trùng lặp
for job in job_data:
    links = job.get("links", [])
    all_links.update(links)  # Thêm các link vào set

# Chuyển set thành danh sách và lưu vào file job_links.json
with open(job_links_file, "w", encoding="utf-8") as f:
    json.dump(list(all_links), f, ensure_ascii=False, indent=4)

print(f"Đã tách {len(all_links)} link và lưu vào file {job_links_file}.")