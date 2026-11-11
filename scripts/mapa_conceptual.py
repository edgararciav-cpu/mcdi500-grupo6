"""Dibuja el mapa conceptual del flujo reproducible del proyecto (docs/figuras/mapa_conceptual.png).

Seis tipos de elemento, cada uno con su color; borde continuo = implementado, borde punteado =
proyectado para las Fases 3 y 4. Las flechas llevan un verbo que dice cómo se relacionan.

Uso (desde la raíz del proyecto):
    .\\.venv\\Scripts\\python.exe scripts\\mapa_conceptual.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D

COLOR = {
    "herramientas": "#3B6FD8",
    "flujo reproducible": "#2E9E6A",
    "procesos": "#E08A2E",
    "decisiones técnicas": "#8E5BC9",
    "organización del repositorio": "#5D6D7E",
    "estructura del notebook": "#C0392B",
}

# Columnas y filas de la grilla
C1, C2, C3, C4, C5 = 1.5, 4.6, 7.7, 10.8, 13.9
F = {1: 8.6, 2: 6.9, 3: 5.2, 4: 3.5, 5: 1.8, 6: 0.2}

# id: (texto, tipo, x, y, proyectado)
NODOS = {
    "venv":  ("Python 3.14 + .venv\nrequirements.txt (105 versiones fijas)", "herramientas", C1, F[1], False),
    "jup":   ("JupyterLab\nkernel «Python (mcdi500)»", "herramientas", C1, F[2], False),
    "pd":    ("pandas · NumPy\nscikit-learn · matplotlib", "herramientas", C1, F[3], False),
    "src":   ("src/utilidades.py\nfunciones, clase, excepción", "organización del repositorio", C1, F[4], False),
    "git":   ("Git (una sola identidad)\n→ GitHub mcdi500-grupo6", "herramientas", C1, F[5], False),
    "repo":  ("F1/ F2/ F3/ F4/ · data/ · docs/\nsrc/ · scripts/ · README", "organización del repositorio", C1, F[6], False),

    "raw":   ("data/raw · incidencias\n(personas codificadas, SHA-256)", "flujo reproducible", C2, F[1], False),
    "f1":    ("F1 · Definición\nproblema, entorno, ficha", "flujo reproducible", C2, F[2], False),
    "f2":    ("F2 · Preprocesamiento\nobtener → validar → guardar", "flujo reproducible", C2, F[3], False),
    "proc":  ("data/processed\nlimpio · modelo · recurrencia", "flujo reproducible", C2, F[4], False),
    "f3":    ("F3 · Algoritmos y POO", "flujo reproducible", C2, F[5], True),

    "nb":    ("Celda narrativa (qué y por qué)\n→ código → evidencia", "estructura del notebook", C3, F[2], False),
    "test":  ("Pruebas normal, límite\ny excepción (assert)", "estructura del notebook", C3, F[3], False),
    "f4":    ("F4 · Visualización\ny comunicación", "flujo reproducible", C3, F[5], True),
    "rama":  ("Rama f2-pipeline\n+ pull request", "organización del repositorio", C3, F[6], False),

    "anon":  ("Anonimizar personas\n(sitios con mnemónico real)", "procesos", C4, F[1], False),
    "medir": ("Medir calidad sin corregir\n(tildes, vacíos, TT)", "procesos", C4, F[2], False),
    "limp":  ("Limpiar · transformar\n· escalar", "procesos", C4, F[3], False),
    "rec":   ("Recurrencia por sitio\n(fusión recursiva)", "procesos", C4, F[4], False),

    "d_na":  ("Duración vacía: no se\ninventa en el limpio", "decisiones técnicas", C5, F[2], False),
    "d_esc": ("Standard en log(duración)\nMinMax en conteos", "decisiones técnicas", C5, F[3], False),
    "d_up":  ("Uptime = P1, P2, P3, P3E\n(sin canceladas)", "decisiones técnicas", C5, F[4], False),
    "d_sit": ("Un sitio por fila\n(2 espacios = Q sitios)", "decisiones técnicas", C5, F[5], False),
}

# (desde, hasta, verbo)
ARISTAS = [
    ("venv", "jup", "ejecuta"), ("jup", "pd", "usa"), ("pd", "f2", "procesa en"), ("src", "f2", "es importado por"),
    ("git", "repo", "versiona"), ("rama", "repo", "se integra a"),
    ("raw", "f1", "alimenta"), ("f1", "f2", "define el alcance de"), ("f2", "proc", "produce"),
    ("proc", "f3", "entrada de"), ("proc", "f4", "entrada de"),
    ("nb", "f1", "ordena"), ("nb", "test", "incluye"), ("test", "f2", "valida"),
    ("anon", "raw", "genera"), ("anon", "medir", "luego"), ("medir", "limp", "orienta"), ("limp", "rec", "prepara"),
    ("rec", "proc", "escribe"),
    ("d_na", "limp", "guía"), ("d_esc", "limp", "guía"), ("d_up", "rec", "filtra"), ("d_sit", "rec", "define la unidad de"),
]

ANCHO, ALTO = 2.6, 1.05


def borde(x1, y1, x2, y2, margen=0.06):
    """Punto donde la recta que va del centro (x1, y1) hacia (x2, y2) sale de la caja."""
    dx, dy = x2 - x1, y2 - y1
    tx = (ANCHO / 2 + margen) / abs(dx) if dx else float("inf")
    ty = (ALTO / 2 + margen) / abs(dy) if dy else float("inf")
    t = min(tx, ty)
    return x1 + t * dx, y1 + t * dy


def dibujar(ruta):
    fig, ax = plt.subplots(figsize=(17, 10.5))
    ax.set_xlim(0, 15.4)
    ax.set_ylim(-0.5, 9.4)
    ax.axis("off")
    for texto, tipo, x, y, proyectado in NODOS.values():
        caja = FancyBboxPatch((x - ANCHO / 2, y - ALTO / 2), ANCHO, ALTO, boxstyle="round,pad=0.04,rounding_size=0.12",
                              facecolor=COLOR[tipo] + "22", edgecolor=COLOR[tipo], linewidth=2,
                              linestyle="--" if proyectado else "-")
        ax.add_patch(caja)
        ax.text(x, y, texto, ha="center", va="center", fontsize=8.8, color="#1B1B1B")
    for origen, destino, verbo in ARISTAS:
        _, _, x1, y1, _ = NODOS[origen]
        _, _, x2, y2, _ = NODOS[destino]
        sx, sy = borde(x1, y1, x2, y2)
        ex, ey = borde(x2, y2, x1, y1)
        ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.2, shrinkA=0, shrinkB=0))
        ax.text((sx + ex) / 2, (sy + ey) / 2, verbo, fontsize=7.8, color="#333333", ha="center", va="center",
                style="italic", bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none"))
    ax.set_title("Mapa conceptual del flujo reproducible · Fallas recurrentes de transmisión (MCDI500, Grupo 6)",
                 fontsize=13, pad=12)
    leyenda = [Patch(facecolor=c + "22", edgecolor=c, linewidth=2, label=t) for t, c in COLOR.items()]
    leyenda += [Line2D([0], [0], color="#333333", lw=2, label="borde continuo: implementado (F1 y F2)"),
                Line2D([0], [0], color="#333333", lw=2, linestyle="--", label="borde punteado: proyectado (F3 y F4)"),
                Line2D([0], [0], color="#555555", lw=1, marker=">", label="flecha con verbo: relación entre elementos")]
    ax.legend(handles=leyenda, loc="lower right", bbox_to_anchor=(1.0, -0.03), fontsize=8, ncol=2, frameon=True,
              title="Leyenda", title_fontsize=9)
    fig.tight_layout()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=160)
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    print("Mapa guardado en", dibujar(raiz / "docs" / "figuras" / "mapa_conceptual.png").relative_to(raiz))
