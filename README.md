# World Cup 2026 AI Predictor Bot 🏆🤖

Bot Telegram dự đoán tỉ số World Cup 2026 bằng mô hình Machine Learning (Random Forest) và lấy lịch thi đấu thực tế từ API.

## 🚀 Tính Năng Nổi Bật
- **`/start`**: Khởi động Bot.
- **`/live`**: Xem tỷ số trực tiếp và đội hình ra sân của các trận đấu đang diễn ra.
- **`/schedule`**: Lấy lịch thi đấu World Cup thực tế từ API (Football-Data.org) với định dạng giờ Việt Nam và thông tin sân vận động.
- **`/predict [Đội 1] vs [Đội 2]`**: Dự báo tỷ lệ thắng/hòa/thua giữa 2 đội bất kỳ bằng AI.
- **`/history`**: Xem lại lịch sử các trận đấu bạn đã dự đoán.
- **`/stats`**: Bảng xếp hạng các đội bóng được cộng đồng vote nhiều nhất.
- **`/help`**: Xem hướng dẫn sử dụng chi tiết.

## 🛠️ Công Nghệ Sử Dụng
- **Python 3.13** (FastAPI, Aiogram 3)
- **Scikit-Learn & Joblib** (Mô hình AI Random Forest)
- **MongoDB** (Lưu trữ lịch sử dự đoán)
- **Redis** (Caching)
- **Docker & Docker Compose** (Triển khai tự động)

## 📦 Hướng Dẫn Triển Khai (Deploy Lên VPS)

> [!CAUTION]
> **CẢNH BÁO BẢO MẬT:** Tuyệt đối không bao giờ Commit file `.env` lên GitHub (hoặc bất kỳ nơi nào public). File `.env` chứa `BOT_TOKEN` và `API_KEY` của bạn. Mặc dù file `.env` đã được liệt kê trong `.gitignore` để ngăn chặn đẩy nhầm lên Git, nhưng bạn vẫn phải luôn cẩn thận.

1. Cài đặt **Docker** và **Docker Compose** trên Server của bạn.
2. Clone toàn bộ thư mục mã nguồn này lên Server.
3. Chỉnh sửa file `.env` (bạn cần có Token của Telegram và API Key của Football-Data):
   ```env
   BOT_TOKEN=your_telegram_bot_token
   API_KEY=your_football_data_api_key
   ```
4. Mở Terminal tại thư mục gốc của dự án và chạy lệnh:
   ```bash
   docker-compose up -d --build
   ```
   Hệ thống sẽ tự động tải MongoDB, Redis và khởi chạy Bot (chạy ngầm).

## 🎛️ Các Lệnh Quản Lý Bằng Docker
- **Bật Bot:** `docker-compose up -d`
- **Tắt Bot (Không mất dữ liệu):** `docker-compose down`
- **Khởi động lại & Cập nhật code mới:** `docker-compose up -d --build`
- **Xem trạng thái các máy ảo đang chạy:** `docker ps`
- **Xem Nhật ký tin nhắn (Logs) của Bot:** `docker-compose logs -f bot` (Bấm Ctrl+C để thoát)

## 🤖 Kiến Trúc Hệ Thống & Trí Tuệ Nhân Tạo (AI)

### Vai trò của FastAPI
Dự án này sử dụng FastAPI nhưng **KHÔNG PHẢI để hứng Telegram Webhook**. FastAPI đóng vai trò:
1. **Background Task Manager:** Quản lý vòng lặp kết nối (Long-Polling) của Aiogram chạy ngầm thông qua sự kiện khởi động `lifespan`.
2. **REST API / Healthcheck:** Cung cấp endpoint `/health` nội bộ để Docker tự động `curl` kiểm tra định kỳ xem Bot có bị treo hay không (Tính năng Docker Healthcheck).

### Khả năng của Mô Hình Machine Learning
- **Nguồn dữ liệu (Dataset):** Huấn luyện trên lịch sử hàng ngàn trận đấu bóng đá quốc tế.
- **Thuật toán:** Mạng rừng ngẫu nhiên (Random Forest Classifier).
- **Độ chính xác (Accuracy thực tế):** Giao động ở mức **`55% - 65%`**. Với một môn thể thao nặng tính bất ngờ như bóng đá thì đây là mức độ tin cậy khá tốt.

## 💡 Lưu Ý Về Tài Nguyên (RAM / CPU)
- Dự án này bao gồm cả một mô hình Machine Learning được load thẳng vào RAM, cộng thêm 2 Database (MongoDB và Redis). 
- Khuyến nghị VPS nên có tối thiểu **1GB - 2GB RAM**.
- Nếu bạn đang chạy các node blockchain hoặc các dự án ngốn phần cứng khác trên cùng server, hãy cân nhắc tắt bớt (gỡ hoặc stop các tiến trình đó) để nhường không gian cho Bot tránh hiện tượng bị Crash do tràn RAM (Out of Memory).
