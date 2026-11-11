from src.parser import load_demo_data
import polars as pl
import matplotlib.pyplot as plt

def main():
    print("CS2 Analytics - График болон Эдийн засгийн шинжилгээ эхэллээ...\n")

    demo_file = "spirit-vs-fut-m1-cache.dem"
    data = load_demo_data(demo_file)

    stats_df = data["stats"]
    damages_df = data["damages"]

    # 1. PLAYER STATS (ADR-ээр эрэмбэлсэн)
    print("\n" + "="*50)
    print("📊 PLAYER STATS (ADR-ээр эрэмбэлсэн)")
    print("="*50)
    print(
        stats_df
        .select("name", "kills", "deaths", "assists", "adr", "kast")
        .sort("adr", descending=True)
    )

    # 2. UTILITY & DAMAGE ANALYSIS (Гранатын болон нийт хохирол)
    print("\n" + "="*50)
    print("💣 UTILITY & DAMAGE ANALYSIS (Гранатын хохирол)")
    print("="*50)
    
    # damages хүснэгтээс weapon/grenade төрлөөр нь шүүж utility damage-ийг олох
    # CS2 дээр HE grenade, molotov, incgrenade зэрэг нь utility damage-д орно
    if "weapon" in damages_df.columns:
        utility_weapons = ["hegrenade", "inferno", "molotov"]
        util_damage = (
            damages_df
            .filter(pl.col("weapon").is_in(utility_weapons))
            .group_by("attacker_name")
            .agg(pl.col("dmg_health").sum().alias("total_utility_damage"))
            .sort("total_utility_damage", descending=True)
        )
        print(util_damage)
    else:
        print("Damage хүснэгтээс зэвсгийн мэдээлэл олдсонгүй.")

    # 3. MATPLOTLIB ГРАФИК ДҮРСЛЭЛ (ADR болон Kills харьцуулсан бар график)
    print("\n" + "="*50)
    print("📈 График үүсгэж байна...")
    print("="*50)

    # Polars өгөгдлийг pandas руу хөрвүүлж matplotlib-д ашиглахад хялбар болгоно
    chart_data = stats_df.sort("adr", descending=True).to_pandas()

    plt.figure(figsize=(10, 6))
    
    # Тоглогчдын ADR-ийг харуулсан бар график
    bars = plt.bar(chart_data["name"], chart_data["adr"], color='skyblue', edgecolor='navy')
    
    plt.title(f"Map: {data['map_name']} - Player ADR (Average Damage per Round)", fontsize=14, fontweight='bold')
    plt.xlabel("Players", fontsize=12)
    plt.ylabel("ADR", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Багана тус бүрийн дээр тоон утгыг нь бичих
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2.,
            height + 1,
            f"{height:.1f}",
            ha='center', va='bottom', fontsize=9
        )

    plt.tight_layout()
    
    # Графикийг зургаар хадгалах
    output_image = "player_adr_chart.png"
    plt.savefig(output_image)
    print(f"График амжилттай хадгалагдлаа: {output_image}")
    
    # Дэлгэц дээр графикийг шууд гаргаж харуулах
    plt.show()

if __name__ == "__main__":
    main()