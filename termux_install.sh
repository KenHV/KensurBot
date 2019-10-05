clear
echo -E "    ____                              __                   "
echo -E "   / __ \____ _____  ___  _________  / /___ _____  ___     "
echo -E "  / /_/ / __ `/ __ \/ _ \/ ___/ __ \/ / __ `/ __ \/ _ \    "
echo -E " / ____/ /_/ / /_/ /  __/ /  / /_/ / / /_/ / / / /  __/    "
echo -E "/_/    \__,_/ .___/\___/_/  / .___/_/\__,_/_/ /_/\___/     "
echo -E "           /_/             /_/                             "
echo -E "       ______     __                 __         __         "
echo -E "      / ____/  __/ /____  ____  ____/ /__  ____/ /         "
echo -E "     / __/ | |/_/ __/ _ \/ __ \/ __  / _ \/ __  /          "
echo -E "    / /____>  </ /_/  __/ / / / /_/ /  __/ /_/ /           "
echo -E "   /_____/_/|_|\__/\___/_/ /_/\__,_/\___/\__,_/            "
echo -E "                                                           "
sleep 5
clear

pkg update && pkg upgrade -y
pkg install clang curl git libcrypt libffi libiconv libjpeg* libjpeg-turbo libwebp libxml2 libxslt make ndk-sysroot openssl postgresql python readline wget zlib -y

git clone https://github.com/AvinashReddy3108/PaperplaneExtended.git
cd PaperplaneExtended

pip install --upgrade pip setuptools
pip install -r requirements.txt

mv sample_config.env config.env

mkdir -p $PREFIX/var/lib/postgresql
initdb $PREFIX/var/lib/postgresql
pg_ctl -D $PREFIX/var/lib/postgresql start
createdb botdb
createuser botuser

cd ..
echo "pg_ctl -D $PREFIX/var/lib/postgresql start" > startbot.sh
echo "cd PaperplaneExtended" >> startbot.sh
echo "python3 -m userbot" >> startbot.sh
chmod 755 startbot.sh

echo "Done."
echo "Now edit config.env with nano or anything you want, then run the userbot with startbot.sh"
echo "Please edit the db to postgresql://botuser:@localhost:5432/botdb"
echo "Good luck!"
