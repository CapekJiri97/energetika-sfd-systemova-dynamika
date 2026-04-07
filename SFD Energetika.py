from __future__ import annotations

import base64
import json
import math
import re
import zlib
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_PARAMS: dict[str, float] = {
    "marginalni_naklady_uhli": 40.0,
    "max_kapacita_uhli": 5000.0,
    "technicke_minimum_uhli": 1000.0,
    "max_prenosova_kapacita": 2500.0,
    "zpozdeni_dispecinku": 0.25,
    "max_vykon_pve": 1170.0,
    "doba_nabehu_plynu": 0.25,
    "kapacita_baterie": 1500.0,
    "max_vykon_baterie": 500.0,
    "kapacita_horni_nadrze": 3500.0,
    "max_kapacita_plynu": 1000.0,
    "max_kapacita_fve": 4500.0,
    "max_kapacita_vetrne": 350.0,
    "init_poptavka": 5000.0,
    "doba_nabehu_uhli": 4.0,
    "vyroba_jadra": 4000.0,
}

_EMBEDDED_LOOKUP_B64 = "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"


def get_default_params() -> dict[str, float]:
    return dict(DEFAULT_PARAMS)


def load_lookup_table_embedded() -> tuple[np.ndarray, np.ndarray]:
    compressed = base64.b64decode(_EMBEDDED_LOOKUP_B64.encode("ascii"))
    raw_json = zlib.decompress(compressed).decode("utf-8")
    points = json.loads(raw_json)

    arr = np.array(points, dtype=float)
    xs = arr[:, 0]
    ys = arr[:, 1]
    return xs, ys


def modulo(value: float, base: float) -> float:
    return value - base * math.floor(value / base)


def random_normal_clipped(
    rng: np.random.Generator,
    low: float,
    high: float,
    mean: float,
    std: float,
) -> float:
    return float(np.clip(rng.normal(mean, std), low, high))


def smooth_step(current: float, target: float, tau: float, dt: float) -> float:
    if tau <= 0:
        return target
    return current + dt * (target - current) / tau


class Smooth3:
    def __init__(self, initial_value: float) -> None:
        self.s1 = initial_value
        self.s2 = initial_value
        self.s3 = initial_value

    @property
    def output(self) -> float:
        return self.s3

    def step(self, target: float, delay_time: float, dt: float) -> None:
        if delay_time <= 0:
            self.s1 = target
            self.s2 = target
            self.s3 = target
            return

        k = 3.0 / delay_time
        ds1 = k * (target - self.s1)
        ds2 = k * (self.s1 - self.s2)
        ds3 = k * (self.s2 - self.s3)

        self.s1 += dt * ds1
        self.s2 += dt * ds2
        self.s3 += dt * ds3


