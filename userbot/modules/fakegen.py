from faker import Faker
from faker.providers import internet
from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern="^.fakegen(?: |$)(.*)", disable_errors=True)
async def hi(event):
    if event.fwd_from:
        return
    fake = Faker()
    print("FAKE DETAILS GENERATED\n")
    name = str(fake.name())
    fake.add_provider(internet)
    address = str(fake.address())
    ip = fake.ipv4_private()
    cc = fake.credit_card_full()
    email = fake.ascii_free_email()
    job = fake.job()
    android = fake.android_platform_token()
    pc = fake.chrome()
    await event.edit(
        f"<b><u> Fake Information Generated</b></u>\n<b>👥 Nama : </b><code>{name}</code>\n\n<b>🏘️ Alamat : </b><code>{address}</code>\n\n<b>🤖 Alamat IP : </b><code>{ip}</code>\n\n<b>🏧 Kartu Kredit : </b><code>{cc}</code>\n<b>🔗 Alamat Email : </b><code>{email}</code>\n\n<b>👨🏻‍🔧 Pekerjaan : </b><code>{job}</code>\n\n<b>📱 Android User-Agent : </b><code>{android}</code>\n\n<b>🖥️ PC User-Agent : </b><code>{pc}</code>",
        parse_mode="HTML",
    )


CMD_HELP.update(
    {
        "fakegen": "**Fake information Generator**\
\n\n**Syntax : **`.fakegen`\
\n**Usage :** Automatically generates fake information."
    }
)
