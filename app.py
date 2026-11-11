import streamlit as st
import polars as pl
import matplotlib.pyplot as plt
from pathlib import Path
from src.parser import load_demo_data, DEMO_DIR

# Streamlit хуудасны тохиргоо
st.set_page_config(page_title="CS2 Analytics Dashboard", page_icon="🎯", layout="wide")

st.title("🎯 CS2 Advanced Analytics Dashboard")
st.markdown("HLTV Demo файлаа задлан шинжлэх интерактив вэб систем.")

# 1. Multi-Demo Support: demos/ хавтас доторх .dem файлуудыг шүүж олох
demo_files = [f.name for f in DEMO_DIR.glob("*.dem")]

if not demo_files:
    st.error("⚠️ `demos/` хавтас дотор ямар ч `.dem` файл олдсонгүй! Файлаа шалгана уу.")
else:
    # Sidebar дээр demo сонгох цэс үүсгэх
    st.sidebar.header("📁 Demo сонгох")
    selected_demo = st.sidebar.selectbox("Шинжлэх demo файлаа сонгоно уу:", demo_files)
    
    # Demo өгөгдлийг ачааллах (Streamlit-ийн cache ашиглан хурдлуулна)
    @st.cache_data
    def get_data(filename):
        return load_demo_data(filename)

    with st.spinner(f"'{selected_demo}' файлыг уншиж байна... Түр хүлээнэ үү."):
        data = get_data(selected_demo)

    st.sidebar.success(f"Map: **{data['map_name']}**")
    st.sidebar.info(f"Нийт раунд: {len(data['rounds'])} | Нийт kill: {len(data['kills'])}")

    # Tab-уудаар мэдээллээ ангилах
    tab1, tab2, tab3 = st.tabs(["📊 Player Stats & ADR", "🔫 Headshot & Weapons", "🛡️ Rounds & Utility"])

    # --- TAB 1: PLAYER STATS & ADR ---
    with tab1:
        st.subheader("Тоглогчдын үндсэн статистик (ADR, Kills, Deaths)")
        
        stats_df = data["stats"]
        kills_df = data["kills"]

        # Headshot хувийг тооцоолох (Headshot % calculation)
        if "headshot" in kills_df.columns and "attacker_name" in kills_df.columns:
            hs_counts = (
                kills_df.filter(pl.col("headshot") == True)
                .group_by("attacker_name")
                .len()
                .rename({"len": "hs_kills"})
            )
            total_kills = (
                kills_df.group_by("attacker_name")
                .len()
                .rename({"len": "total_kills"})
            )
            hs_df = total_kills.join(hs_counts, on="attacker_name", how="left").fill_null(0)
            hs_df = hs_df.with_columns(
                (pl.col("hs_kills") / pl.col("total_kills") * 100).round(1).alias("headshot_pct")
            )
            
            # Stats хүснэгттэй нэгтгэх
            stats_pd = stats_df.to_pandas()
            hs_pd = hs_df.select("attacker_name", "headshot_pct").to_pandas()
            
            # DataFrame дээр Headshot хувийг харуулах холболт
            merged_stats = stats_pd.merge(hs_pd, left_on="name", right_on="attacker_name", how="left")
            if "attacker_name" in merged_stats.columns:
                merged_stats = merged_stats.drop(columns=["attacker_name"])
            st.dataframe(merged_stats, use_container_width=True)
        else:
            st.dataframe(stats_df, use_container_width=True)

        # ADR Бар График
        st.markdown("### 📈 Тоглогчдын ADR (Average Damage per Round) Харьцуулалт")
        fig, ax = plt.subplots(figsize=(10, 4))
        chart_data = stats_df.sort("adr", descending=True)
        players = chart_data["name"].to_list()
        adr_values = chart_data["adr"].to_list()

        bars = ax.bar(players, adr_values, color='skyblue', edgecolor='navy')
        ax.set_ylabel("ADR")
        ax.set_xlabel("Players")
        plt.xticks(rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Багана дээр тоон утгыг бичих
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 1,
                f"{height:.1f}",
                ha='center', va='bottom', fontsize=9
            )

        st.pyplot(fig)

    # --- TAB 2: WEAPONS & HEADSHOTS ---
    with tab2:
        st.subheader("🔫 Зэвсгийн анализ (Ямар зэвсгээр хэдэн kill авсан бэ)")
        if "weapon" in kills_df.columns:
            weapons_df = (
                kills_df.group_by("weapon")
                .len()
                .sort("len", descending=True)
            )
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(weapons_df, use_container_width=True)
            with col2:
                # Зэвсгийн тархалтыг пирог график эсвэл бар график хэлбэрээр харуулах
                fig_w, ax_w = plt.subplots(figsize=(6, 4))
                w_top = weapons_df.head(5).to_pandas()
                ax_w.barh(w_top["weapon"], w_top["len"], color='orange', edgecolor='brown')
                ax_w.set_xlabel("Kill count")
                ax_w.invert_yaxis()
                st.pyplot(fig_w)
        else:
            st.warning("Зэвсгийн мэдээлэл олдсонгүй.")

    # --- TAB 3: ROUNDS & UTILITY ---
    with tab3:
        st.subheader("🛡️⚔️ Раунд болон Талуудын гүйцэтгэл (CT vs T)")
        side_wins = (
            data["rounds"]
            .group_by("winner_side")
            .len()
            .sort("len", descending=True)
        )
        st.dataframe(side_wins, use_container_width=True)

        st.subheader("💣 Utility Damage (Гранатын хохирол)")
        damages_df = data["damages"]
        if "weapon" in damages_df.columns:
            utility_weapons = ["hegrenade", "inferno", "molotov"]
            util_damage = (
                damages_df.filter(pl.col("weapon").is_in(utility_weapons))
                .group_by("attacker_name")
                .agg(pl.col("dmg_health").sum().alias("total_utility_damage"))
                .sort("total_utility_damage", descending=True)
            )
            st.dataframe(util_damage, use_container_width=True)