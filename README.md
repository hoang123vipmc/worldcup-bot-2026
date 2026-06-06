# World Cup 2026 AI Predictor Bot 🏆🤖

Bot Telegram dự đoán tỉ số World Cup 2026 bằng mô hình Machine Learning (Random Forest) và lấy lịch thi đấu thực tế từ API.

## 🚀 Tính Năng Nổi Bật
- **`/start`**: Khởi động Bot.
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
- **Xem Nhật ký tin nhắn (Logs) của Bot:** `docker logs worldcup_bot -f` (Bấm Ctrl+C để thoát)

## 💡 Lưu Ý Về Tài Nguyên (RAM / CPU)
- Dự án này bao gồm cả một mô hình Machine Learning được load thẳng vào RAM, cộng thêm 2 Database (MongoDB và Redis). 
- Khuyến nghị VPS nên có tối thiểu **1GB - 2GB RAM**.
- Nếu bạn đang chạy các node blockchain hoặc các dự án ngốn phần cứng khác trên cùng server, hãy cân nhắc tắt bớt (gỡ hoặc stop các tiến trình đó) để nhường không gian cho Bot tránh hiện tượng bị Crash do tràn RAM (Out of Memory).
