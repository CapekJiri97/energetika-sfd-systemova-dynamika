from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="SFD Energetika", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

    :root {
        --bg-main: #0a0f1a;
        --bg-card: #101a2b;
        --bg-soft: #17243a;
        --text-main: #ecf3ff;
        --text-soft: #a8bddc;
        --accent: #52c7ea;
        color-scheme: dark;
    }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text-main);
    }

    .stApp {
        color: var(--text-main);
        background:
            radial-gradient(circle at 12% 18%, #15263c 0%, rgba(21, 38, 60, 0.4) 25%, rgba(10, 15, 26, 0.95) 55%),
            radial-gradient(circle at 88% 10%, #1f2d47 0%, rgba(31, 45, 71, 0.28) 28%, rgba(10, 15, 26, 0.92) 62%),
            linear-gradient(145deg, #090d16 0%, #0e1524 55%, #090d16 100%);
    }

    h1, h2, h3 {
        letter-spacing: 0.02em;
        color: var(--text-main);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1a2b 0%, #0b1320 100%);
        border-right: 1px solid #25324a;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-main);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, var(--bg-card), #0d1727);
        border: 1px solid #243651;
        border-radius: 12px;
        padding: 10px 12px;
    }

    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--text-main);
    }

    [data-testid="stMarkdownContainer"] p {
        color: var(--text-soft);
    }

    [data-testid="stExpander"] details {
        background: linear-gradient(180deg, var(--bg-card), #0d1727);
        border: 1px solid #243651;
        border-radius: 12px;
    }

    [data-testid="stExpander"] summary {
        background: linear-gradient(180deg, var(--bg-card), #0d1727);
        color: var(--text-main);
        border-radius: 12px;
    }

    [data-testid="stExpanderDetails"] {
        background: rgba(16, 26, 43, 0.72);
        border-radius: 0 0 12px 12px;
    }

    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input,
    .stSlider {
        background-color: var(--bg-soft);
        color: var(--text-main);
    }

    div[data-baseweb="popover"] > div {
        background: #101a2b !important;
        border: 1px solid #243651 !important;
        color: #ecf3ff !important;
    }

    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"] {
        background: #101a2b !important;
        color: #ecf3ff !important;
    }

    div[data-baseweb="popover"] [aria-selected="true"] {
        background: #17243a !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_DARK_LAYOUT = {
    "template": "plotly_dark",
    "paper_bgcolor": "#0a0f1a",
    "plot_bgcolor": "#0a0f1a",
    "font": {"color": "#ecf3ff", "family": "Space Grotesk, sans-serif"},
    "legend": {"bgcolor": "rgba(10,15,26,0.85)"},
}


def load_model_module():
    model_path = Path(__file__).with_name("SFD Energetika.py")
    spec = importlib.util.spec_from_file_location("sfd_energetika_core", model_path)
    if spec is None or spec.loader is None:
        raise ImportError("Nepodařilo se načíst modelové jádro.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@st.cache_resource
def get_model_module():
    return load_model_module()


@st.cache_data(show_spinner=False)
def run_model(
    initial_time: float,
    final_time: float,
    dt: float,
    params: dict[str, float],
    seed_oblacnost: int,
    seed_vitr: int,
    seed_sum: int,
) -> pd.DataFrame:
    module = get_model_module()
    return module.simulate_sfd_energetika(
        initial_time=initial_time,
        final_time=final_time,
        dt=dt,
        mdl_path=None,
        model_params=params,
        seed_oblacnost=seed_oblacnost,
        seed_vitr=seed_vitr,
        seed_sum=seed_sum,
    )


def build_energy_share(df: pd.DataFrame, dt: float) -> pd.DataFrame:
    share_map = {
        "Uhlí": (df["aktualni_vyroba_uhli"].clip(lower=0) * dt).sum(),
        "Jádro": (df["vyroba_jadra"].clip(lower=0) * dt).sum(),
        "Plyn": (df["aktualni_vyroba_plynu"].clip(lower=0) * dt).sum(),
        "FVE": (df["vyroba_fve"].clip(lower=0) * dt).sum(),
        "Vítr": (df["vyroba_vetrne_energie"].clip(lower=0) * dt).sum(),
        "PVE turbínování": (df["turbinovani_pve"].clip(lower=0) * dt).sum(),
        "Baterie vybíjení": (df["vybijeni"].clip(lower=0) * dt).sum(),
        "Import": (df["import"].clip(lower=0) * dt).sum(),
    }

    result = pd.DataFrame(
        {
            "zdroj": list(share_map.keys()),
            "mwh": list(share_map.values()),
        }
    )
    return result[result["mwh"] > 0]


def padded_range(values: pd.Series, min_padding: float = 1.0) -> tuple[float, float]:
    vmin = float(values.min())
    vmax = float(values.max())
    span = vmax - vmin
    padding = max(min_padding, span * 0.12)
    return (vmin - padding, vmax + padding)


module = get_model_module()
defaults = module.get_default_params()

st.title("Energetická síť - SFD simulátor")
st.caption("Levé menu obsahuje vstupní parametry modelu. Vpravo najdeš grafy bilance, validace, energetického mixu a akumulace.")

left_col, right_col = st.columns([2, 8], gap="large")

with left_col:
    st.subheader("Menu")

    with st.expander("Čas simulace", expanded=True):
        initial_time = st.number_input("Počáteční čas [h]", min_value=0.0, max_value=48.0, value=1.0, step=1.0)
        final_time = st.number_input("Koncový čas [h]", min_value=24.0, max_value=720.0, value=168.0, step=24.0)
        dt = st.select_slider("Časový krok [h]", options=[0.03125, 0.0625, 0.125, 0.25], value=0.0625)

    with st.expander("Poptávka a cena", expanded=False):
        init_poptavka = st.slider("Počáteční poptávka [MW]", 1000, 10000, int(defaults["init_poptavka"]), 50)
        marginalni_naklady_uhli = st.slider(
            "Marginální náklady uhlí [EUR/MWh]", 10, 150, int(defaults["marginalni_naklady_uhli"]), 1
        )

    with st.expander("Výroba - zdroje", expanded=False):
        vyroba_jadra = st.slider("Výroba jádra [MW]", 0, 8000, int(defaults["vyroba_jadra"]), 50)
        max_kapacita_fve = st.slider("Maximální kapacita FVE [MW]", 0, 12000, int(defaults["max_kapacita_fve"]), 50)
        max_kapacita_vetrne = st.slider("Maximální kapacita větru [MW]", 0, 3000, int(defaults["max_kapacita_vetrne"]), 10)
        max_kapacita_uhli = st.slider("Maximální kapacita uhlí [MW]", 0, 10000, int(defaults["max_kapacita_uhli"]), 50)
        technicke_minimum_uhli = st.slider(
            "Technické minimum uhlí [MW]",
            0,
            int(max_kapacita_uhli),
            min(int(defaults["technicke_minimum_uhli"]), int(max_kapacita_uhli)),
            10,
        )
        doba_nabehu_uhli = st.slider("Doba náběhu uhlí [h]", 0.0, 12.0, float(defaults["doba_nabehu_uhli"]), 0.25)
        max_kapacita_plynu = st.slider("Maximální kapacita plynu [MW]", 0, 5000, int(defaults["max_kapacita_plynu"]), 10)
        doba_nabehu_plynu = st.slider("Doba náběhu plynu [h]", 0.0, 4.0, float(defaults["doba_nabehu_plynu"]), 0.05)

    with st.expander("Akumulace a síť", expanded=False):
        kapacita_baterie = st.slider("Kapacita baterie [MWh]", 0, 10000, int(defaults["kapacita_baterie"]), 50)
        max_vykon_baterie = st.slider("Maximální výkon baterie [MW]", 0, 3000, int(defaults["max_vykon_baterie"]), 10)
        kapacita_horni_nadrze = st.slider(
            "Kapacita horní nádrže [MWh]", 0, 15000, int(defaults["kapacita_horni_nadrze"]), 50
        )
        max_vykon_pve = st.slider("Maximální výkon PVE [MW]", 0, 4000, int(defaults["max_vykon_pve"]), 10)
        max_prenosova_kapacita = st.slider(
            "Maximální přenosová kapacita [MW]", 0, 7000, int(defaults["max_prenosova_kapacita"]), 50
        )
        zpozdeni_dispecinku = st.slider(
            "Zpoždění dispečinku [h]", 0.0, 2.0, float(defaults["zpozdeni_dispecinku"]), 0.05
        )

    with st.expander("Náhoda (seedy)", expanded=False):
        seed_oblacnost = st.number_input("Seed oblačnosti", min_value=0, max_value=9999, value=11, step=1)
        seed_vitr = st.number_input("Seed větru", min_value=0, max_value=9999, value=2, step=1)
        seed_sum = st.number_input("Seed šumu", min_value=0, max_value=9999, value=11, step=1)

params = {
    "marginalni_naklady_uhli": float(marginalni_naklady_uhli),
    "max_kapacita_uhli": float(max_kapacita_uhli),
    "technicke_minimum_uhli": float(technicke_minimum_uhli),
    "max_prenosova_kapacita": float(max_prenosova_kapacita),
    "zpozdeni_dispecinku": float(zpozdeni_dispecinku),
    "max_vykon_pve": float(max_vykon_pve),
    "doba_nabehu_plynu": float(doba_nabehu_plynu),
    "kapacita_baterie": float(kapacita_baterie),
    "max_vykon_baterie": float(max_vykon_baterie),
    "kapacita_horni_nadrze": float(kapacita_horni_nadrze),
    "max_kapacita_plynu": float(max_kapacita_plynu),
    "max_kapacita_fve": float(max_kapacita_fve),
    "max_kapacita_vetrne": float(max_kapacita_vetrne),
    "init_poptavka": float(init_poptavka),
    "doba_nabehu_uhli": float(doba_nabehu_uhli),
    "vyroba_jadra": float(vyroba_jadra),
}

with right_col:
    if final_time <= initial_time:
        st.error("Koncový čas musí být větší než počáteční čas.")
        st.stop()

    with st.spinner("Počítám simulaci..."):
        df = run_model(
            initial_time=float(initial_time),
            final_time=float(final_time),
            dt=float(dt),
            params=params,
            seed_oblacnost=int(seed_oblacnost),
            seed_vitr=int(seed_vitr),
            seed_sum=int(seed_sum),
        )

if "celkova_vyroba" not in df.columns:
    df["celkova_vyroba"] = (
        df["aktualni_vyroba_uhli"]
        + df["vyroba_fve"]
        + df["vyroba_jadra"]
        + df["vyroba_vetrne_energie"]
        + df["vybijeni"]
        - df["nabijeni"]
        + df["turbinovani_pve"]
        - df["cerpani_pve"]
        + df["aktualni_vyroba_plynu"]
        - df["omezovani_oze"]
    )

lookup_source = "interní lookup tabulky v Pythonu"

bilance_auto = padded_range(pd.concat([df["bilance_site"], df["vyzehlena_bilance_site"]]), min_padding=10.0)
validace_auto = padded_range(pd.concat([df["vyzehlena_bilance_site"], df["systemova_odchylka"]]), min_padding=10.0)
mix_auto = padded_range(
    pd.concat(
        [
            df["aktualni_vyroba_uhli"],
            df["vyroba_jadra"],
            df["aktualni_vyroba_plynu"],
            df["vyroba_fve"],
            df["vyroba_vetrne_energie"],
            df["import"],
        ]
    ),
    min_padding=20.0,
)
compare_auto = padded_range(pd.concat([df["poptavka_po_energii"], df["celkova_vyroba"]]), min_padding=20.0)
storage_auto = padded_range(pd.concat([df["energie_v_bateriich"], df["voda_v_horni_nadrzi"]]), min_padding=20.0)

with left_col:
    with st.expander("Nastavení os grafů (Y)", expanded=False):
        auto_y = st.toggle("Automaticky přizpůsobit osy Y podle dat", value=True)
        if auto_y:
            y_bilance = bilance_auto
            y_validace = validace_auto
            y_mix = mix_auto
            y_compare = compare_auto
            y_storage = storage_auto
        else:
            y_bilance = st.slider(
                "Bilance sítě [MW]",
                min_value=-12000.0,
                max_value=12000.0,
                value=(float(bilance_auto[0]), float(bilance_auto[1])),
                step=10.0,
            )
            y_validace = st.slider(
                "Validace (bilance vs referenční řada)",
                min_value=-12000.0,
                max_value=12000.0,
                value=(float(validace_auto[0]), float(validace_auto[1])),
                step=10.0,
            )
            y_mix = st.slider(
                "Energetický mix [MW]",
                min_value=-1000.0,
                max_value=20000.0,
                value=(float(mix_auto[0]), float(mix_auto[1])),
                step=20.0,
            )
            y_compare = st.slider(
                "Poptávka vs celková výroba [MW]",
                min_value=-1000.0,
                max_value=20000.0,
                value=(float(compare_auto[0]), float(compare_auto[1])),
                step=20.0,
            )
            y_storage = st.slider(
                "Akumulace [MWh]",
                min_value=-1000.0,
                max_value=25000.0,
                value=(float(storage_auto[0]), float(storage_auto[1])),
                step=20.0,
            )

chart_config = {
    "scrollZoom": True,
    "displaylogo": False,
    "modeBarButtonsToAdd": ["zoom2d", "pan2d", "select2d", "lasso2d", "resetScale2d"],
}

with right_col:
    st.caption("Tip: v grafech můžeš zoomovat kolečkem myši a tažením výběru, podobně jako v BI nástrojích.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Průměrná poptávka [MW]", f"{df['poptavka_po_energii'].mean():,.0f}")
    c2.metric("Průměrná bilance [MW]", f"{df['bilance_site'].mean():,.1f}")
    c3.metric("Nejhorší bilance [MW]", f"{df['bilance_site'].min():,.1f}")
    c4.metric("Kritický deficit [h]", f"{df['kriticky_deficit_hodiny'].iloc[-1]:,.2f}")

    st.subheader("Bilance sítě")
    fig_balance = go.Figure()
    fig_balance.add_trace(
        go.Scatter(x=df["time"], y=df["bilance_site"], mode="lines", name="Bilance sítě", line=dict(width=2))
    )
    fig_balance.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["vyzehlena_bilance_site"],
            mode="lines",
            name="Vyhlazená bilance",
            line=dict(width=2, dash="dash"),
        )
    )
    fig_balance.add_hline(y=0, line_width=1, line_dash="dot")
    fig_balance.add_hline(y=-500, line_width=1, line_dash="dot", line_color="red")
    fig_balance.update_layout(height=340, legend_title_text="", **PLOTLY_DARK_LAYOUT)
    fig_balance.update_xaxes(title="Čas [h]")
    fig_balance.update_yaxes(title="MW", range=[float(y_bilance[0]), float(y_bilance[1])])
    st.plotly_chart(fig_balance, use_container_width=True, config=chart_config)

    st.subheader("Validace: bilance modelu vs referenční data")
    st.caption(f"Referenční řada pochází z {lookup_source}.")
    fig_validation = go.Figure()
    fig_validation.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["vyzehlena_bilance_site"],
            mode="lines",
            name="Vyhlazená bilance modelu",
            line=dict(width=2),
        )
    )
    fig_validation.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["systemova_odchylka"],
            mode="lines",
            name="Referenční odchylka",
            line=dict(width=2, dash="dot"),
        )
    )
    fig_validation.add_hline(y=0, line_width=1, line_dash="dot")
    fig_validation.update_layout(height=320, legend_title_text="", **PLOTLY_DARK_LAYOUT)
    fig_validation.update_xaxes(title="Čas [h]")
    fig_validation.update_yaxes(title="MW / MWh", range=[float(y_validace[0]), float(y_validace[1])])
    st.plotly_chart(fig_validation, use_container_width=True, config=chart_config)

    corr = df["vyzehlena_bilance_site"].corr(df["systemova_odchylka"])
    st.caption(f"Korelace (vyhlazená bilance vs referenční odchylka): {corr:.3f}")

    st.subheader("Skladba energetického mixu v čase")
    mix_cols = {
        "aktualni_vyroba_uhli": "Uhlí",
        "vyroba_jadra": "Jádro",
        "aktualni_vyroba_plynu": "Plyn",
        "vyroba_fve": "FVE",
        "vyroba_vetrne_energie": "Vítr",
        "import": "Import",
    }
    mix_df = df[["time", *mix_cols.keys()]].rename(columns=mix_cols)
    mix_long = mix_df.melt(id_vars="time", var_name="zdroj", value_name="výkon")

    fig_mix = px.line(
        mix_long,
        x="time",
        y="výkon",
        color="zdroj",
        labels={"time": "Čas [h]", "výkon": "MW", "zdroj": "Zdroj"},
        template="plotly_dark",
    )
    fig_mix.update_layout(height=380, legend_title_text="", **PLOTLY_DARK_LAYOUT)
    fig_mix.update_yaxes(range=[float(y_mix[0]), float(y_mix[1])])
    st.plotly_chart(fig_mix, use_container_width=True, config=chart_config)

    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.subheader("Poptávka vs celková výroba")
        compare_df = df[["time", "poptavka_po_energii", "celkova_vyroba"]].rename(
            columns={"poptavka_po_energii": "Poptávka", "celkova_vyroba": "Celková výroba"}
        )
        comp_long = compare_df.melt(id_vars="time", var_name="řada", value_name="mw")
        fig_compare = px.line(comp_long, x="time", y="mw", color="řada", template="plotly_dark")
        fig_compare.update_layout(height=330, legend_title_text="", **PLOTLY_DARK_LAYOUT)
        fig_compare.update_xaxes(title="Čas [h]")
        fig_compare.update_yaxes(title="MW", range=[float(y_compare[0]), float(y_compare[1])])
        st.plotly_chart(fig_compare, use_container_width=True, config=chart_config)

    with col_b:
        st.subheader("Podíly výroby")
        shares = build_energy_share(df, dt=float(dt))
        fig_pie = px.pie(shares, names="zdroj", values="mwh", hole=0.45, template="plotly_dark")
        fig_pie.update_layout(height=330, **PLOTLY_DARK_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True, config=chart_config)

    st.subheader("Stavy akumulace")
    storage_df = df[["time", "energie_v_bateriich", "voda_v_horni_nadrzi"]].rename(
        columns={
            "energie_v_bateriich": "Energie v bateriích [MWh]",
            "voda_v_horni_nadrzi": "Voda v horní nádrži [MWh]",
        }
    )
    storage_long = storage_df.melt(id_vars="time", var_name="zásobník", value_name="stav")
    fig_storage = px.line(storage_long, x="time", y="stav", color="zásobník", template="plotly_dark")
    fig_storage.update_layout(height=320, legend_title_text="", **PLOTLY_DARK_LAYOUT)
    fig_storage.update_xaxes(title="Čas [h]")
    fig_storage.update_yaxes(title="MWh", range=[float(y_storage[0]), float(y_storage[1])])
    st.plotly_chart(fig_storage, use_container_width=True, config=chart_config)

