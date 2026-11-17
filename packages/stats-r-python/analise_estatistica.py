#!/usr/bin/env python3
"""
RespiraCidadao - FIAP GS 2026.2 (09 Statistical Computing with R & Python)
Analise estatistica completa sobre base real UCI Air Quality (sem dados sinteticos).
Gera base limpa (.csv), graficos (.png) e resumo estruturado (artifacts/stats_summary.json).
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT_DIR / "data" / "raw" / "AirQualityUCI.csv"
PROCESSED_CSV = ROOT_DIR / "data" / "processed" / "air_quality_clean.csv"
PKG_DIR = Path(__file__).resolve().parent
LOCAL_CLEAN_CSV = PKG_DIR / "air_quality_clean.csv"
CHARTS_DIR = PKG_DIR / "charts"
ARTIFACTS_DIR = PKG_DIR / "artifacts"

CORE_COLS = [
    "CO(GT)",
    "PT08.S1(CO)",
    "C6H6(GT)",
    "PT08.S2(NMHC)",
    "NOx(GT)",
    "PT08.S3(NOx)",
    "NO2(GT)",
    "PT08.S4(NO2)",
    "PT08.S5(O3)",
    "T",
    "RH",
    "AH",
]

plt.rcParams.update({
    "figure.facecolor": "#0f0f12",
    "axes.facecolor": "#1c1c21",
    "axes.edgecolor": "#3a3a45",
    "axes.labelcolor": "#e5e9f0",
    "text.color": "#e5e9f0",
    "xtick.color": "#acc1cc",
    "ytick.color": "#acc1cc",
    "grid.color": "#2a2a33",
    "font.size": 10,
})

FIAP_MAGENTA = "#ED145B"
FIAP_CYAN = "#64D2FF"
FIAP_GREEN = "#00C365"
FIAP_YELLOW = "#FFB700"


def classify_event_prob(p: float) -> str:
    if p <= 0.05:
        return "Evento muito raro / improvável"
    if p < 0.45:
        return "Evento pouco provável"
    if p <= 0.55:
        return "Evento equiprovável (50/50 sob simetria normal)"
    if p < 0.90:
        return "Evento provável / frequente"
    return "Evento altamente provável"


def load_and_clean() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV, sep=";", decimal=",")
    df = df.dropna(axis=1, how="all").dropna(how="all")
    for c in [col for col in df.columns if col not in ("Date", "Time")]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.replace(-200, np.nan)
    df_clean = df[["Date", "Time"] + CORE_COLS].dropna().reset_index(drop=True)

    # Classificacao de risco respiratorio baseada em CO(GT) (mg/m3):
    # < 1.5 normal | 1.5..2.99 atencao | >= 3.0 critico
    df_clean["nivel_risco_id"] = np.select(
        [df_clean["CO(GT)"] < 1.5, df_clean["CO(GT)"] < 3.0],
        [0, 1],
        default=2,
    )
    risk_map = {0: "normal", 1: "atencao", 2: "critico"}
    df_clean["nivel_risco"] = df_clean["nivel_risco_id"].map(risk_map)
    df_clean["alerta_critico"] = (df_clean["CO(GT)"] >= 3.0).astype(int)

    PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(PROCESSED_CSV, index=False)
    df_clean.to_csv(LOCAL_CLEAN_CSV, index=False)
    return df_clean


def main():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_and_clean()
    n_total = len(df)
    print(f"[01] Base real limpa carregada: {n_total} registros completos (UCI Air Quality).")

    # ------------------------------------------------------------------ 02 Normal
    co = df["CO(GT)"].to_numpy()
    co_mean = float(np.mean(co))
    co_std = float(np.std(co, ddof=1))
    co_median = float(np.median(co))

    p_lt_mean = float(stats.norm.cdf(co_mean, loc=co_mean, scale=co_std))
    p_gt_median = float(stats.norm.sf(co_median, loc=co_mean, scale=co_std))

    # Grafico da distribuicao Normal (Item 02)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    xs = np.linspace(max(-1.0, co_mean - 3.5 * co_std), co_mean + 3.5 * co_std, 400)
    ys = stats.norm.pdf(xs, loc=co_mean, scale=co_std)
    ax.hist(co, bins=40, density=True, alpha=0.35, color=FIAP_CYAN, label="Distribuição empírica CO(GT)")
    ax.plot(xs, ys, color=FIAP_MAGENTA, linewidth=2.2, label=f"Normal teórica N({co_mean:.2f}, {co_std:.2f}²)")
    ax.axvline(co_mean, color=FIAP_YELLOW, linestyle="--", linewidth=1.8, label=f"Média = {co_mean:.2f} mg/m³")
    ax.axvline(co_median, color=FIAP_GREEN, linestyle=":", linewidth=2.0, label=f"Mediana = {co_median:.2f} mg/m³")
    ax.set_title("02. Distribuição Normal de Probabilidade: CO(GT) [mg/m³]", fontweight="bold")
    ax.set_xlabel("Concentração de CO(GT) [mg/m³]")
    ax.set_ylabel("Densidade de Probabilidade")
    ax.grid(True, alpha=0.35)
    ax.legend(frameon=True, facecolor="#15151a", edgecolor="#2a2a33")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "02_distribuicao_normal_co.png", dpi=160)
    plt.close(fig)

    # ------------------------------------------------------------------ 03 Testes de Hipotese
    pop_std = float(np.std(co, ddof=0))

    # 3a) H1: mu_amostral < mu_pop, alpha = 6%, n = 20
    sample_a = df["CO(GT)"].sample(n=20, random_state=42).to_numpy()
    mean_a = float(np.mean(sample_a))
    se_a = pop_std / np.sqrt(20)
    z_a = float((mean_a - co_mean) / se_a)
    z_crit_a = float(stats.norm.ppf(0.06))
    p_val_a = float(stats.norm.cdf(z_a))
    rejeita_a = bool(p_val_a < 0.06)

    # 3b) H1: mu_amostral > mu_pop, alpha = 9%, n = 25
    sample_b = df["CO(GT)"].sample(n=25, random_state=108).to_numpy()
    mean_b = float(np.mean(sample_b))
    se_b = pop_std / np.sqrt(25)
    z_b = float((mean_b - co_mean) / se_b)
    z_crit_b = float(stats.norm.ppf(1.0 - 0.09))
    p_val_b = float(stats.norm.sf(z_b))
    rejeita_b = bool(p_val_b < 0.09)

    # ------------------------------------------------------------------ 04 Bivariada & Reg Simples
    x_s1 = df["PT08.S1(CO)"].to_numpy()
    y_co = df["CO(GT)"].to_numpy()
    cov_xy = float(np.cov(x_s1, y_co, ddof=1)[0, 1])
    pearson_r, pearson_p = stats.pearsonr(x_s1, y_co)
    pearson_r = float(pearson_r)
    pearson_p = float(pearson_p)

    X_simple = sm.add_constant(x_s1)
    ols_simple = sm.OLS(y_co, X_simple).fit()
    b0_s, b1_s = float(ols_simple.params[0]), float(ols_simple.params[1])
    r2_simple = float(ols_simple.rsquared)
    f_stat_simple = float(ols_simple.fvalue)
    f_pval_simple = float(ols_simple.f_pvalue)
    exemplo_s1 = 1350.0
    prev_simple = float(b0_s + b1_s * exemplo_s1)

    # 4a + 4d) Scatter + Reta
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.scatter(x_s1, y_co, alpha=0.22, s=14, color=FIAP_CYAN, label="Leituras reais (n = 6.941)")
    x_line = np.linspace(x_s1.min(), x_s1.max(), 200)
    y_line = b0_s + b1_s * x_line
    ax.plot(x_line, y_line, color=FIAP_MAGENTA, linewidth=2.4,
            label=f"ŷ = {b0_s:.4f} + {b1_s:.5f}·X (R² = {r2_simple:.4f})")
    ax.scatter([exemplo_s1], [prev_simple], color=FIAP_YELLOW, s=90, zorder=5,
               label=f"Previsão (X={exemplo_s1:.0f}) -> {prev_simple:.2f} mg/m³")
    ax.set_title("04. Dispersão e Regressão Linear Simples: Sensor PT08.S1(CO) vs CO(GT)", fontweight="bold")
    ax.set_xlabel("Resposta do Sensor Óxido Metálico PT08.S1(CO)")
    ax.set_ylabel("Concentração de Referência CO(GT) [mg/m³]")
    ax.grid(True, alpha=0.35)
    ax.legend(frameon=True, facecolor="#15151a", edgecolor="#2a2a33")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "04_dispersao_regressao_simples.png", dpi=160)
    plt.close(fig)

    # 4c) Grafico de Correlacao Linear Bivariada (valores medios por decil de X)
    df_tmp = pd.DataFrame({"PT08_S1": x_s1, "CO_GT": y_co})
    df_tmp["decil"] = pd.qcut(df_tmp["PT08_S1"], 10, labels=False) + 1
    decis = df_tmp.groupby("decil", as_index=False).mean()
    fig, ax = plt.subplots(figsize=(8.2, 4.5))
    sns.regplot(data=decis, x="PT08_S1", y="CO_GT", ax=ax, color=FIAP_MAGENTA,
                scatter_kws={"s": 70, "color": FIAP_CYAN}, line_kws={"linewidth": 2.2})
    ax.set_title(f"04c. Correlação Linear Bivariada por Decis (Pearson r = {pearson_r:.4f})", fontweight="bold")
    ax.set_xlabel("Média por Decil de PT08.S1(CO)")
    ax.set_ylabel("Média de CO(GT) [mg/m³]")
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "04_correlacao_bivariada.png", dpi=160)
    plt.close(fig)

    # ------------------------------------------------------------------ 05 Multivariada & Reg Multipla
    multi_features = ["PT08.S1(CO)", "C6H6(GT)", "NO2(GT)", "T"]
    multi_cols = ["CO(GT)"] + multi_features
    df_multi = df[multi_cols]
    cov_matrix = df_multi.cov().round(4)
    corr_matrix = df_multi.corr(method="pearson").round(4)

    # 5a) Dispersao multivariada (cada preditor vs CO(GT))
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.0))
    for ax, feat, col_hex in zip(axes.ravel(), multi_features, [FIAP_CYAN, FIAP_MAGENTA, FIAP_YELLOW, FIAP_GREEN]):
        ax.scatter(df[feat], df["CO(GT)"], alpha=0.18, s=12, color=col_hex)
        m, b = np.polyfit(df[feat], df["CO(GT)"], 1)
        xs_f = np.linspace(df[feat].min(), df[feat].max(), 100)
        ax.plot(xs_f, m * xs_f + b, color="#ffffff", linewidth=1.6, linestyle="--")
        r_f = corr_matrix.loc["CO(GT)", feat]
        ax.set_title(f"{feat} vs CO(GT) (r = {r_f:.3f})", fontweight="bold")
        ax.set_xlabel(feat)
        ax.set_ylabel("CO(GT) [mg/m³]")
        ax.grid(True, alpha=0.3)
    fig.suptitle("05a. Análise de Dispersão Multivariada em Relação ao CO(GT)", fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "05_dispersao_multivariada.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # 5c) Heatmap da Matriz de Correlacao
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    sns.heatmap(corr_matrix, annot=True, fmt=".3f", cmap="RdPu", vmin=-1, vmax=1,
                linewidths=0.6, linecolor="#0f0f12", ax=ax)
    ax.set_title("05c. Matriz de Correlação Linear de Pearson (Multivariada)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "05_matriz_correlacao.png", dpi=160)
    plt.close(fig)

    X_multi = sm.add_constant(df[multi_features])
    ols_multi = sm.OLS(df["CO(GT)"], X_multi).fit()
    multi_params = {k: float(v) for k, v in ols_multi.params.items()}
    r2_multi = float(ols_multi.rsquared)
    r2_adj_multi = float(ols_multi.rsquared_adj)
    f_stat_multi = float(ols_multi.fvalue)
    f_pval_multi = float(ols_multi.f_pvalue)

    cen_multi_atencao = {"PT08.S1(CO)": 1180.0, "C6H6(GT)": 11.5, "NO2(GT)": 115.0, "T": 27.0}
    cen_multi_critico = {"PT08.S1(CO)": 1520.0, "C6H6(GT)": 24.0, "NO2(GT)": 185.0, "T": 34.0}
    prev_multi_atencao = float(ols_multi.predict([1.0] + [cen_multi_atencao[f] for f in multi_features])[0])
    prev_multi_critico = float(ols_multi.predict([1.0] + [cen_multi_critico[f] for f in multi_features])[0])

    # ------------------------------------------------------------------ 06 Regressao Logistica Binaria
    X_log = df[multi_features]
    y_log = df["alerta_critico"]
    X_tr, X_te, y_tr, y_te = train_test_split(X_log, y_log, test_size=0.25, random_state=42, stratify=y_log)

    log_clf = LogisticRegression(max_iter=1000)
    log_clf.fit(X_tr, y_tr)
    y_pred = log_clf.predict(X_te)
    acc_log = float(accuracy_score(y_te, y_pred))
    cm_log = confusion_matrix(y_te, y_pred).tolist()
    rep_log = classification_report(y_te, y_pred, output_dict=True)

    b0_log = float(log_clf.intercept_[0])
    coef_log = {feat: float(w) for feat, w in zip(multi_features, log_clf.coef_[0])}

    # Grafico Matriz de Confusao (Item 06)
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    sns.heatmap(
        cm_log,
        annot=True,
        fmt="d",
        cmap="magma",
        xticklabels=["Normal/Atenção (0)", "Crítico >= 3.0 (1)"],
        yticklabels=["Normal/Atenção (0)", "Crítico >= 3.0 (1)"],
        ax=ax,
    )
    ax.set_title(f"06b. Matriz de Confusão: Regressão Logística (Acc = {acc_log:.2%})", fontweight="bold")
    ax.set_xlabel("Classe Predita")
    ax.set_ylabel("Classe Real")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "06_matriz_confusao_logistica.png", dpi=160)
    plt.close(fig)

    df_cen_log = pd.DataFrame([cen_multi_atencao, cen_multi_critico])
    probs_log = log_clf.predict_proba(df_cen_log)[:, 1]
    preds_log = log_clf.predict(df_cen_log)

    summary = {
        "dataset": {
            "nome": "UCI Air Quality (Vito et al., 2008)",
            "registros_brutos": 9357,
            "registros_limpos": n_total,
            "variavel_alvo": "CO(GT) [mg/m³]",
            "distribuicao_risco": {k: int(v) for k, v in df["nivel_risco"].value_counts().to_dict().items()},
            "estatisticas_descritivas": df[multi_cols].describe().round(4).to_dict(),
        },
        "item_02_normal": {
            "variavel": "CO(GT)",
            "media": round(co_mean, 4),
            "desvio_padrao": round(co_std, 4),
            "mediana": round(co_median, 4),
            "p_menor_media": round(p_lt_mean, 4),
            "classificacao_a": classify_event_prob(p_lt_mean),
            "p_maior_mediana": round(p_gt_median, 4),
            "classificacao_b": classify_event_prob(p_gt_median),
        },
        "item_03_testes_hipotese": {
            "variavel": "CO(GT)",
            "media_pop": round(co_mean, 4),
            "sigma_pop": round(pop_std, 4),
            "teste_3a_unilateral_esquerda": {
                "n": 20,
                "alpha": 0.06,
                "media_amostral": round(mean_a, 4),
                "z_calculado": round(z_a, 4),
                "z_critico": round(z_crit_a, 4),
                "p_valor": round(p_val_a, 4),
                "rejeita_h0": rejeita_a,
                "decisao": "Rejeitar H0" if rejeita_a else "Não rejeitar H0",
            },
            "teste_3b_unilateral_direita": {
                "n": 25,
                "alpha": 0.09,
                "media_amostral": round(mean_b, 4),
                "z_calculado": round(z_b, 4),
                "z_critico": round(z_crit_b, 4),
                "p_valor": round(p_val_b, 4),
                "rejeita_h0": rejeita_b,
                "decisao": "Rejeitar H0" if rejeita_b else "Não rejeitar H0",
            },
        },
        "item_04_regressao_simples": {
            "x": "PT08.S1(CO)",
            "y": "CO(GT)",
            "covariancia": round(cov_xy, 4),
            "pearson_r": round(pearson_r, 4),
            "pearson_p_valor": pearson_p,
            "intercepto_b0": round(b0_s, 4),
            "inclinacao_b1": round(b1_s, 6),
            "equacao": f"CO(GT) = {b0_s:.4f} + {b1_s:.5f} * PT08.S1(CO)",
            "r2": round(r2_simple, 4),
            "teste_f": round(f_stat_simple, 2),
            "f_p_valor": f_pval_simple,
            "previsao_exemplo": {"PT08.S1(CO)": exemplo_s1, "co_previsto": round(prev_simple, 4)},
        },
        "item_05_regressao_multipla": {
            "variaveis_explicativas": multi_features,
            "alvo": "CO(GT)",
            "matriz_covariancia": cov_matrix.to_dict(),
            "matriz_correlacao": corr_matrix.to_dict(),
            "coeficientes": {k: round(v, 5) for k, v in multi_params.items()},
            "equacao": (
                f"CO(GT) = {multi_params['const']:.4f}"
                f" + {multi_params['PT08.S1(CO)']:.5f}*PT08.S1(CO)"
                f" + {multi_params['C6H6(GT)']:.4f}*C6H6(GT)"
                f" + {multi_params['NO2(GT)']:.5f}*NO2(GT)"
                f" + ({multi_params['T']:.5f})*T"
            ),
            "r2": round(r2_multi, 4),
            "r2_ajustado": round(r2_adj_multi, 4),
            "teste_f": round(f_stat_multi, 2),
            "f_p_valor": f_pval_multi,
            "previsoes": [
                {"cenario": "Atenção Urbana", "entrada": cen_multi_atencao, "co_previsto": round(prev_multi_atencao, 4)},
                {"cenario": "Crítico Queimada", "entrada": cen_multi_critico, "co_previsto": round(prev_multi_critico, 4)},
            ],
        },
        "item_06_regressao_logistica": {
            "variaveis_explicativas": multi_features,
            "alvo_binario": "alerta_critico (1 se CO(GT) >= 3.0 mg/m³)",
            "intercepto_b0": round(b0_log, 4),
            "coeficientes": {k: round(v, 5) for k, v in coef_log.items()},
            "equacao_logit": (
                f"logit(P) = {b0_log:.4f}"
                + "".join(f" + ({coef_log[f]:.5f})*{f}" for f in multi_features)
            ),
            "acuracia_teste": round(acc_log, 4),
            "matriz_confusao": cm_log,
            "precision_critico": round(float(rep_log["1"]["precision"]), 4),
            "recall_critico": round(float(rep_log["1"]["recall"]), 4),
            "f1_critico": round(float(rep_log["1"]["f1-score"]), 4),
            "classificacoes_exemplo": [
                {
                    "cenario": "Atenção Urbana",
                    "entrada": cen_multi_atencao,
                    "prob_critico": round(float(probs_log[0]), 4),
                    "classe_predita": int(preds_log[0]),
                },
                {
                    "cenario": "Crítico Queimada",
                    "entrada": cen_multi_critico,
                    "prob_critico": round(float(probs_log[1]), 4),
                    "classe_predita": int(preds_log[1]),
                },
            ],
        },
    }

    (ARTIFACTS_DIR / "stats_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False)[:1800])
    print("\n[OK] Analise estatistica concluida com sucesso!")


if __name__ == "__main__":
    main()
