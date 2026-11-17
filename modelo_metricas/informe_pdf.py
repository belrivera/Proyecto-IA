"""
Genera el informe PDF a partir de los resultados del modelo (metricas_esterilizacion.py).

Uso:
    python informe_pdf.py
Salida:
    resultados/Informe_esterilizacion_por_comuna.pdf
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, LongTable, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

BASE = Path(__file__).resolve().parent
RES = BASE / "resultados"
GRAF = RES / "graficos"
XLSX = RES / "metricas_esterilizacion.xlsx"
PDF = RES / "Informe_esterilizacion_por_comuna.pdf"

C_PERRO, C_GATO, C_TOTAL = "#2B6CB0", "#DD6B20", "#4A5568"

# Referencias citadas en el informe (APA 7). Tomadas de bibliografia_esterilizacion_animales.md.
REFERENCIAS = [
    "Beauvais, W., Cardwell, J. M., & Brodbelt, D. C. (2012). The effect of neutering on the risk of mammary tumours in dogs – a systematic review. <i>Journal of Small Animal Practice, 53</i>(6), 314–322.",
    "Bryan, J. N., Keeler, M. R., Henry, C. J., Bryan, M. E., Hahn, A. W., & Caldwell, C. W. (2007). A population study of neutering status as a risk factor for canine prostate cancer. <i>The Prostate, 67</i>(11), 1174–1181.",
    "Cooley, D. M., Beranek, B. C., Schlittler, D. L., Glickman, N. W., Glickman, L. T., & Waters, D. J. (2002). Endogenous gonadal hormone exposure and bone sarcoma risk. <i>Cancer Epidemiology, Biomarkers &amp; Prevention, 11</i>(11), 1434–1440.",
    "Creevy, K. E., Grady, J., Little, S. E., Moore, G. E., Strickler, B. G., Thompson, S., &amp; Webb, J. A. (2019). 2019 AAHA canine life stage guidelines. <i>Journal of the American Animal Hospital Association, 55</i>(6), 267–290.",
    "Egenvall, A., Hagman, R., Bonnett, B. N., Hedhammar, Å., Olson, P., &amp; Lagerstedt, A.-S. (2001). Breed risk of pyometra in insured dogs in Sweden. <i>Journal of Veterinary Internal Medicine, 15</i>(6), 530–538.",
    "Farhoody, P., Mallawaarachchi, I., Tarwater, P. M., Serpell, J. A., Duffy, D. L., &amp; Zink, C. (2018). Aggression toward familiar people, strangers, and conspecifics in gonadectomized and intact dogs. <i>Frontiers in Veterinary Science, 5</i>, 18. https://doi.org/10.3389/fvets.2018.00018",
    "Hagman, R. (2018). Pyometra in small animals. <i>Veterinary Clinics of North America: Small Animal Practice, 48</i>(4), 639–661.",
    "Hart, B. L., &amp; Barrett, R. E. (1973). Effects of castration on fighting, roaming, and urine spraying in adult male cats. <i>Journal of the American Veterinary Medical Association, 163</i>(3), 290–292.",
    "Hart, B. L., Hart, L. A., Thigpen, A. P., &amp; Willits, N. H. (2014). Long-term health effects of neutering dogs: Comparison of Labrador Retrievers with Golden Retrievers. <i>PLoS ONE, 9</i>(7), e102241. https://doi.org/10.1371/journal.pone.0102241",
    "Hart, B. L., Hart, L. A., Thigpen, A. P., &amp; Willits, N. H. (2020). Assisting decision-making on age of neutering for 35 breeds of dogs: Associated joint disorders, cancers, and urinary incontinence. <i>Frontiers in Veterinary Science, 7</i>, 388. https://doi.org/10.3389/fvets.2020.00388",
    "Hoffman, J. M., Creevy, K. E., &amp; Promislow, D. E. L. (2013). Reproductive capability is associated with lifespan and cause of death in companion dogs. <i>PLoS ONE, 8</i>(4), e61082. https://doi.org/10.1371/journal.pone.0061082",
    "Hopkins, S. G., Schubert, T. A., &amp; Hart, B. L. (1976). Castration of adult male dogs: Effects on roaming, aggression, urine marking, and mounting. <i>Journal of the American Veterinary Medical Association, 168</i>(12), 1108–1110.",
    "Journal of Small Animal Practice. (2025). Correction to “WSAVA guidelines for the control of reproduction in dogs and cats”. <i>Journal of Small Animal Practice.</i> https://doi.org/10.1111/jsap.13839",
    "Kanchuk, M. L., Backus, R. C., Calvert, C. C., Morris, J. G., &amp; Rogers, Q. R. (2003). Weight gain in gonadectomized normal and lipoprotein lipase-deficient male domestic cats results from increased food intake and not decreased energy expenditure. <i>The Journal of Nutrition, 133</i>(6), 1866–1874.",
    "Kreisler, R. E., Cornell, H. N., &amp; Levy, J. K. (2019). Decrease in population and increase in welfare of community cats in a twenty-three year trap-neuter-return program in Key Largo, FL: The ORCAT Program. <i>Frontiers in Veterinary Science, 6</i>, 7. https://doi.org/10.3389/fvets.2019.00007",
    "Lefebvre, S. L., Yang, M., Wang, M., Elliott, D. A., Buff, P. R., &amp; Lund, E. M. (2013). Effect of age at gonadectomy on the probability of dogs becoming overweight. <i>Journal of the American Veterinary Medical Association, 243</i>(2), 236–243.",
    "Levy, J. K., Isaza, N. M., &amp; Scott, K. C. (2014). Effect of high-impact targeted trap-neuter-return and adoption of community cats on cat intake to a shelter. <i>The Veterinary Journal, 201</i>(3), 269–274.",
    "Longcore, T., Rich, C., &amp; Sullivan, L. M. (2009). Critical assessment of claims regarding management of feral cats by trap-neuter-return. <i>Conservation Biology, 23</i>(4), 887–894.",
    "McGreevy, P. D., Wilson, B., Starling, M. J., &amp; Serpell, J. A. (2018). Behavioural risks in male dogs with minimal lifetime exposure to gonadal hormones may complicate population-control benefits of desexing. <i>PLoS ONE, 13</i>(5), e0196284. https://doi.org/10.1371/journal.pone.0196284",
    "Overley, B., Shofer, F. S., Goldschmidt, M. H., Sherer, D., &amp; Sorenmo, K. U. (2005). Association between ovarihysterectomy and feline mammary carcinoma. <i>Journal of Veterinary Internal Medicine, 19</i>(4), 560–563.",
    "Romagnoli, S., Krekeler, N., de Cramer, K., Kutzler, M., McCarthy, R., &amp; Schaefer-Somi, S. (2024). WSAVA guidelines for the control of reproduction in dogs and cats. <i>Journal of Small Animal Practice, 65</i>(7), 424–559. https://doi.org/10.1111/jsap.13724",
    "Root Kustritz, M. V. (2012). Effects of surgical sterilization on canine and feline health and on society. <i>Reproduction in Domestic Animals, 47</i>(Suppl. 4), 214–222.",
    "Schneider, R., Dorn, C. R., &amp; Taylor, D. O. (1969). Factors influencing canine mammary cancer development and postsurgical survival. <i>Journal of the National Cancer Institute, 43</i>(6), 1249–1261.",
    "Spain, C. V., Scarlett, J. M., &amp; Houpt, K. A. (2004). Long-term risks and benefits of early-age gonadectomy in cats. <i>Journal of the American Veterinary Medical Association, 224</i>(3), 372–379.",
    "Starling, M., Fawcett, A., Wilson, B., Serpell, J., &amp; McGreevy, P. (2019). Behavioural risks in female dogs with minimal lifetime exposure to gonadal hormones. <i>PLoS ONE, 14</i>(12), e0223709. https://doi.org/10.1371/journal.pone.0223709",
    "Thrusfield, M. V., Holt, P. E., &amp; Muirhead, R. H. (1998). Acquired urinary incontinence in bitches: Its incidence and relationship to neutering practices. <i>Journal of Small Animal Practice, 39</i>(12), 559–566.",
    "Torres de la Riva, G., Hart, B. L., Farver, T. B., Oberbauer, A. M., Messam, L. L. M., Willits, N., &amp; Hart, L. A. (2013). Neutering dogs: Effects on joint disorders and cancers in Golden Retrievers. <i>PLoS ONE, 8</i>(2), e55937. https://doi.org/10.1371/journal.pone.0055937",
    "Urfer, S. R., &amp; Kaeberlein, M. (2019). Desexing dogs: A review of the current literature. <i>Animals, 9</i>(12), 1086. https://doi.org/10.3390/ani9121086",
]
FUENTE_DATOS = ("Registro Nacional de Mascotas o Animales de Compañía (RNAC). (2026). <i>Base de datos de animales de compañía "
                "inscritos, corte julio 2026</i> [archivo «RNAC julio 2026.xlsx»]. Chile.")
N_MIN_RANKING = 100  # mínimo de animales registrados para entrar a rankings de %


def region_corta(r: str) -> str:
    r = re.sub(r"^REGI[ÓO]N\s+(DEL\s+|DE\s+)?", "", str(r), flags=re.I)
    u = r.upper()
    for clave, corto in [("HIGGINS", "O'Higgins"), ("AYS", "Aysén"), ("MAGALLANES", "Magallanes"),
                         ("METROPOLITANA", "Metropolitana")]:
        if clave in u:
            return corto
    return r.title().replace(" Y ", " y ")


def miles(x) -> str:
    return f"{int(x):,}".replace(",", ".")


def pct(x) -> str:
    return f"{x:.1f} %".replace(".", ",")


# ------------------------------------------------------------------ gráficos
def graficos(com: pd.DataFrame, reg: pd.DataFrame) -> dict[str, Path]:
    GRAF.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    out = {}

    # 1. % esterilización por región, perros vs gatos
    r = reg.sort_values("total_pct_esterilizados")
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    y = range(len(r))
    ax.barh([i + 0.2 for i in y], r["perro_pct_esterilizados"], 0.4, color=C_PERRO, label="Perros")
    ax.barh([i - 0.2 for i in y], r["gato_pct_esterilizados"], 0.4, color=C_GATO, label="Gatos")
    ax.set_yticks(list(y), r["region_c"])
    ax.set_xlim(0, 100); ax.set_xlabel("% esterilizados")
    ax.axvline(com.attrs["nac_perro"], color=C_PERRO, ls=":", lw=1)
    ax.axvline(com.attrs["nac_gato"], color=C_GATO, ls=":", lw=1)
    ax.legend(loc="lower right", frameon=False)
    ax.set_title("Figura 1. Porcentaje de esterilización por región (líneas punteadas: promedio nacional)", loc="left", fontsize=9)
    fig.tight_layout(); out["reg"] = GRAF / "fig1_region.png"; fig.savefig(out["reg"], dpi=200); plt.close(fig)

    # 2. Top 15 comunas por número de esterilizados
    t = com.nlargest(15, "total_esterilizados").iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.barh(t["comuna"], t["perro_esterilizados"], color=C_PERRO, label="Perros")
    ax.barh(t["comuna"], t["gato_esterilizados"], left=t["perro_esterilizados"], color=C_GATO, label="Gatos")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: miles(v)))
    ax.set_xlabel("Animales esterilizados"); ax.legend(loc="lower right", frameon=False)
    ax.set_title("Figura 2. Las 15 comunas con más perros y gatos esterilizados", loc="left", fontsize=9)
    fig.tight_layout(); out["top"] = GRAF / "fig2_top_comunas.png"; fig.savefig(out["top"], dpi=200); plt.close(fig)

    # 3. Distribución del % comunal
    c = com[com["total_registrados"] >= N_MIN_RANKING]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    bins = range(0, 101, 5)
    ax.hist(c["perro_pct_esterilizados"].dropna(), bins=bins, alpha=0.75, color=C_PERRO, label="Perros")
    ax.hist(c["gato_pct_esterilizados"].dropna(), bins=bins, alpha=0.75, color=C_GATO, label="Gatos")
    ax.set_xlabel("% esterilizados en la comuna"); ax.set_ylabel("N.º de comunas")
    ax.legend(frameon=False)
    ax.set_title(f"Figura 3. Distribución del % de esterilización entre comunas (n ≥ {N_MIN_RANKING} animales)", loc="left", fontsize=9)
    fig.tight_layout(); out["hist"] = GRAF / "fig3_distribucion.png"; fig.savefig(out["hist"], dpi=200); plt.close(fig)

    # 4. Comunas con mayor y menor % total (con IC 95 %)
    hi = c.nlargest(10, "total_pct_esterilizados"); lo = c.nsmallest(10, "total_pct_esterilizados")
    d = pd.concat([lo, hi]).sort_values("total_pct_esterilizados")
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    col = [C_GATO if v >= com.attrs["nac_total"] else C_PERRO for v in d["total_pct_esterilizados"]]
    err = [d["total_pct_esterilizados"] - d["total_ic95_inf"], d["total_ic95_sup"] - d["total_pct_esterilizados"]]
    ax.errorbar(d["total_pct_esterilizados"], range(len(d)), xerr=err, fmt="none", ecolor="#999", lw=1)
    ax.scatter(d["total_pct_esterilizados"], range(len(d)), c=col, zorder=3)
    ax.set_yticks(range(len(d)), [f"{a} ({region_corta(b)})" for a, b in zip(d["comuna"], d["region"])])
    ax.axvline(com.attrs["nac_total"], color=C_TOTAL, ls=":", lw=1)
    ax.set_xlim(0, 100); ax.set_xlabel("% esterilizados (perros + gatos), con IC 95 %")
    ax.set_title("Figura 4. Comunas con mayor y menor % de esterilización (10 y 10)", loc="left", fontsize=9)
    fig.tight_layout(); out["rank"] = GRAF / "fig4_ranking.png"; fig.savefig(out["rank"], dpi=200); plt.close(fig)
    return out


# ------------------------------------------------------------------ PDF
def tabla(datos, anchos, encabezado_color="#2D3748", zebra=True, fuente=8, alinear_der_desde=1):
    t = LongTable(datos, colWidths=anchos, repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(encabezado_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), fuente),
        ("ALIGN", (alinear_der_desde, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    if zebra:
        for i in range(1, len(datos)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7FAFC")))
    t.setStyle(TableStyle(st))
    return t


def main() -> None:
    com = pd.read_excel(XLSX, sheet_name="Por comuna", engine="calamine")
    reg = pd.read_excel(XLSX, sheet_name="Por región", engine="calamine")
    nac = pd.read_excel(XLSX, sheet_name="Nacional", engine="calamine").iloc[0]
    cal = pd.read_excel(XLSX, sheet_name="Calidad de datos", engine="calamine").set_index("indicador")["valor"]
    reg["region_c"] = reg["region"].map(region_corta)
    com.attrs.update(nac_perro=nac.perro_pct_esterilizados, nac_gato=nac.gato_pct_esterilizados,
                     nac_total=nac.total_pct_esterilizados)
    g = graficos(com, reg)

    # ---- cifras para la interpretación (todas calculadas, no escritas a mano)
    c = com[com["total_registrados"] >= N_MIN_RANKING]
    brecha = nac.gato_pct_esterilizados - nac.perro_pct_esterilizados
    r_max, r_min = reg.loc[reg.total_pct_esterilizados.idxmax()], reg.loc[reg.total_pct_esterilizados.idxmin()]
    c_max, c_min = c.loc[c.total_pct_esterilizados.idxmax()], c.loc[c.total_pct_esterilizados.idxmin()]
    q1p, medp, q3p = c.perro_pct_esterilizados.quantile([.25, .5, .75])
    q1g, medg, q3g = c.gato_pct_esterilizados.quantile([.25, .5, .75])
    gato_mayor = int((c.gato_pct_esterilizados > c.perro_pct_esterilizados).sum())
    bajo50_perro = int((c.perro_pct_esterilizados < 50).sum())
    top10_share = 100 * com.nlargest(10, "total_esterilizados").total_esterilizados.sum() / nac.total_esterilizados
    sd = nac.get("sin_dueno_pct_esterilizados")
    n_excl = len(com) - len(c)

    # ---- estilos
    ss = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=17, leading=21, spaceAfter=4)
    H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, textColor=colors.HexColor("#2D3748"), spaceBefore=10)
    P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY)
    S = ParagraphStyle("S", parent=P, fontSize=8, textColor=colors.HexColor("#4A5568"))
    B = ParagraphStyle("B", parent=P, leftIndent=12, bulletIndent=2)
    H3 = ParagraphStyle("H3", parent=P, fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=2)
    REF = ParagraphStyle("REF", parent=P, fontSize=8.5, leading=11.5, leftIndent=18, firstLineIndent=-18,
                         alignment=0, spaceAfter=4)

    doc = SimpleDocTemplate(str(PDF), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Informe: esterilización de perros y gatos por comuna", author="Proyecto IA")
    W = A4[0] - 4 * cm
    el = []

    el += [Paragraph("Esterilización de perros y gatos por comuna", H1),
           Paragraph(f"Registro Nacional de Mascotas (RNAC) · corte julio 2026 · informe generado el {date.today():%d-%m-%Y}", S),
           Spacer(1, 8),
           Paragraph("<b>Pregunta de investigación:</b> ¿Cuántos perros y gatos están esterilizados por comuna en la base de datos del proyecto?", P)]

    # ---- contexto bibliográfico
    el += [Paragraph("1. Contexto: qué dice la evidencia sobre la esterilización", H2),
           Paragraph(
               "La esterilización quirúrgica (ovariectomía, ovariohisterectomía u orquiectomía) es la herramienta más usada "
               "para controlar la reproducción de perros y gatos. La literatura veterinaria coincide en que tiene beneficios "
               "claros, pero también riesgos que dependen de la especie, la raza, el tamaño, el sexo y la edad a la que se "
               "realiza (Root Kustritz, 2012; Urfer &amp; Kaeberlein, 2019). Por eso conocer cuántos animales están "
               "esterilizados en cada comuna permite dimensionar tanto los beneficios sanitarios y poblacionales "
               "alcanzados como los grupos donde aún se concentran animales enteros.", P),
           Paragraph("Beneficios documentados", H3)]
    el += [Paragraph(t, B, bulletText="•") for t in [
        "<b>Tumores mamarios.</b> La esterilización temprana se asocia a un menor riesgo de tumores mamarios en perras "
        "(Schneider et al., 1969) y, en gatas, la ovariohisterectomía antes de los 6 meses redujo el riesgo de carcinoma "
        "mamario en un 91 % (Overley et al., 2005). Una revisión sistemática advierte, sin embargo, que la evidencia en "
        "perras es más débil de lo que se suele afirmar (Beauvais et al., 2012).",
        "<b>Piometra.</b> La esterilización elimina el riesgo de piometra, una infección uterina grave y frecuente en hembras "
        "enteras de edad avanzada (Egenvall et al., 2001; Hagman, 2018).",
        "<b>Conducta.</b> La castración de machos reduce el vagabundeo, el marcaje con orina y la monta en perros "
        "(Hopkins et al., 1976), y las peleas y el marcaje en gatos (Hart &amp; Barrett, 1973).",
        "<b>Longevidad.</b> En perros, la esterilización se ha asociado a una mayor esperanza de vida, aunque con distinto "
        "perfil de causas de muerte (Hoffman et al., 2013).",
        "<b>Control poblacional.</b> Los programas intensivos de captura, esterilización y retorno (CER) redujeron el "
        "ingreso de gatos a refugios (Levy et al., 2014) y el tamaño de colonias felinas a largo plazo (Kreisler et al., 2019), "
        "aunque su eficacia general ha sido cuestionada (Longcore et al., 2009).",
    ]]
    el.append(Paragraph("Riesgos documentados", H3))
    el += [Paragraph(t, B, bulletText="•") for t in [
        "<b>Articulaciones y cáncer en perros de razas grandes.</b> En algunas razas, la esterilización antes del año se "
        "asocia a más displasia de cadera, rotura de ligamento cruzado y ciertos cánceres (Torres de la Riva et al., 2013; "
        "Hart et al., 2014). El riesgo varía mucho entre razas y tamaños (Hart et al., 2020). También se ha asociado a "
        "osteosarcoma (Cooley et al., 2002) y a cáncer de próstata en machos castrados (Bryan et al., 2007).",
        "<b>Incontinencia urinaria y obesidad.</b> Las perras esterilizadas tienen más incontinencia urinaria "
        "(Thrusfield et al., 1998), y la esterilización aumenta la probabilidad de sobrepeso en perros y gatos "
        "(Kanchuk et al., 2003; Lefebvre et al., 2013).",
        "<b>Conducta en perros.</b> Algunos estudios asocian la esterilización, sobre todo temprana, a más miedo o "
        "agresividad (Farhoody et al., 2018; McGreevy et al., 2018; Starling et al., 2019).",
        "<b>Gatos.</b> En gatos, la esterilización temprana no se asoció a un aumento de problemas graves de salud "
        "(Spain et al., 2004), por lo que el balance entre beneficios y riesgos es más claro que en perros.",
    ]]
    el += [Paragraph("Recomendaciones actuales", H3),
           Paragraph(
               "La guía de la Asociación Mundial de Veterinarios de Pequeños Animales (WSAVA) recomienda decidir la "
               "esterilización caso a caso, con el bienestar animal como prioridad, y desaconseja la esterilización "
               "pediátrica rutinaria (Romagnoli et al., 2024). Su sección de ética no alcanzó consenso dentro de la WSAVA "
               "(Journal of Small Animal Practice, 2025). La guía de la Asociación Americana de Hospitales de Animales "
               "(AAHA) también recomienda individualizar la decisión según raza, tamaño y estilo de vida (Creevy et al., 2019).", P)]

    el += [Paragraph("2. Metodología", H2),
           Paragraph(
               f"Se procesaron las cinco hojas de datos del archivo <i>RNAC julio 2026.xlsx</i> ({miles(cal['Registros totales en el Excel'])} registros). "
               f"Se excluyeron {miles(cal['Fallecidos excluidos'])} animales fallecidos, por lo que la población analizada es de "
               f"<b>{miles(cal['Registros usados en las métricas'])}</b> perros y gatos vivos registrados en {miles(cal['Comunas distintas'])} comunas "
               f"y {miles(cal['Regiones distintas'])} regiones. Un animal se considera <i>esterilizado</i> si su estado reproductivo es "
               "«Esterilizado»; «Entero» equivale a no esterilizado (según la hoja «Léame primero»). Para cada comuna se calculan "
               "el número de animales registrados, el de esterilizados y el porcentaje de esterilización por especie, con un "
               "intervalo de confianza del 95 % (método de Wilson). Los rankings por porcentaje consideran solo las comunas "
               f"con al menos {N_MIN_RANKING} animales registrados ("
               + (f"{n_excl} comuna queda fuera" if n_excl == 1 else f"{n_excl} comunas quedan fuera") + " por tamaño).", P)]

    # ---- tabla resumen nacional
    el.append(Paragraph("3. Resumen nacional", H2))
    filas = [["Especie", "Registrados", "Esterilizados", "Enteros", "% esterilizados", "IC 95 %"]]
    for esp, nom in [("perro", "Perros"), ("gato", "Gatos"), ("total", "Total")]:
        filas.append([nom, miles(nac[f"{esp}_registrados"]), miles(nac[f"{esp}_esterilizados"]),
                      miles(nac[f"{esp}_enteros"]), pct(nac[f"{esp}_pct_esterilizados"]),
                      f"{pct(nac[f'{esp}_ic95_inf'])} – {pct(nac[f'{esp}_ic95_sup'])}"])
    t = tabla(filas, [2.6 * cm, 2.6 * cm, 2.6 * cm, 2.4 * cm, 2.6 * cm, 4.2 * cm], fuente=9)
    t.setStyle(TableStyle([("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold")]))
    el += [t, Spacer(1, 4), Paragraph("Tabla 1. Perros y gatos esterilizados a nivel nacional (excluidos los fallecidos).", S)]

    # ---- interpretación
    el.append(Paragraph("4. Interpretación de las métricas", H2))
    puntos = [
        f"<b>Diferencia por especie.</b> El {pct(nac.gato_pct_esterilizados)} de los gatos registrados está esterilizado, frente "
        f"al {pct(nac.perro_pct_esterilizados)} de los perros: una brecha de {pct(brecha).replace(' %', '')} puntos porcentuales. "
        f"La brecha se repite a nivel local: en {gato_mayor} de {len(c)} comunas el porcentaje de gatos supera al de perros.",
        f"<b>Volumen.</b> En total hay {miles(nac.total_esterilizados)} animales esterilizados ({pct(nac.total_pct_esterilizados)}). "
        f"La cifra está concentrada: las 10 comunas con más esterilizados reúnen el {pct(top10_share)} del total nacional, "
        "en buena parte porque también son las comunas con más animales registrados (Figura 2).",
        f"<b>Variación territorial.</b> Por región, el porcentaje va de {pct(r_min.total_pct_esterilizados)} ({region_corta(r_min.region)}) "
        f"a {pct(r_max.total_pct_esterilizados)} ({region_corta(r_max.region)}). Entre comunas, la mediana del porcentaje de perros esterilizados es de "
        f"{pct(medp)} (rango intercuartílico de {pct(q1p)} a {pct(q3p)}), y la de gatos, de {pct(medg)} ({pct(q1g)} a {pct(q3g)}). "
        f"En {bajo50_perro} comunas menos de la mitad de los perros está esterilizada.",
        f"<b>Comunas extremas.</b> Entre las comunas con al menos {N_MIN_RANKING} animales, la de mayor esterilización es "
        f"{c_max.comuna.title()} ({pct(c_max.total_pct_esterilizados)}) y la de menor es {c_min.comuna.title()} "
        f"({pct(c_min.total_pct_esterilizados)}) (Figura 4). Los intervalos de confianza son estrechos en las comunas grandes "
        "y más amplios en las pequeñas, donde el porcentaje es menos estable.",
    ]
    if pd.notna(sd):
        puntos.append(f"<b>Animales sin dueño.</b> Entre los {miles(nac.sin_dueno_registrados)} animales registrados como «sin dueño», "
                      f"el {pct(sd)} está esterilizado. Esta cifra es coherente con el uso de la esterilización como herramienta de "
                      "control de animales comunitarios descrita en la literatura (Levy et al., 2014; Kreisler et al., 2019).")
    puntos.append(
        "<b>Lectura a la luz de la literatura.</b> La mayor esterilización de gatos es coherente con un balance "
        "beneficio-riesgo más favorable en esa especie (Spain et al., 2004; Overley et al., 2005). En perros, la cifra "
        "cercana al 50 % podría reflejar en parte las recomendaciones de individualizar la decisión según raza y tamaño "
        "(Hart et al., 2020; Romagnoli et al., 2024), aunque estos datos no permiten probar esa causa. Al mismo tiempo, "
        f"significa que {miles(nac.perro_enteros)} perros siguen enteros: en las hembras, ese grupo mantiene el riesgo "
        "de piometra y tumores mamarios (Hagman, 2018; Schneider et al., 1969). Las comunas con baja esterilización de "
        "perros son candidatas prioritarias para campañas, idealmente con criterios por edad, sexo y tamaño.")
    puntos.append(
        "<b>Limitaciones.</b> Las cifras describen a los animales <i>inscritos</i> en el RNAC, no a toda la población de cada "
        "comuna: el registro sobrerrepresenta a los animales con dueño responsable y a las comunas con operativos de "
        "inscripción, y el estado reproductivo puede estar desactualizado si un animal se esterilizó después de inscribirse. "
        f"Se detectaron {miles(cal['Filas idénticas en las 19 columnas (posibles duplicados, NO excluidos)'])} filas idénticas "
        f"({pct(100 * cal['Filas idénticas en las 19 columnas (posibles duplicados, NO excluidos)'] / cal['Registros totales en el Excel'])}), "
        "que no alteran las conclusiones.")
    el += [Paragraph(p, B, bulletText="•") for p in puntos]

    # ---- gráficos
    el.append(PageBreak())
    el.append(Paragraph("5. Gráficos", H2))
    for k, h in [("reg", 5.2), ("top", 4.6), ("hist", 3.6), ("rank", 5.2)]:
        el += [KeepTogether([Image(str(g[k]), width=W, height=W * h / 7.5)]), Spacer(1, 6)]

    # ---- tabla por región
    el.append(PageBreak())
    el.append(Paragraph("6. Resultados por región", H2))
    filas = [["Región", "Perros reg.", "Perros est.", "% perros", "Gatos reg.", "Gatos est.", "% gatos", "% total"]]
    for _, r in reg.sort_values("total_pct_esterilizados", ascending=False).iterrows():
        filas.append([r.region_c, miles(r.perro_registrados), miles(r.perro_esterilizados), pct(r.perro_pct_esterilizados),
                      miles(r.gato_registrados), miles(r.gato_esterilizados), pct(r.gato_pct_esterilizados),
                      pct(r.total_pct_esterilizados)])
    el += [tabla(filas, [4.2 * cm, 1.8 * cm, 1.8 * cm, 1.6 * cm, 1.8 * cm, 1.8 * cm, 1.6 * cm, 1.6 * cm]),
           Spacer(1, 4), Paragraph("Tabla 2. Perros y gatos esterilizados por región, ordenadas por % total.", S)]

    # ---- anexo por comuna
    el.append(PageBreak())
    el.append(Paragraph("Anexo. Resultados por comuna", H2))
    el.append(Paragraph("Comunas ordenadas por región y por número de animales esterilizados. «reg.»: registrados; «est.»: esterilizados.", S))
    el.append(Spacer(1, 4))
    filas = [["Comuna", "Región", "Perros reg.", "Perros est.", "% perros", "Gatos reg.", "Gatos est.", "% gatos", "% total"]]
    com["region_c"] = com["region"].map(region_corta)
    for _, r in com.sort_values(["region_c", "total_esterilizados"], ascending=[True, False]).iterrows():
        filas.append([str(r.comuna).title()[:24], r.region_c[:18], miles(r.perro_registrados), miles(r.perro_esterilizados),
                      pct(r.perro_pct_esterilizados), miles(r.gato_registrados), miles(r.gato_esterilizados),
                      pct(r.gato_pct_esterilizados), pct(r.total_pct_esterilizados)])
    el.append(tabla(filas, [3.4 * cm, 2.9 * cm, 1.45 * cm, 1.45 * cm, 1.3 * cm, 1.45 * cm, 1.45 * cm, 1.3 * cm, 1.3 * cm],
                    fuente=6.8, alinear_der_desde=2))

    # ---- referencias
    el.append(PageBreak())
    el.append(Paragraph("Referencias", H2))
    el.append(Paragraph("Fuente de datos", H3))
    el.append(Paragraph(FUENTE_DATOS, REF))
    el.append(Paragraph("Bibliografía", H3))
    el += [Paragraph(r, REF) for r in REFERENCIAS]

    def pie(canvas, d):
        canvas.saveState(); canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.HexColor("#718096"))
        canvas.drawString(2 * cm, 1.1 * cm, "Fuente: RNAC julio 2026 · Elaboración propia (modelo_metricas/metricas_esterilizacion.py)")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Página {d.page}")
        canvas.restoreState()

    doc.build(el, onFirstPage=pie, onLaterPages=pie)
    print(f"PDF generado: {PDF}")


if __name__ == "__main__":
    main()
