import aiosqlite

DATABASE = 'clicker.db'


async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                username TEXT,
                points INTEGER,
                click_power INTEGER,
                energy INTEGER,
                autobot_active INTEGER,
                autobot_end_time REAL
            )
        ''')
        await db.commit()


async def get_player(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT * FROM players WHERE id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()


async def add_player(user_id, username):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('INSERT INTO players (id, username, points, click_power, energy, autobot_active, autobot_end_time) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (user_id, username, 0, 1, 500, 0, 0))
        await db.commit()


async def update_player(user_id, **kwargs):
    query = 'UPDATE players SET ' + \
        ', '.join([f'{k} = ?' for k in kwargs.keys()]) + ' WHERE id = ?'
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(query, (*kwargs.values(), user_id))
        await db.commit()