def load_lookup_table_from_mdl(mdl_path: Path) -> tuple[np.ndarray, np.ndarray]:
    text = mdl_path.read_text(encoding="utf-8")
    match = re.search(r"Tabulka\((.*?)\)\s*~", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Nepodarilo se nacist lookup tabulku z .mdl souboru.")

    block = match.group(1)
    block = re.sub(r"\[\([^\]]+\)-\([^\]]+\)\],?", "", block)
    block = block.replace("\\", "")
    block = re.sub(r"([,(])\s*-\s*(\d)", r"\1-\2", block)

    pairs = re.findall(r"\(([-+]?\d+(?:\.\d+)?),\s*([-+]?\d+(?:\.\d+)?)\s*\)", block)
    if len(pairs) < 2:
        raise ValueError("Lookup tabulka neobsahuje dostatek bodu.")

    xs = np.array([float(x) for x, _ in pairs], dtype=float)
    ys = np.array([float(y) for _, y in pairs], dtype=float)

    order = np.argsort(xs)
    xs = xs[order]
    ys = ys[order]
    return xs, ys


def lookup_periodic(x: float, xs: np.ndarray, ys: np.ndarray, period: float = 120.0) -> float:
    x_mod = modulo(x, period)

    if x_mod <= xs[0]:
        return float(ys[0])

    if x_mod >= xs[-1]:
        x0, y0 = xs[-1], ys[-1]
        x1, y1 = xs[0] + period, ys[0]
        ratio = (x_mod - x0) / (x1 - x0)
        return float(y0 + ratio * (y1 - y0))

    return float(np.interp(x_mod, xs, ys))


def resolve_step_params(
    base_params: dict[str, float],
    time: float,
    param_overrides: list[dict[str, object]] | None,
) -> dict[str, float]:
    active = dict(base_params)
    if not param_overrides:
        return active

    for rule in param_overrides:
        start_raw = rule.get("start", -1e30)
        end_raw = rule.get("end", 1e30)
        start = float(start_raw) if isinstance(start_raw, (int, float, str)) else -1e30
        end = float(end_raw) if isinstance(end_raw, (int, float, str)) else 1e30
        if not (start <= time <= end):
            continue

        updates = rule.get("params", {})
        if not isinstance(updates, dict):
            continue

        for key, value in updates.items():
            if key in active:
                active[key] = float(value)

    return active


def simulate_sfd_energetika(
    initial_time: float = 1.0,
    final_time: float = 168.0,
    dt: float = 0.0625,
    mdl_path: str | Path | None = None,
    model_params: dict[str, float] | None = None,
    param_overrides: list[dict[str, object]] | None = None,
    seed_oblacnost: int = 11,
    seed_vitr: int = 2,
    seed_sum: int = 11,
) -> pd.DataFrame:
    params = get_default_params()
    if model_params:
        params.update(model_params)

    base_params = dict(params)
    sorted_overrides = None
    if param_overrides:
        def _start_key(rule: dict[str, object]) -> float:
            raw = rule.get("start", 0.0)
            return float(raw) if isinstance(raw, (int, float, str)) else 0.0

        sorted_overrides = sorted(param_overrides, key=_start_key)

    params = resolve_step_params(base_params, initial_time, sorted_overrides)

    if mdl_path is None:
        lookup_x, lookup_y = load_lookup_table_embedded()
    else:
        lookup_x, lookup_y = load_lookup_table_from_mdl(Path(mdl_path))

    rng_oblacnost = np.random.default_rng(seed_oblacnost)
    rng_vitr = np.random.default_rng(seed_vitr)
    rng_sum = np.random.default_rng(seed_sum)

    odlozena_prace = 0.0
    energie_v_bateriich = params["kapacita_baterie"]
    voda_v_horni_nadrzi = params["kapacita_horni_nadrze"] * 0.5
    kriticky_deficit_hodiny = 0.0

    vnimana_cena = 60.0

    t0 = initial_time
    hodina_dne_4_t0 = modulo(t0 + 4.0, 24.0)
    sum_signal = random_normal_clipped(rng_sum, 0.8, 1.2, 1.0, 0.06)
    sum_vetru = float(rng_vitr.uniform(0.0, 1.0))
    vyroba_vetrne_smooth = Smooth3(sum_vetru)

    ocek_poptavka_4_t0 = (
        params["init_poptavka"]
        + 1200.0 * math.exp(-((hodina_dne_4_t0 - 8.0) ** 2) / 12.0)
        + 1800.0 * math.exp(-((hodina_dne_4_t0 - 19.0) ** 2) / 12.0)
    )
    ocek_vyroba_fve_4_t0 = (
        params["max_kapacita_fve"]
        * float(rng_oblacnost.uniform(0.8, 1.1))
        * max(0.0, math.exp(-((hodina_dne_4_t0 - 12.0) ** 2) / 6.0))
    )
    ocek_cista_potreba_4_t0 = (
        ocek_poptavka_4_t0 - params["vyroba_jadra"] - ocek_vyroba_fve_4_t0 - params["max_kapacita_vetrne"] * vyroba_vetrne_smooth.output
    )
    cilovy_vykon_uhli_t0 = (
        min(
            params["max_kapacita_uhli"],
            max(params["technicke_minimum_uhli"], ocek_cista_potreba_4_t0),
        )
        if vnimana_cena > params["marginalni_naklady_uhli"]
        else params["technicke_minimum_uhli"]
    )

    aktualni_uhli_smooth = Smooth3(cilovy_vykon_uhli_t0)

    # Initial placeholders are aligned to Vensim default behavior for SMOOTH.
    aktualni_vyroba_plynu = 0.0
    vyzehlena_bilance_site = 0.0
    vnimana_bilance_po_baterii = 0.0

    records: list[dict[str, float]] = []

    n_steps = int(round((final_time - initial_time) / dt)) + 1
    for step_idx in range(n_steps):
        time = initial_time + step_idx * dt
        params = resolve_step_params(base_params, time, sorted_overrides)

        if abs(modulo(time, 0.5)) < 1e-12:
            sum_signal = random_normal_clipped(rng_sum, 0.8, 1.2, 1.0, 0.06)

        faktor_oblacnosti = float(rng_oblacnost.uniform(0.8, 1.1))
        sum_vetru = float(rng_vitr.uniform(0.0, 1.0))

        hodina_dne = modulo(time, 24.0)
        hodina_dne_4 = modulo(time + 4.0, 24.0)

        zakladni_poptavka = (
            params["init_poptavka"]
            + 1200.0 * math.exp(-((hodina_dne - 8.0) ** 2) / 12.0)
            + 1800.0 * math.exp(-((hodina_dne - 19.0) ** 2) / 12.0)
        ) * sum_signal

        cenovy_tlumic = (60.0 / max(1.0, vnimana_cena)) ** 0.05
        omezeni_spotreby = max(0.0, zakladni_poptavka - (zakladni_poptavka * cenovy_tlumic))
        dohaneni_spotreby = (odlozena_prace / 2.0) if (vnimana_cena < 50.0) else 0.0
        poptavka_po_energii = (zakladni_poptavka * cenovy_tlumic) + dohaneni_spotreby

        vyroba_fve = (
            params["max_kapacita_fve"]
            * faktor_oblacnosti
            * max(0.0, math.exp(-((hodina_dne - 12.0) ** 2) / 6.0))
        )
        vyroba_vetrne_energie = params["max_kapacita_vetrne"] * vyroba_vetrne_smooth.output

        ocek_poptavka_4 = (
            params["init_poptavka"]
            + 1200.0 * math.exp(-((hodina_dne_4 - 8.0) ** 2) / 12.0)
            + 1800.0 * math.exp(-((hodina_dne_4 - 19.0) ** 2) / 12.0)
        )
        ocek_vyroba_fve_4 = (
            params["max_kapacita_fve"]
            * faktor_oblacnosti
            * max(0.0, math.exp(-((hodina_dne_4 - 12.0) ** 2) / 6.0))
        )
        ocek_cista_potreba_4 = (
            ocek_poptavka_4 - params["vyroba_jadra"] - ocek_vyroba_fve_4 - vyroba_vetrne_energie
        )

        cilovy_vykon_uhli = (
            min(
                params["max_kapacita_uhli"],
                max(params["technicke_minimum_uhli"], ocek_cista_potreba_4),
            )
            if vnimana_cena > params["marginalni_naklady_uhli"]
            else params["technicke_minimum_uhli"]
        )

        aktualni_vyroba_uhli = aktualni_uhli_smooth.output
        zmena_vykonu_uhli = (
            (cilovy_vykon_uhli - aktualni_vyroba_uhli) / params["doba_nabehu_uhli"]
            if params["doba_nabehu_uhli"] > 0
            else 0.0
        )

        bilance_pred_baterii = (
            aktualni_vyroba_uhli
            + vyroba_fve
            + params["vyroba_jadra"]
            + vyroba_vetrne_energie
            - poptavka_po_energii
        )

        potencialni_nabijeni = (
            min(params["max_vykon_baterie"], bilance_pred_baterii)
            if bilance_pred_baterii > 0.0
            else 0.0
        )
        potencialni_vybijeni = (
            min(params["max_vykon_baterie"], abs(bilance_pred_baterii))
            if bilance_pred_baterii < 0.0
            else 0.0
        )

        minimalni_energie_v_bateriich = params["kapacita_baterie"] * 0.1
        maximalni_energie_v_bateriich = params["kapacita_baterie"] * 0.9

        nabijeni = (
            potencialni_nabijeni
            if energie_v_bateriich < maximalni_energie_v_bateriich
            else 0.0
        )
        vybijeni = (
            potencialni_vybijeni
            if energie_v_bateriich > minimalni_energie_v_bateriich
            else 0.0
        )

        bilance_po_baterii = bilance_pred_baterii + vybijeni - nabijeni

        potencialni_cerpani = (
            min(params["max_vykon_pve"], vnimana_bilance_po_baterii)
            if vnimana_bilance_po_baterii > 0.0
            else 0.0
        )
        potencialni_turbinovani = (
            min(params["max_vykon_pve"], abs(vnimana_bilance_po_baterii))
            if vnimana_bilance_po_baterii < 0.0
            else 0.0
        )

        cerpani_pve = (
            potencialni_cerpani
            if voda_v_horni_nadrzi < params["kapacita_horni_nadrze"]
            else 0.0
        )
        turbinovani_pve = potencialni_turbinovani if voda_v_horni_nadrzi > 0.0 else 0.0

        bilance_po_pve = bilance_po_baterii + turbinovani_pve - cerpani_pve

        cilovy_vykon_plynu = (
            min(params["max_kapacita_plynu"], abs(bilance_po_pve + 50.0))
            if bilance_po_pve < -50.0
            else 0.0
        )

        bilance_po_plynu = bilance_po_pve + aktualni_vyroba_plynu
        import_mw = (
            min(params["max_prenosova_kapacita"], abs(bilance_po_plynu + 50.0))
            if bilance_po_plynu < -50.0
            else 0.0
        )
        export_mw = (
            min(params["max_prenosova_kapacita"], bilance_po_plynu - 50.0)
            if bilance_po_plynu > 50.0
            else 0.0
        )

        omezovani_oze = max(0.0, (bilance_po_plynu - export_mw) - 50.0)

        celkova_vyroba = (
            aktualni_vyroba_uhli
            + vyroba_fve
            + params["vyroba_jadra"]
            + vyroba_vetrne_energie
            + vybijeni
            - nabijeni
            + turbinovani_pve
            - cerpani_pve
            + aktualni_vyroba_plynu
            - omezovani_oze
        )

        bilance_site = (celkova_vyroba + import_mw) - (poptavka_po_energii + export_mw)

        zbytkove_zatizeni = (
            poptavka_po_energii - vyroba_fve - vyroba_vetrne_energie - params["vyroba_jadra"]
        )
        okamzita_cena = max(-10.0, 20.0 + (zbytkove_zatizeni * 0.03))

        if step_idx == 0:
            vnimana_bilance_po_baterii = bilance_po_baterii
            aktualni_vyroba_plynu = cilovy_vykon_plynu
            bilance_po_plynu = bilance_po_pve + aktualni_vyroba_plynu
            import_mw = (
                min(params["max_prenosova_kapacita"], abs(bilance_po_plynu + 50.0))
                if bilance_po_plynu < -50.0
                else 0.0
            )
            export_mw = (
                min(params["max_prenosova_kapacita"], bilance_po_plynu - 50.0)
                if bilance_po_plynu > 50.0
                else 0.0
            )
            omezovani_oze = max(0.0, (bilance_po_plynu - export_mw) - 50.0)
            celkova_vyroba = (
                aktualni_vyroba_uhli
                + vyroba_fve
                + params["vyroba_jadra"]
                + vyroba_vetrne_energie
                + vybijeni
                - nabijeni
                + turbinovani_pve
                - cerpani_pve
                + aktualni_vyroba_plynu
                - omezovani_oze
            )
            bilance_site = (celkova_vyroba + import_mw) - (poptavka_po_energii + export_mw)
            vyzehlena_bilance_site = bilance_site

        riziko_blackoutu = 1.0 if vyzehlena_bilance_site < -500.0 else 0.0
        systemova_odchylka = lookup_periodic(time, lookup_x, lookup_y, period=120.0)

        records.append(
            {
                "time": time,
                "poptavka_po_energii": poptavka_po_energii,
                "zakladni_poptavka": zakladni_poptavka,
                "cenovy_tlumic": cenovy_tlumic,
                "vnimana_cena_elektriny": vnimana_cena,
                "okamzita_cena": okamzita_cena,
                "aktualni_vyroba_uhli": aktualni_vyroba_uhli,
                "cilovy_vykon_uhli": cilovy_vykon_uhli,
                "zmena_vykonu_uhli": zmena_vykonu_uhli,
                "vyroba_fve": vyroba_fve,
                "vyroba_vetrne_energie": vyroba_vetrne_energie,
                "vyroba_jadra": params["vyroba_jadra"],
                "aktualni_vyroba_plynu": aktualni_vyroba_plynu,
                "cilovy_vykon_plynu": cilovy_vykon_plynu,
                "bilance_pred_baterii": bilance_pred_baterii,
                "bilance_po_baterii": bilance_po_baterii,
                "vnimana_bilance_po_baterii": vnimana_bilance_po_baterii,
                "bilance_po_pve": bilance_po_pve,
                "bilance_po_plynu": bilance_po_plynu,
                "celkova_vyroba": celkova_vyroba,
                "bilance_site": bilance_site,
                "vyzehlena_bilance_site": vyzehlena_bilance_site,
                "riziko_blackoutu": riziko_blackoutu,
                "import": import_mw,
                "export": export_mw,
                "omezovani_oze": omezovani_oze,
                "nabijeni": nabijeni,
                "vybijeni": vybijeni,
                "cerpani_pve": cerpani_pve,
                "turbinovani_pve": turbinovani_pve,
                "energie_v_bateriich": energie_v_bateriich,
                "voda_v_horni_nadrzi": voda_v_horni_nadrzi,
                "odlozena_prace": odlozena_prace,
                "dohaneni_spotreby": dohaneni_spotreby,
                "omezeni_spotreby": omezeni_spotreby,
                "sum": sum_signal,
                "sum_vetru": sum_vetru,
                "faktor_oblacnosti": faktor_oblacnosti,
                "zbytkove_zatizeni": zbytkove_zatizeni,
                "systemova_odchylka": systemova_odchylka,
                "kriticky_deficit_hodiny": kriticky_deficit_hodiny,
            }
        )

        odlozena_prace += dt * (omezeni_spotreby - dohaneni_spotreby)
        energie_v_bateriich += dt * (nabijeni - vybijeni)
        voda_v_horni_nadrzi += dt * (cerpani_pve - turbinovani_pve)
        kriticky_deficit_hodiny += dt * riziko_blackoutu

        vnimana_cena = smooth_step(vnimana_cena, okamzita_cena, 1.0, dt)
        vnimana_bilance_po_baterii = smooth_step(
            vnimana_bilance_po_baterii,
            bilance_po_baterii,
            params["zpozdeni_dispecinku"],
            dt,
        )
        aktualni_vyroba_plynu = smooth_step(
            aktualni_vyroba_plynu,
            cilovy_vykon_plynu,
            params["doba_nabehu_plynu"],
            dt,
        )
        vyzehlena_bilance_site = smooth_step(vyzehlena_bilance_site, bilance_site, 0.25, dt)

        aktualni_uhli_smooth.step(cilovy_vykon_uhli, params["doba_nabehu_uhli"], dt)
        vyroba_vetrne_smooth.step(sum_vetru, 5.0, dt)

    return pd.DataFrame.from_records(records)


if __name__ == "__main__":
    df = simulate_sfd_energetika()
    print(df[["time", "poptavka_po_energii", "bilance_site", "riziko_blackoutu"]].head())
    print(df[["time", "poptavka_po_energii", "bilance_site", "riziko_blackoutu"]].tail())
