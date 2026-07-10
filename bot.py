import discord
from discord.ext import commands
import asyncio
import os
import json
from dotenv import load_dotenv

# ============ الإعدادات ============
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
OWNERS_FILE = "owners.json"
UPDATES_ROLE_ID = 1510783082926571580  # الرول اللي يختاره اللاعب بنفسه

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============ إدارة الـ Owners ============
def load_owners():
    if not os.path.exists(OWNERS_FILE):
        initial = [int(x.strip()) for x in os.getenv("OWNER_IDS").split(",")]
        save_owners(initial)
        return initial
    with open(OWNERS_FILE, "r") as f:
        return json.load(f)

def save_owners(owners_list):
    with open(OWNERS_FILE, "w") as f:
        json.dump(owners_list, f)

OWNER_IDS = load_owners()

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS

# ============ حدث الإقلاع ============
@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول بنجاح كـ {bot.user} (ID: {bot.user.id})")
    print(f"📡 متصل على {len(bot.guilds)} سيرفر")
    try:
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"🔄 تم مزامنة {len(synced)} أمر بسيرفر {guild.name} فوراً")
    except Exception as e:
        print(f"⚠️ خطأ بمزامنة الأوامر: {e}")

# ============ !dm و /dm ============
@bot.command(name="dm")
async def dm_user(ctx, member: discord.Member, *, message: str):
    if not is_owner(ctx.author.id):
        await ctx.send("❌ ما عندك صلاحية تستخدم هذا الأمر.")
        return
    try:
        await member.send(message)
        await ctx.send(f"✅ تم إرسال الرسالة إلى {member.name}")
    except discord.Forbidden:
        await ctx.send(f"❌ ما قدرت أرسل لـ {member.name} — مقفل DMs.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ صار خطأ: {e}")

