import os, asyncio, signal
from io import BytesIO
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters, ContextTypes)

TOKEN = os.environ["BOT_TOKEN"]
ALLOWED = {int(x) for x in os.environ["ALLOWED_IDS"].split(",")}
TIMEOUT = int(os.getenv("TIMEOUT", "300"))
running = {}  # user_id -> process


def ok(update):
    return update.effective_user and update.effective_user.id in ALLOWED


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ok(update):
        return
    await update.message.reply_text(
        "Kali Lab tayyor.\nHar pagom = farmoni terminal.\n"
        "/cancel - qat' kardani farmon\n/id - ID-i shumo")


async def myid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.effective_user.id))


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ok(update):
        return
    p = running.get(update.effective_user.id)
    if p and p.returncode is None:
        os.killpg(p.pid, signal.SIGKILL)
        await update.message.reply_text("Qat' shud.")
    else:
        await update.message.reply_text("Farmoni faol nest.")


async def shell(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ok(update):
        return
    uid = update.effective_user.id
    cmd = update.message.text.strip()
    cwd = ctx.user_data.get("cwd", "/work")

    if cmd == "cd" or cmd.startswith("cd "):
        target = os.path.abspath(
            os.path.join(cwd, os.path.expanduser(cmd[2:].strip() or "~")))
        if os.path.isdir(target):
            ctx.user_data["cwd"] = target
            await update.message.reply_text(target)
        else:
            await update.message.reply_text("Papka nest")
        return

    if uid in running and running[uid].returncode is None:
        await update.message.reply_text("Farmoni digar kor mekunad. /cancel")
        return

    os.makedirs(cwd, exist_ok=True)
    p = await asyncio.create_subprocess_shell(
        cmd, cwd=cwd, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT, start_new_session=True)
    running[uid] = p
    try:
        out, _ = await asyncio.wait_for(p.communicate(), TIMEOUT)
    except asyncio.TimeoutError:
        os.killpg(p.pid, signal.SIGKILL)
        out, _ = await p.communicate()
        out += f"\n[timeout {TIMEOUT}s]".encode()

    text = out.decode(errors="replace").strip() or "(natija nest)"
    if len(text) > 3900:
        f = BytesIO(out)
        f.name = "output.txt"
        await update.message.reply_document(f)
    else:
        await update.message.reply_text(text)


def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", myid))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shell))
    app.run_polling()


if __name__ == "__main__":
    main()
