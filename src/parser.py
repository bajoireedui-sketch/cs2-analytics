from awpy import Demo
from pathlib import Path
from typing import Optional
import polars as pl


DEMO_DIR = Path("demos")


def get_demo_path(demo_filename: str) -> Path:
    """Demo файлын бүтэн замыг буцаана"""
    path = DEMO_DIR / demo_filename
    if not path.exists():
        raise FileNotFoundError(f"Demo файл олдсонгүй: {path}")
    return path


def load_demo(demo_filename: str) -> Demo:
    """
    Demo объектыг үүсгэж буцаана.
    Дараа нь .kills, .stats, .rounds гэх мэтийг ашиглана.
    """
    demo_path = get_demo_path(demo_filename)
    print(f"Уншиж байна: {demo_path}")
    demo = Demo(str(demo_path))
    return demo


def load_demo_data(demo_filename: str) -> dict:
    """
    Demo-оос гол өгөгдлүүдийг нэг дор гаргаж dict хэлбэрээр буцаана.
    """
    demo = load_demo(demo_filename)

    data = {
        "header": demo.header,
        "map_name": demo.header.get("map_name"),
        "stats": demo.stats,          # ADR, KAST, K/D гэх мэт
        "rounds": demo.rounds,        # Round бүрийн мэдээлэл
        "kills": demo.kills,          # Бүх аллага
        "damages": demo.damages,      # Damage event-үүд
        "bomb": demo.bomb,            # Bomb plant/defuse
        "shots": demo.shots,          # Буудсан буудлага
    }

    print(f"Map: {data['map_name']}")
    print(f"Rounds: {len(data['rounds'])} | Kills: {len(data['kills'])}")
    return data


def load_demo_kills(demo_filename: str) -> pl.DataFrame:
    """Зөвхөн kills буцаах (хуучин функц, нийцтэй байлгах)"""
    demo = load_demo(demo_filename)
    return demo.kills


def load_demo_stats(demo_filename: str) -> pl.DataFrame:
    """Scoreboard (stats) буцаах"""
    demo = load_demo(demo_filename)
    return demo.stats