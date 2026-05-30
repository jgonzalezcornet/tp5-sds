"""
Estilo global para los gráficos del TP5.

Reglas (de GuiaPresentaciones.pdf):
- Sin títulos en las figuras (sólo labels de ejes).
- Labels en palabras, no símbolos. Unidades entre paréntesis sólo cuando aplica.
- Tamaño de letra ≥ 20.
- Números de los ejes derechos (sin rotación).
- Datos como símbolos identificables; líneas sólo como "guía para el ojo".
"""
import matplotlib as mpl

mpl.rcParams["font.size"] = 20
mpl.rcParams["axes.labelsize"] = 22
mpl.rcParams["xtick.labelsize"] = 20
mpl.rcParams["ytick.labelsize"] = 20
mpl.rcParams["legend.fontsize"] = 18

mpl.rcParams["axes.titlesize"] = 0
mpl.rcParams["axes.titlepad"] = 0

mpl.rcParams["figure.figsize"] = (8.5, 6.5)
mpl.rcParams["figure.dpi"] = 100
mpl.rcParams["savefig.dpi"] = 150
mpl.rcParams["savefig.bbox"] = "tight"

mpl.rcParams["axes.grid"] = True
mpl.rcParams["grid.alpha"] = 0.3
mpl.rcParams["axes.spines.top"] = False
mpl.rcParams["axes.spines.right"] = False

mpl.rcParams["xtick.direction"] = "out"
mpl.rcParams["ytick.direction"] = "out"
mpl.rcParams["lines.markersize"] = 9
mpl.rcParams["lines.linewidth"] = 2

mpl.rcParams["errorbar.capsize"] = 5