@bot.tree.command(name="dm", description="إرسال رسالة خاصة لشخص معين")
async def slash_dm_user(interaction: discord.Interaction, member: discord.Member, message: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ ما عندك صلاحية.", ephemeral=True)
        return
    try:
        await member.send(message)
        await interaction.response.send_message(f"✅ تم الإرسال إلى {member.name}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ مقفل DMs عند {member.name}.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"❌ خطأ: {e}", ephemeral=True)

# ============ !addowner / !removeowner + Slash ============
@bot.command(name="addowner")
async def add_owner(ctx, member: discord.Member):
    if not is_owner(ctx.author.id):
        await ctx.send("❌ ما عندك صلاحية.")
        return
    if member.id in OWNER_IDS:
        await ctx.send(f"⚠️ {member.name} موجود أصلاً.")
        return
    OWNER_IDS.append(member.id)
    save_owners(OWNER_IDS)
    await ctx.send(f"✅ تم إضافة {member.name}.")

@bot.command(name="removeowner")
async def remove_owner(ctx, member: discord.Member):
    if not is_owner(ctx.author.id):
        await ctx.send("❌ ما عندك صلاحية.")
        return
    if member.id not in OWNER_IDS:
        await ctx.send(f"⚠️ {member.name} مو موجود.")
        return
    OWNER_IDS.remove(member.id)
    save_owners(OWNER_IDS)
    await ctx.send(f"✅ تم إزالة {member.name}.")

@bot.tree.command(name="addowner", description="إضافة شخص مصرّح له")
async def slash_add_owner(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ ما عندك صلاحية.", ephemeral=True)
        return
    if member.id in OWNER_IDS:
        await interaction.response.send_message(f"⚠️ {member.name} موجود أصلاً.", ephemeral=True)
        return
    OWNER_IDS.append(member.id)
    save_owners(OWNER_IDS)
    await interaction.response.send_message(f"✅ تم إضافة {member.name}.", ephemeral=True)

@bot.tree.command(name="removeowner", description="إزالة شخص من المصرّح لهم")
async def slash_remove_owner(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ ما عندك صلاحية.", ephemeral=True)
        return
    if member.id not in OWNER_IDS:
        await interaction.response.send_message(f"⚠️ {member.name} مو موجود.", ephemeral=True)
        return
    OWNER_IDS.remove(member.id)
    save_owners(OWNER_IDS)
    await interaction.response.send_message(f"✅ تم إزالة {member.name}.", ephemeral=True)

# ============ !تنبيه و /تنبيه ============
@bot.command(name="تنبيه")
async def tanbih(ctx, member: discord.Member):
    if not is_owner(ctx.author.id):
        await ctx.send("❌ ما عندك صلاحية تستخدم هذا الأمر.")
        return

    channel_link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}"
    message = (
        f"مرحباً {member.name} 👋\n"
        f"اذهب لتذكرتك، نتمنى منك الرد.\n"
        f"{channel_link}"
    )

    try:
        await member.send(message)
        await ctx.send(f"✅ تم إرسال التنبيه إلى {member.name}")
    except discord.Forbidden:
        await ctx.send(f"❌ ما قدرت أرسل لـ {member.name} — مقفل DMs.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ صار خطأ: {e}")

@bot.tree.command(name="تنبيه", description="تنبيه شخص بالرد على تذكرته")
async def slash_tanbih(interaction: discord.Interaction, member: discord.Member):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ ما عندك صلاحية.", ephemeral=True)
        return

    channel_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}"
    message = (
        f"مرحباً {member.name} 👋\n"
        f"اذهب لتذكرتك، نتمنى منك الرد.\n"
        f"{channel_link}"
    )

    try:
        await member.send(message)
        await interaction.response.send_message(f"✅ تم إرسال التنبيه إلى {member.name}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ مقفل DMs عند {member.name}.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"❌ خطأ: {e}", ephemeral=True)

# ============ !dmall و /dmall (بس لأعضاء الرول المحدد) ============
@bot.command(name="dmall")
async def dm_all(ctx, *, message: str):
    if not is_owner(ctx.author.id):
        await ctx.send("❌ ما عندك صلاحية تستخدم هذا الأمر.")
        return

    role = ctx.guild.get_role(UPDATES_ROLE_ID)
    if role is None:
        await ctx.send("⚠️ الرول غير موجود، تأكد من الـ Role ID.")
        return

    members = [m for m in role.members if not m.bot]
    if not members:
        await ctx.send("⚠️ ما فيه أعضاء مشتركين بهذا الرول حالياً.")
        return

    await ctx.send(f"⏳ جاري الإرسال لـ {len(members)} عضو مشترك بالتحديثات...")

    success = 0
    failed = 0
    for member in members:
        try:
            await member.send(message)
            success += 1
        except discord.Forbidden:
            failed += 1
        except discord.HTTPException:
            failed += 1
        await asyncio.sleep(1.2)

    await ctx.send(f"✅ تم الإرسال: نجح {success}، فشل {failed}.")

@bot.tree.command(name="dmall", description="إرسال رسالة لأعضاء رول التحديثات فقط")
async def slash_dm_all(interaction: discord.Interaction, message: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ ما عندك صلاحية.", ephemeral=True)
        return

    role = interaction.guild.get_role(UPDATES_ROLE_ID)
    if role is None:
        await interaction.response.send_message("⚠️ الرول غير موجود.", ephemeral=True)
        return

    members = [m for m in role.members if not m.bot]
    if not members:
        await interaction.response.send_message("⚠️ ما فيه أعضاء مشتركين بهذا الرول.", ephemeral=True)
        return

    await interaction.response.send_message(f"⏳ جاري الإرسال لـ {len(members)} عضو...", ephemeral=True)

    success = 0
    failed = 0
    for member in members:
        try:
            await member.send(message)
            success += 1
        except discord.Forbidden:
            failed += 1
        except discord.HTTPException:
            failed += 1
        await asyncio.sleep(1.2)

    await interaction.followup.send(f"✅ تم الإرسال: نجح {success}، فشل {failed}.", ephemeral=True)

# ============ تشغيل البوت (لازم يضل آخر شي بالملف) ============
bot.run(TOKEN)	
