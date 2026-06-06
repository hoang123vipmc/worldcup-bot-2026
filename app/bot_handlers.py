from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from ml_core.predictor import MatchPredictor
from app.external_api import get_upcoming_matches
from app.database import save_prediction, get_user_history, get_global_stats

# Initialize the router for bot handlers
router = Router()

# Initialize the Match Predictor AI
predictor = MatchPredictor()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Handle the /start command.
    """
    await message.answer(
        "Xin chào! Tôi là Trợ lý AI dự đoán World Cup 2026. Hệ thống đang đồng bộ dữ liệu, vui lòng chờ trong giây lát..."
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Handle the /help command.
    """
    help_text = (
        "🤖 *DANH SÁCH CÁC LỆNH:*\n\n"
        "🔹 /start: Khởi động lại bot.\n"
        "🔹 /schedule: Xem lịch thi đấu World Cup 2026.\n"
        "🔹 /predict [Đội 1] vs [Đội 2]: Dự đoán nhanh bằng AI.\n"
        "🔹 /history: Xem lịch sử dự đoán.\n"
        "🔹 /stats: Xem thống kê dự đoán cộng đồng.\n"
        "🔹 /help: Xem hướng dẫn sử dụng."
    )
    
    # Create inline button linking to admin
    btn = InlineKeyboardButton(text="Liên hệ Admin", url="https://t.me/admin")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])
    
    await message.answer(help_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

@router.message(Command("predict"))
async def cmd_predict(message: types.Message):
    """
    Handle the /predict command.
    Expected syntax: /predict [Team 1] vs [Team 2]
    """
    try:
        # Extract arguments after the /predict command
        text = message.text.replace("/predict", "").strip()
        
        # Validate syntax
        if " vs " not in text.lower():
            await message.answer(
                "❌ *Sai cú pháp!* Vui lòng nhập theo định dạng:\n`/predict [Đội 1] vs [Đội 2]`\nVí dụ: `/predict Brazil vs France`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
            
        # Parse team names
        parts = text.lower().split(" vs ")
        # Using .title() to format e.g. 'brazil' -> 'Brazil', 'costa rica' -> 'Costa Rica'
        home_team = parts[0].strip().title()
        away_team = parts[1].strip().title()
        
        # Get predictions from ML model
        prediction = predictor.predict_win_probability(home_team, away_team)
        
        if not prediction or "error" in prediction:
            await message.answer("⚠️ Xin lỗi, hệ thống AI hiện chưa sẵn sàng. Vui lòng thử lại sau.")
            return

        # Format the output beautifully using Markdown
        response = (
            f"⚽ *DỰ ĐOÁN KẾT QUẢ* ⚽\n"
            f"🏟️ *{home_team}* vs *{away_team}*\n\n"
            f"📊 *Tỷ lệ dự báo từ AI:*\n"
            f"🔹 Thắng ({home_team}): *{prediction['home_win']}%*\n"
            f"➖ Hòa: *{prediction['draw']}%*\n"
            f"🔸 Thắng ({away_team}): *{prediction['away_win']}%*"
        )
        
        await message.answer(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        # Gracefully handle any unexpected errors or missing teams
        await message.answer("⚠️ Đã có lỗi xảy ra. Vui lòng kiểm tra lại cú pháp hoặc chắc chắn rằng bạn đã nhập đúng tên tiếng Anh của đội bóng nhé!")

@router.message(Command("history"))
async def cmd_history(message: types.Message):
    """
    Handle the /history command.
    """
    user_id = message.from_user.id
    history = get_user_history(user_id, limit=5)
    
    if not history:
        await message.answer("Bạn chưa có dự đoán nào. Hãy thử dùng lệnh `/schedule` nhé!", parse_mode=ParseMode.MARKDOWN)
        return
        
    response_lines = ["📜 *LỊCH SỬ DỰ ĐOÁN:*\n"]
    
    for item in history:
        home_team = item.get("home_team", "TBA")
        away_team = item.get("away_team", "TBA")
        prediction = item.get("prediction_result", {})
        
        home_win = prediction.get("home_win", 0)
        draw = prediction.get("draw", 0)
        away_win = prediction.get("away_win", 0)
        
        if home_win > draw and home_win > away_win:
            pred_str = f"Thắng ({home_team})"
        elif away_win > home_win and away_win > draw:
            pred_str = f"Thắng ({away_team})"
        else:
            pred_str = "Hòa"
            
        timestamp = item.get("timestamp")
        if timestamp:
            vn_time = timestamp + timedelta(hours=7)
            date_str = vn_time.strftime("%d/%m/%Y")
        else:
            date_str = "N/A"
            
        response_lines.append(f"🔹 *{date_str}*: {home_team} vs {away_team} ➡️ {pred_str}")
        
    await message.answer("\n".join(response_lines), parse_mode=ParseMode.MARKDOWN)

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """
    Handle the /stats command.
    """
    stats = get_global_stats()
    
    if not stats:
        await message.answer("Chưa có đủ dữ liệu thống kê từ cộng đồng.", parse_mode=ParseMode.MARKDOWN)
        return
        
    response_lines = ["📊 *ĐỘI BÓNG ĐƯỢC CỘNG ĐỒNG TIN TƯỞNG NHẤT:*\n"]
    
    total_votes = sum([item["count"] for item in stats])
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
    
    for idx, item in enumerate(stats):
        team = item["_id"]
        count = item["count"]
        
        # Calculate percentage to create a simple text chart (max 10 blocks)
        percentage = (count / total_votes) if total_votes > 0 else 0
        blocks = int(percentage * 10)
        chart = "🟩" * blocks + "⬜" * (10 - blocks)
        
        medal = medals[idx] if idx < len(medals) else "🔹"
        response_lines.append(f"{medal} *{team}*: {count} phiếu\n{chart} ({round(percentage * 100, 1)}%)")
        
    await message.answer("\n\n".join(response_lines), parse_mode=ParseMode.MARKDOWN)

@router.message(Command("schedule"))
async def cmd_schedule(message: types.Message):
    """
    Handle the /schedule command to show upcoming matches.
    """
    try:
        matches = await get_upcoming_matches()
        
        if not matches:
            await message.answer("Hiện tại không có trận đấu nào sắp diễn ra.")
            return
            
        for match in matches:
            home_team = match["home_team"]
            away_team = match["away_team"]
            
            # Parse time and convert UTC to UTC+7 (Vietnam Time)
            try:
                utc_time = datetime.strptime(match['kickoff_time'], "%Y-%m-%dT%H:%M:%SZ")
                vn_time = utc_time + timedelta(hours=7)
                time_str = vn_time.strftime("%d/%m/%Y - %H:%M")
            except (ValueError, TypeError):
                time_str = "Chưa xác định"
                
            stadium_str = "Chưa xác định" if match['stadium'] == 'TBA' else match['stadium']
            
            # Format message
            msg_text = (
                f"🏆 Trận đấu: *{home_team}* vs *{away_team}*\n"
                f"📅 Thời gian: {time_str}\n"
                f"🏟 Địa điểm: {stadium_str}\n"
                f"🔮 Dự đoán: Nhấn nút bên dưới để AI đưa ra tỷ lệ chiến thắng!"
            )
            
            # Create inline button
            btn = InlineKeyboardButton(
                text="🔮 AI Dự đoán tỉ lệ",
                callback_data=f"predict_{home_team}_{away_team}"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])
            
            await message.answer(msg_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
            
    except Exception as e:
        await message.answer("⚠️ Đã có lỗi xảy ra khi lấy lịch thi đấu.")


@router.callback_query(F.data.startswith("predict_"))
async def callback_predict(callback: types.CallbackQuery):
    """
    Handle the inline button click for AI Prediction.
    """
    try:
        data_parts = callback.data.split("_")
        if len(data_parts) >= 3:
            home_team = data_parts[1]
            away_team = data_parts[2]
            
            prediction = predictor.predict_win_probability(home_team, away_team)
            
            if not prediction or "error" in prediction:
                # Show popup if error
                await callback.answer(text="⚠️ Hệ thống AI hiện chưa sẵn sàng.", show_alert=True)
            else:
                # Save to database
                save_prediction(callback.from_user.id, home_team, away_team, prediction)
                
                # Send a new message with prediction results
                response = (
                    f"⚽ *DỰ ĐOÁN KẾT QUẢ* ⚽\n"
                    f"🏟️ *{home_team}* vs *{away_team}*\n\n"
                    f"📊 *Tỷ lệ dự báo từ AI:*\n"
                    f"🔹 Thắng ({home_team}): *{prediction['home_win']}%*\n"
                    f"➖ Hòa: *{prediction['draw']}%*\n"
                    f"🔸 Thắng ({away_team}): *{prediction['away_win']}%*"
                )
                await callback.message.answer(response, parse_mode=ParseMode.MARKDOWN)
                
                # Acknowledge the callback lightly to stop the loading icon
                await callback.answer(text="Đã phân tích xong! ✅")
        else:
            await callback.answer(text="⚠️ Dữ liệu không hợp lệ.", show_alert=True)
            
    except Exception as e:
        await callback.answer(text="⚠️ Đã có lỗi xảy ra trong quá trình dự đoán.", show_alert=True)
