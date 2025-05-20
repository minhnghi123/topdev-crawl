import json
import re
from datetime import datetime, timedelta

def parse_relative_time(text, now=None):
    if now is None:
        now = datetime.now()
    text = str(text).strip()
    match = re.match(r"(\d+)\s+(giờ|ngày|tuần)\s+(trước|tới)", text)
    if not match:
        return text  # Giữ nguyên nếu không đúng định dạng
    value, unit, direction = match.groups()
    value = int(value)
    if unit == "giờ":
        delta = timedelta(hours=value)
    elif unit == "ngày":
        delta = timedelta(days=value)
    elif unit == "tuần":
        delta = timedelta(weeks=value)
    else:
        return text
    if direction == "trước":
        dt = now - delta
    else:  # "tới"
        dt = now + delta
    return dt.isoformat(sep=" ", timespec="seconds")

# Đọc file JSON
input = r"Data/job/job_links_full_2.json"
with open(input, "r", encoding="utf-8") as f:
    job_links = json.load(f)

now = datetime.now()
for job in job_links:
    if "posted_time" in job:
        job["posted_time"] = parse_relative_time(job["posted_time"], now)
    if "expired_time" in job:
        job["expired_time"] = parse_relative_time(job["expired_time"], now)

# Ghi đè lại file JSON với dữ liệu đã chuyển đổi
with open(input, "w", encoding="utf-8") as f:
    json.dump(job_links, f, ensure_ascii=False, indent=4)