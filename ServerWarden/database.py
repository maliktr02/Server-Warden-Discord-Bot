import aiosqlite
import json
from datetime import datetime

class Database:
    def __init__(self, db_file="serverwarden.db"):
        self.db_file = db_file

    async def init(self):
        """Veritabanı tablolarını oluşturur"""
        async with aiosqlite.connect(self.db_file) as db:
            # Uyarılar tablosu
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            ''')

            # Yasaklı kelimeler tablosu
            await db.execute('''
                CREATE TABLE IF NOT EXISTS banned_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    word TEXT NOT NULL
                )
            ''')

            # Premium sunucular tablosu
            await db.execute('''
                CREATE TABLE IF NOT EXISTS premium_servers (
                    guild_id INTEGER PRIMARY KEY,
                    expiry_date DATETIME
                )
            ''')

            # Özel komutlar tablosu
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    command_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME NOT NULL
                )
            ''')

            # Otomatik roller tablosu
            await db.execute('''
                CREATE TABLE IF NOT EXISTS auto_roles (
                    guild_id INTEGER PRIMARY KEY,
                    role_id INTEGER NOT NULL
                )
            ''')

            # Yedekler tablosu
            await db.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    data TEXT NOT NULL
                )
            ''')

            await db.commit()

    async def add_warning(self, user_id: int, guild_id: int, reason: str, moderator_id: int):
        """Uyarı ekler"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                'INSERT INTO warnings (user_id, guild_id, reason, moderator_id, timestamp) VALUES (?, ?, ?, ?, ?)',
                (user_id, guild_id, reason, moderator_id, datetime.now())
            )
            await db.commit()

    async def get_warnings(self, user_id: int, guild_id: int):
        """Kullanıcının uyarılarını getirir"""
        async with aiosqlite.connect(self.db_file) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM warnings WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            return await cursor.fetchall()

    async def add_banned_word(self, guild_id: int, word: str):
        """Yasaklı kelime ekler"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                'INSERT INTO banned_words (guild_id, word) VALUES (?, ?)',
                (guild_id, word.lower())
            )
            await db.commit()

    async def get_banned_words(self, guild_id: int):
        """Sunucunun yasaklı kelimelerini getirir"""
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute(
                'SELECT word FROM banned_words WHERE guild_id = ?',
                (guild_id,)
            )
            return [row[0] for row in await cursor.fetchall()]

    async def is_premium(self, guild_id: int):
        """Sunucunun premium olup olmadığını kontrol eder"""
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute(
                'SELECT expiry_date FROM premium_servers WHERE guild_id = ? AND expiry_date > ?',
                (guild_id, datetime.now())
            )
            return bool(await cursor.fetchone())

    async def add_premium(self, guild_id: int, days: int):
        """Premium üyelik ekler"""
        async with aiosqlite.connect(self.db_file) as db:
            expiry_date = datetime.now() + timedelta(days=days)
            await db.execute(
                'INSERT OR REPLACE INTO premium_servers (guild_id, expiry_date) VALUES (?, ?)',
                (guild_id, expiry_date)
            )
            await db.commit()

    async def add_custom_command(self, guild_id: int, command_name: str, response: str, created_by: int):
        """Özel komut ekler"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                'INSERT INTO custom_commands (guild_id, command_name, response, created_by, created_at) VALUES (?, ?, ?, ?, ?)',
                (guild_id, command_name, response, created_by, datetime.now())
            )
            await db.commit()

    async def get_custom_command(self, guild_id: int, command_name: str):
        """Özel komut getirir"""
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute(
                'SELECT response FROM custom_commands WHERE guild_id = ? AND command_name = ?',
                (guild_id, command_name)
            )
            result = await cursor.fetchone()
            return result[0] if result else None

    async def set_auto_role(self, guild_id: int, role_id: int):
        """Otomatik rol ayarlar"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                'INSERT OR REPLACE INTO auto_roles (guild_id, role_id) VALUES (?, ?)',
                (guild_id, role_id)
            )
            await db.commit()

    async def get_auto_role(self, guild_id: int):
        """Otomatik rol getirir"""
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute(
                'SELECT role_id FROM auto_roles WHERE guild_id = ?',
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None

    async def add_backup(self, guild_id: int, data: dict):
        """Sunucu yedeği ekler"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                'INSERT INTO backups (guild_id, timestamp, data) VALUES (?, ?, ?)',
                (guild_id, datetime.now(), json.dumps(data))
            )
            await db.commit()

    async def get_latest_backup(self, guild_id: int):
        """En son yedeği getirir"""
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute(
                'SELECT data FROM backups WHERE guild_id = ? ORDER BY timestamp DESC LIMIT 1',
                (guild_id,)
            )
            result = await cursor.fetchone()
            return json.loads(result[0]) if result else None 