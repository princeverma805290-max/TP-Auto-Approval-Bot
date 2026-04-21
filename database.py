from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
# Database se saare functions import kiye
from database import add_user, add_group, all_users, all_groups, users, remove_user, is_admin, add_admin, remove_admin
from configs import cfg
import asyncio, time

app = Client("approver", api_id=cfg.API_ID, api_hash=cfg.API_HASH, bot_token=cfg.BOT_TOKEN)

# Permission Check Logic
def is_privileged(user_id):
    return user_id in cfg.SUDO or is_admin(user_id)

#━━━━━━━━━━━━━━━━━━━━━━━━━ Auto Approve (Immediate Action) ━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_chat_join_request()
async def approve_all_requests(_, m: Message):
    # Jaise hi request aayegi, bot turant accept karega
    chat = m.chat
    user = m.from_user
    
    try:
        # Chat ID database mein save kar li taaki bot ise yaad rakhe
        add_group(chat.id)
        
        # Request Accept karna
        await app.approve_chat_join_request(chat.id, user.id)
        
        # Join Link Logic (1 min expiry)
        expire_time = int(time.time() + 60)
        try:
            invite_link = await app.create_chat_invite_link(chat.id, expire_date=expire_time)
            join_url = invite_link.invite_link
        except:
            join_url = f"https://t.me/{chat.username}" if chat.username else "https://t.me/telegram"

        # Welcome message (Purana Style)
        await app.send_message(
            user.id, 
            "**Hello {}!\nYour Request To Join {} Has Approved Successfully ✅\n\n[Join Channel]({})\n\n__Made By : @TP_02_Bots __ Powered By : @HENTAI_HUB_02__**".format(user.mention, chat.title, join_url),
            disable_web_page_preview=True
        )
        add_user(user.id)
    except Exception as e:
        print(f"Error: {e}")

#━━━━━━━━━━━━━━━━━━━━━━━━━ Admin & Remove Admin (Permanent) ━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("addadmin") & filters.private)
async def make_admin(_, m: Message):
    if m.from_user.id not in cfg.SUDO:
        if is_admin(m.from_user.id):
            return await m.reply_text("if you want to add another Admin so tell the owner", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Owner", url=f"tg://user?id={cfg.SUDO[0]}")]]))
        return await m.reply_text("This is for only owner")
    
    if len(m.command) == 1:
        return await m.reply_text("send me the adding Admin id for set admin")
    
    try:
        new_id = int(m.command[1])
        add_admin(new_id) # Database mein permanent save
        await m.reply_text(f"✅ User `{new_id}` is now a Permanent Admin.")
    except:
        await m.reply_text("Invalid ID.")

@app.on_message(filters.command("removeadmin") & filters.private)
async def delete_admin(_, m: Message):
    if m.from_user.id not in cfg.SUDO:
        return await m.reply_text("This is for only owner")
    
    if len(m.command) == 1:
        return await m.reply_text("Send me the Admin ID to remove.")
    
    try:
        rem_id = int(m.command[1])
        remove_admin(rem_id) # Database se remove
        await m.reply_text(f"❌ User `{rem_id}` removed from Admin list.")
    except:
        await m.reply_text("Invalid ID.")

#━━━━━━━━━━━━━━━━━━━━━━━━━ Other Commands (Bcast/Stats) ━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command(["bcast", "fcast"]))
async def bcast_handler(_, m: Message):
    if not is_privileged(m.from_user.id):
        return await m.reply_text("this only for Owner & Admins")
    
    if not m.reply_to_message:
        return await m.reply_text("Reply to a message to broadcast.")
    
    process = await m.reply_text("`⚡️ Processing...`")
    success, failed = 0, 0
    
    for user in users.find():
        try:
            if m.command[0] == "bcast":
                await m.reply_to_message.copy(int(user["user_id"]))
            else:
                await m.reply_to_message.forward(int(user["user_id"]))
            success += 1
            await asyncio.sleep(0.3)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            failed += 1
            
    await process.edit(f"✅ Success: `{success}`\n❌ Failed: `{failed}`")

@app.on_message(filters.command("users"))
async def stats(_, m: Message):
    if not is_privileged(m.from_user.id):
        return await m.reply_text("this only for Owner & Admins")
    await m.reply_text(f"🙋‍♂️ Users: `{all_users()}`\n👥 Groups/Channels: `{all_groups()}`")

@app.on_message(filters.command("id"))
async def show_id(_, m: Message):
    target = m.reply_to_message.from_user if m.reply_to_message else m.from_user
    await m.reply_text(f"👤 **Name:** {target.mention}\n🆔 **ID:** `{target.id}`")

# Restart ke baad bot ko active rakhne ke liye
print("Bot Started! Permanent Channels and Admins are Active.")
app.run()