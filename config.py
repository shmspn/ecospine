import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _fix_db_url(url: str) -> str:
    """Railway PostgreSQL URL ni SQLAlchemy uchun to'g'rilash.
    
    Railway ba'zan 'postgres://' prefix bilan beradi,
    lekin SQLAlchemy 2.x faqat 'postgresql://' qabul qiladi.
    """
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    # Har doim env variable dan olish kerak, default FAQAT local dev uchun
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')

    _db_url = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'ecospine.db')
    )
    SQLALCHEMY_DATABASE_URI = _fix_db_url(_db_url)

    SQLALCHEMY_TRACK_MODIFICATIONS = False