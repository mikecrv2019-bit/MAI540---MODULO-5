"""Rol 3 (Auditor): verificacion independiente. Codigo propio.

NO importa src/validacion.py ni src/particion_unica.py. Lee el CSV directamente.
Solo importa de src/ lo imprescindible para INSPECCIONAR los objetos reales del
ingeniero (src/modelos.py: crear_pipeline y dos_modelos). Las metricas, los
pliegues y las particiones se recalculan aqui con codigo propio.

Determinista: sin fechas ni tiempos. Salida: consola y verificacion_salida.txt.
Uso: python evidencia/03_auditor/verificar.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from modelos import crear_pipeline, dos_modelos  # noqa: E402  (solo para inspeccionar)

LINEAS = []
RESULTADOS = []


def p(*a):
    s = " ".join(str(x) for x in a)
    LINEAS.append(s)
    print(s)


def chk(nombre, ok, detalle=""):
    RESULTADOS.append((nombre, bool(ok)))
    p(f"[{'OK ' if ok else 'FALLO'}] {nombre}" + (f" :: {detalle}" if detalle else ""))


# ---------------------------------------------------------------- datos (propios)
df = pd.read_csv(RAIZ / "datos" / "credit_g.csv", keep_default_na=False, na_values=[""])
raw_text = (RAIZ / "datos" / "credit_g.csv").read_text(encoding="utf-8")
y = (df["clase"] == "bad").astype(int).to_numpy()
X = df.drop(columns=["clase"])
cat = [c for c in X.columns if X[c].dtype == object or str(X[c].dtype).startswith("str")]
num = [c for c in X.columns if c not in cat]

metr = json.loads((RAIZ / "evidencia/02_ingeniero_modelos/metricas.json").read_text(encoding="utf-8"))
metr_md = (RAIZ / "evidencia/02_ingeniero_modelos/metricas.md").read_text(encoding="utf-8")
res = json.loads((RAIZ / "evidencia/01_analista_datos/resumen_datos.json").read_text(encoding="utf-8"))
res_md = (RAIZ / "evidencia/01_analista_datos/resumen_datos.md").read_text(encoding="utf-8")

# ================================================================ 1. RESUMEN DE DATOS
p("=== 1. Resumen de datos vs CSV ===")
chk("1.1 forma X = [1000, 20]", list(X.shape) == res["forma_X"] == [1000, 20], f"{X.shape}")
chk("1.2 clase good/bad = 700/300",
    (y == 0).sum() == res["clase"]["good_0"] == 700 and (y == 1).sum() == res["clase"]["bad_1"] == 300)
chk("1.3 valores de clase solo {good,bad}", set(df["clase"].unique()) == {"good", "bad"})
chk("1.4 faltantes = 0 (con lectura que solo trata '' como NA)", int(df.isna().sum().sum()) == 0)
lineas_csv = raw_text.splitlines()
chk("1.5 ninguna celda vacia en el CSV crudo",
    all(len(l.split(",")) == 21 and "" not in l.split(",") for l in lineas_csv),
    f"{len(lineas_csv)} lineas")
chk("1.6 duplicados en X = 0 y X+clase = 0",
    int(X.duplicated().sum()) == 0 and int(df.duplicated().sum()) == 0)
chk("1.7 X identico con clase distinta = 0",
    int((df.drop_duplicates().duplicated(subset=list(X.columns), keep=False)).sum()) == 0)
chk("1.8 13 categoricas y 7 numericas, listas iguales",
    cat == res["columnas_categoricas"] and num == res["columnas_numericas"] and len(cat) == 13 and len(num) == 7)
chk("1.9 columnas numericas son int64", all(str(X[c].dtype) == "int64" for c in num))
ok_card = all(X[c].nunique() == res["categoricas"][c]["cardinalidad"] for c in cat)
ok_cnt = all(X[c].value_counts().to_dict() == res["categoricas"][c]["categorias"] for c in cat)
tasa_ok = True
for c in cat:
    t = df.groupby(c)["clase"].apply(lambda s: (s == "bad").mean()).round(4).to_dict()
    tasa_ok &= all(abs(t[k] - v) < 1e-9 for k, v in res["categoricas"][c]["tasa_bad_por_categoria"].items())
chk("1.10 cardinalidades, conteos y tasa_bad por categoria coinciden", ok_card and ok_cnt and tasa_ok)
num_ok = True
for c in num:
    s = X[c]
    q1, q3 = s.quantile(.25), s.quantile(.75)
    iqr = q3 - q1
    at = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
    r = res["numericas"][c]
    num_ok &= (s.min() == r["min"] and s.max() == r["max"] and abs(s.mean() - r["media"]) < 1e-3
               and s.median() == r["mediana"] and abs(s.std() - r["desv_est"]) < 1e-3
               and abs(s.skew() - r["asimetria"]) < 1e-3 and s.nunique() == r["valores_unicos"]
               and at == r["atipicos_iqr_1_5"])
chk("1.11 estadisticos numericos (min/max/media/mediana/desv/asimetria/unicos/atipicos IQR) coinciden", num_ok)
chk("1.12 'none' literal conservado como categoria (no NaN): conteos 907/814/596",
    (X["other_parties"] == "none").sum() == 907 and (X["other_payment_plans"] == "none").sum() == 814
    and (X["own_telephone"] == "none").sum() == 596)
chk("1.13 'purpose' retraining = 9 filas", (X["purpose"] == "retraining").sum() == 9)
chk("1.14 resumen .md consistente con .json (1000 filas, 70.0%/30.0%, 0.7000)",
    "1000 filas x 20 columnas" in res_md and "0.7000" in res_md and "| good (0) | 700 | 70.0% |" in res_md
    and "| bad (1) | 300 | 30.0% |" in res_md)

# ================================================================ 2. INSPECCION DEL PIPELINE
p("")
p("=== 2. Inspeccion de objetos Pipeline reales (src/modelos.py) ===")
modelos_eng = dos_modelos()
tipos_ok = (isinstance(modelos_eng["arbol"], DecisionTreeClassifier)
            and isinstance(modelos_eng["random_forest"], RandomForestClassifier))
chk("2.1 modelos: DecisionTreeClassifier y RandomForestClassifier", tipos_ok)
pr = {k: v.get_params() for k, v in modelos_eng.items()}
defaults = {"arbol": DecisionTreeClassifier(random_state=42).get_params(),
            "random_forest": RandomForestClassifier(random_state=42).get_params()}
chk("2.2 hiperparametros = defaults salvo random_state=42",
    pr["arbol"] == defaults["arbol"] and pr["random_forest"] == defaults["random_forest"]
    and pr["arbol"]["random_state"] == 42 and pr["random_forest"]["random_state"] == 42,
    f"RF n_estimators={pr['random_forest']['n_estimators']}, arbol max_depth={pr['arbol']['max_depth']}")

pipes = {k: crear_pipeline(e, cat, num) for k, e in dos_modelos().items()}
for k, pipe in pipes.items():
    ok_t = isinstance(pipe, Pipeline) and [n for n, _ in pipe.steps] == ["prep", "modelo"]
    prep = pipe.named_steps["prep"]
    ok_ct = isinstance(prep, ColumnTransformer)
    tr = {n: (t, list(c)) for n, t, c in prep.transformers}
    enc = tr["cat"][0]
    ok_enc = isinstance(enc, OrdinalEncoder) and tr["cat"][1] == cat
    ok_num = tr["num"][0] == "passthrough" and tr["num"][1] == num
    chk(f"2.3 [{k}] Pipeline(prep=ColumnTransformer[OrdinalEncoder en 13 cat, passthrough 7 num], modelo)",
        ok_t and ok_ct and ok_enc and ok_num and prep.remainder == "drop",
        f"steps={[n for n, _ in pipe.steps]}, handle_unknown={enc.handle_unknown}, unknown_value={enc.unknown_value}")
    chk(f"2.4 [{k}] el pipeline NO esta ajustado antes de la validacion",
        not hasattr(prep, "transformers_") and not hasattr(pipe.named_steps["modelo"], "classes_"))

# 2.5 el encoder se ajusta SOLO con entrenamiento: pliegue a pliegue, con estimadores reales ajustados
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
folds = list(skf.split(X, y))
for k, pipe in pipes.items():
    ok_cat = True
    ok_n = True
    detalle = []
    for i, (tr_idx, te_idx) in enumerate(folds):
        m = clone(pipe).fit(X.iloc[tr_idx], y[tr_idx])
        enc = m.named_steps["prep"].named_transformers_["cat"]
        for j, c in enumerate(cat):
            if sorted(enc.categories_[j].tolist()) != sorted(X.iloc[tr_idx][c].unique().tolist()):
                ok_cat = False
        # el modelo vio solo n_train filas: arbol -> raiz con n_node_samples = n_train
        mod = m.named_steps["modelo"]
        if k == "arbol":
            ok_n &= int(mod.tree_.n_node_samples[0]) == len(tr_idx) == 800
        else:
            ok_n &= mod.n_features_in_ == 20  # RF no expone n de filas; se comprueba n_features
        detalle.append(len(tr_idx))
    chk(f"2.5 [{k}] categories_ del OrdinalEncoder == categorias del entrenamiento de cada pliegue (5/5)",
        ok_cat, f"n_train por pliegue={detalle}")
    chk(f"2.6 [{k}] el modelo se ajusta con 800 filas de entrenamiento por pliegue" if k == "arbol"
        else f"2.6 [{k}] el modelo recibe 20 columnas codificadas", ok_n)

# 2.7 prueba de comportamiento: una categoria ausente en entrenamiento NO esta en categories_ y se codifica -1
c_prueba = "purpose"
mask_tr = (X[c_prueba] != "retraining").to_numpy()
m = clone(pipes["arbol"]).fit(X[mask_tr], y[mask_tr])
enc = m.named_steps["prep"].named_transformers_["cat"]
j = cat.index(c_prueba)
cod_test = m.named_steps["prep"].transform(X[~mask_tr].head(3))[:, j]
chk("2.7 categoria ausente en entrenamiento ('retraining') no aparece en categories_ y se codifica -1",
    "retraining" not in enc.categories_[j].tolist() and set(cod_test.tolist()) == {-1.0},
    f"codigos de test={cod_test.tolist()}")
# 2.8 contraste: si se codificara con TODOS los datos, 'retraining' si estaria (demuestra que el metodo distingue)
enc_all = OrdinalEncoder().fit(X[[c_prueba]])
chk("2.8 contraste: ajuste global SI incluiria 'retraining' (el pipeline del ingeniero no lo hace)",
    "retraining" in enc_all.categories_[0].tolist())

# ================================================================ 3. CV (codigo propio)
p("")
p("=== 3. Validacion cruzada estratificada (recalculo propio) ===")
chk("3.1 StratifiedKFold(5, shuffle=True, random_state=42): 5 pliegues, test disjuntos y cubren 1000",
    len(folds) == 5 and sorted(np.concatenate([t for _, t in folds]).tolist()) == list(range(1000)))
prop = [float(y[t].mean()) for _, t in folds]
chk("3.2 cada pliegue test tiene 60 'bad' de 200 (30%), estratificado", all(int(y[t].sum()) == 60 and len(t) == 200 for _, t in folds),
    f"bad por pliegue={[int(y[t].sum()) for _, t in folds]}")
chk("3.3 ningun indice comun entre train y test en cada pliegue",
    all(len(set(tr) & set(te)) == 0 for tr, te in folds))


def metricas_propias(y_true, y_pred):
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    acc = float((y_true == y_pred).mean())
    rec = tp / (tp + fn)
    return acc, rec


def mi_pipeline(est):
    """Pipeline construido por mi (independiente del de src/)."""
    return Pipeline([
        ("pre", ColumnTransformer([("c", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat)],
                                  remainder="passthrough")),
        ("m", est)])


def cv_propia(fabrica):
    accs, recs = [], []
    for tr, te in folds:
        mod = fabrica().fit(X.iloc[tr], y[tr])
        a, r = metricas_propias(y[te], mod.predict(X.iloc[te]))
        accs.append(a)
        recs.append(r)
    return accs, recs


ests = {"arbol": lambda: DecisionTreeClassifier(random_state=42),
        "random_forest": lambda: RandomForestClassifier(random_state=42)}
cv_res = {}
for k in ["arbol", "random_forest"]:
    a_p, r_p = cv_propia(lambda k=k: mi_pipeline(ests[k]()))          # pipeline mio
    a_e, r_e = cv_propia(lambda k=k: clone(pipes[k]))                 # pipeline del ingeniero, mi bucle
    rep = metr["modelos"][k]["cv"]
    cv_res[k] = (a_p, r_p)
    chk(f"3.4 [{k}] exactitud por pliegue (mi pipeline) == metricas.json (exacto)",
        a_p == rep["exactitud_por_pliegue"], f"{a_p}")
    chk(f"3.5 [{k}] recall bad por pliegue (mi pipeline, positivo=bad) == metricas.json (exacto)",
        r_p == rep["recall_bad_por_pliegue"], f"{[round(v, 4) for v in r_p]}")
    chk(f"3.6 [{k}] pipeline del ingeniero con mi bucle == mi pipeline", a_e == a_p and r_e == r_p)
    m1, s1 = float(np.mean(a_p)), float(np.std(a_p, ddof=1))
    m2, s2 = float(np.mean(r_p)), float(np.std(r_p, ddof=1))
    chk(f"3.7 [{k}] media/desv (ddof=1) de exactitud y recall == metricas.json",
        abs(m1 - rep["exactitud"]["media"]) < 1e-12 and abs(s1 - rep["exactitud"]["desv"]) < 1e-12
        and abs(m2 - rep["recall_bad"]["media"]) < 1e-12 and abs(s2 - rep["recall_bad"]["desv"]) < 1e-12,
        f"exactitud {m1:.4f} +/- {s1:.4f} | recall bad {m2:.4f} +/- {s2:.4f} | (ddof=0: {np.std(a_p):.4f}, {np.std(r_p):.4f})")
    # agregado: predicciones fuera de pliegue concatenadas
    pred = np.empty(1000, dtype=int)
    for tr, te in folds:
        pred[te] = mi_pipeline(ests[k]()).fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
    _, rec_ag = metricas_propias(y, pred)
    chk(f"3.8 [{k}] recall agregado fuera de pliegue == reportado", abs(rec_ag - rep["recall_bad_agregado_cross_val_predict"]) < 1e-12,
        f"{rec_ag:.4f}")
    # sanity de la clase positiva: con 'good' como positivo el valor seria distinto
    tn = int(((y == 0) & (pred == 0)).sum())
    rec_good = tn / int((y == 0).sum())
    chk(f"3.9 [{k}] el recall reportado NO es el de 'good' (positivo correcto = bad)",
        abs(rec_good - rep["recall_bad"]["media"]) > 0.05, f"recall good agregado={rec_good:.4f}")

# lectura de resultados: ¿el arbol supera la linea base?
mb = metr["modelos"]
chk("3.10 linea base 'siempre bueno' = 0.70 calculada", abs((y == 0).mean() - 0.70) < 1e-12)

# ================================================================ 4. PARTICION UNICA (propia)
p("")
p("=== 4. Particion unica 75/25, semillas 0..29 (recalculo propio) ===")
part = {}
for k in ["arbol", "random_forest"]:
    acc, rec = [], []
    for s in range(30):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=s)
        assert len(Xte) == 250 and int(yte.sum()) == 75 and len(Xtr) == 750
        mod = mi_pipeline(ests[k]()).fit(Xtr, ytr)
        a, r = metricas_propias(yte, mod.predict(Xte))
        acc.append(a)
        rec.append(r)
    part[k] = (np.array(acc), np.array(rec))
    rep = mb[k]["particion_unica"]
    ok_pa = all(rep["por_semilla"][str(s)]["exactitud"] == acc[s] and rep["por_semilla"][str(s)]["recall_bad"] == rec[s]
                for s in range(30))
    chk(f"4.1 [{k}] 30 pares (exactitud, recall bad) por semilla == metricas.json (exacto)", ok_pa)
    cvm_a, cvm_r = float(np.mean(cv_res[k][0])), float(np.mean(cv_res[k][1]))
    for etq, sl in (("semillas_0_29", slice(0, 30)), ("semillas_0_9", slice(0, 10))):
        a, r = np.array(acc[sl]), np.array(rec[sl])
        b = rep[etq]
        ok = (abs(a.mean() - b["exactitud"]["media"]) < 1e-12 and abs(a.std(ddof=1) - b["exactitud"]["desv"]) < 1e-12
              and a.min() == b["exactitud"]["min"] and a.max() == b["exactitud"]["max"]
              and abs(r.mean() - b["recall_bad"]["media"]) < 1e-12 and abs(r.std(ddof=1) - b["recall_bad"]["desv"]) < 1e-12)
        d = b["dif_exactitud_vs_cv"]
        ok_d = (abs((a.mean() - cvm_a) * 100 - d["media_menos_media_cv_pp"]) < 1e-9
                and abs((a.min() - cvm_a) * 100 - d["min_menos_media_cv_pp"]) < 1e-9
                and abs((a.max() - cvm_a) * 100 - d["max_menos_media_cv_pp"]) < 1e-9)
        dr = b["dif_recall_bad_vs_cv"]
        ok_dr = (abs((r.mean() - cvm_r) * 100 - dr["media_menos_media_cv_pp"]) < 1e-9
                 and abs((r.min() - cvm_r) * 100 - dr["min_menos_media_cv_pp"]) < 1e-9
                 and abs((r.max() - cvm_r) * 100 - dr["max_menos_media_cv_pp"]) < 1e-9)
        chk(f"4.2 [{k}] {etq}: estadisticos y diferencias vs media CV (exactitud y recall) == metricas.json",
            ok and ok_d and ok_dr,
            f"exact. media={a.mean():.4f} dif={(a.mean() - cvm_a) * 100:+.2f}pp rango=[{(a.min() - cvm_a) * 100:+.2f},{(a.max() - cvm_a) * 100:+.2f}]pp | "
            f"recall media={r.mean():.4f} dif={(r.mean() - cvm_r) * 100:+.2f}pp rango=[{(r.min() - cvm_r) * 100:+.2f},{(r.max() - cvm_r) * 100:+.2f}]pp")

chk("4.3 numero de semillas >= 10 (usadas 30, subconjunto 10)", len(mb["arbol"]["particion_unica"]["por_semilla"]) == 30)
# tamano del efecto: ¿cuantas particiones caen fuera de +/- 1 desv CV?
for k in ["arbol", "random_forest"]:
    a = part[k][0]
    sd_cv = float(np.std(cv_res[k][0], ddof=1))
    p(f"     info [{k}]: desv exactitud entre particiones (ddof=1)={a.std(ddof=1):.4f} vs desv entre pliegues CV={sd_cv:.4f}; "
      f"particiones con exactitud > media CV: {int((a > np.mean(cv_res[k][0])).sum())}/30")

# ================================================================ 5. AFIRMACIONES DEL INGENIERO (texto)
p("")
p("=== 5. Afirmaciones del ingeniero ===")
f4 = lambda v: f"{v:.4f}"
ok_md = True
for k, nombre in (("arbol", "Arbol de decision"), ("random_forest", "Random Forest")):
    cv = mb[k]["cv"]
    fila = (f"| {nombre} | {f4(cv['exactitud']['media'])} | {f4(cv['exactitud']['desv'])} | "
            f"{f4(cv['recall_bad']['media'])} | {f4(cv['recall_bad']['desv'])} |")
    ok_md &= fila in metr_md
chk("5.1 tabla CV de metricas.md == metricas.json", ok_md)
chk("5.2 linea base: arbol CV -0.20 pp, RF +5.90 pp (metricas.md seccion 4)",
    abs((np.mean(cv_res['arbol'][0]) - 0.70) * 100 - (-0.20)) < 1e-9
    and abs((np.mean(cv_res['random_forest'][0]) - 0.70) * 100 - 5.90) < 1e-9
    and "diferencia -0.20 pp" in metr_md and "diferencia +5.90 pp" in metr_md)
chk("5.3 'solo se cambia la semilla de particion; semilla modelo fija 42' (config)",
    "random_state=42" in metr["config"]["modelos"] and metr["config"]["semillas_particion"] == list(range(30)))
chk("5.4 config declarada == codigo: cv y particion",
    metr["config"]["cv"] == "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)"
    and metr["config"]["particion"] == "train_test_split(test_size=0.25, stratify=y, random_state=s)")
src_mod = (RAIZ / "src" / "modelos.py").read_text(encoding="utf-8")
src_val = (RAIZ / "src" / "validacion.py").read_text(encoding="utf-8")
chk("5.5 codigo de validacion.py usa clone(pipeline) + scoring 'recall' (positivo por defecto = 1) y pos_label=1 en el agregado",
    "clone(pipeline)" in src_val and '"recall"' in src_val and "pos_label=1" in src_val)
# 5.6 afirmacion 'RF mejora en exactitud pero empeora el recall de bad'
chk("5.6 RF: mayor exactitud CV pero menor recall bad CV que el arbol (hecho observable)",
    np.mean(cv_res['random_forest'][0]) > np.mean(cv_res['arbol'][0]) and np.mean(cv_res['random_forest'][1]) < np.mean(cv_res['arbol'][1]),
    f"exact. {np.mean(cv_res['arbol'][0]):.4f}->{np.mean(cv_res['random_forest'][0]):.4f}; recall {np.mean(cv_res['arbol'][1]):.4f}->{np.mean(cv_res['random_forest'][1]):.4f}")

# ================================================================ resumen
p("")
n_ok = sum(1 for _, o in RESULTADOS if o)
p(f"RESUMEN: {n_ok}/{len(RESULTADOS)} verificaciones OK; fallos: {[n for n, o in RESULTADOS if not o]}")
(AQUI / "verificacion_salida.txt").write_text("\n".join(LINEAS) + "\n", encoding="utf-8")
