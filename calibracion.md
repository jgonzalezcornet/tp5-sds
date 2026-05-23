# TP5 — Calibración de parámetros numéricos (N, dt, tSim)

Este documento explica **cómo elegimos** los valores numéricos del TP y **por qué**, basado en experimentos de convergencia y estacionariedad. Resultado final:

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| **N** | **600** | Cumple N > 500 con costo computacional manejable. |
| **dt** | **10⁻³** | Por test de convergencia RK4 (mínimo estable, máquina-precisión). |
| **tSim_completa** | **50** | Sincroniza en t < 1. Margen 50×. |
| **tSim_aleatoria** | **50** | Sincroniza en t < 3 incluso para p chico. Margen ~15×. |
| **tSim_anillo** | **1500** | Transitorios lentos por propagación local (estados quiméricos). |

**Costo total estimado del TP:** ~25 min con 4 cores paralelos (vs. ~50 h con N=1000, tSim=500 global).

---

## 1. Elección de N

**Constraint del enunciado:** N > 500.

### Costo computacional vs N

Benchmark del motor optimizado (red completa, K=0.8, tSim=50):

| N | Tiempo (s) | Escalado |
|---|------------|----------|
| 500 | 2.92 | 1× |
| 750 | 6.67 | 2.3× (≈ N²) |
| 1000 | 12.32 | 4.2× |
| 1500 | 28.37 | 9.7× |

El costo por paso escala como N² (cuello de botella: doble bucle de la red completa). Como además el tSim requerido en anillo escala como N (propagación local), el **costo total escala como N³**.

### Calidad estadística

Las fluctuaciones del parámetro de orden escalan como 1/√N:
- N=600: ~4.1%
- N=1000: ~3.2%

Diferencia despreciable. La transición K_c se ve igual de clara en ambos.

### Conectividad de la red aleatoria

Para asegurar que un sorteo de Erdős–Rényi sea conectado se necesita ⟨k⟩ > log(N):
- N=600: log(600) ≈ 6.4 → p_min ≈ 0.011
- N=1000: log(1000) ≈ 6.9 → p_min ≈ 0.007

Con N=600 y p chico (0.01), la red puede estar marginalmente desconectada. Aceptable porque se promedia sobre >10 realizaciones independientes.

### Veredicto: **N = 600**

Cumple consigna, costo 8× menor que N=1000, calidad estadística suficiente.

---

## 2. Elección de dt

### Test de convergencia

**Setup:** N=1000, completa, K=0.5, seed=42, tSim=20. Misma realización (mismas ωᵢ y θᵢ(0)) corrida con dt = 10⁻¹, 5·10⁻², 2·10⁻², 10⁻², 5·10⁻³, 2·10⁻³, 10⁻³, 10⁻⁴. Comparamos r(t) tomando dt=10⁻⁴ como referencia.

![Convergencia dt](postproc/dt_convergence.png)

### Resultados cuantitativos

| dt | max\|Δr\| vs ref | Diagnóstico |
|----|------------------|-------------|
| 10⁻¹ | 0.987 | **inestable** (catastrófico) |
| 5·10⁻² | 0.981 | inestable |
| 2·10⁻² | 0.977 | inestable |
| 10⁻² | 0.984 | inestable |
| 5·10⁻³ | 8.7·10⁻⁹ | converge |
| 2·10⁻³ | 3.9·10⁻¹⁵ | precisión de máquina |
| **10⁻³** | **3.8·10⁻¹⁵** | **precisión de máquina** |

**Hay un acantilado de estabilidad entre dt = 10⁻² (inestable) y dt = 5·10⁻³ (converge).** Por debajo del threshold, la convergencia es a precisión de máquina (~10⁻¹⁵).

### Por qué 10⁻³ y no 5·10⁻³

- 5·10⁻³ está apenas debajo del threshold. Para K más alto que 0.5 o N más grande, el threshold se corre más bajo (condición RK4: dt ≲ 2.78/(K·N)).
- 10⁻³ asegura estabilidad para **todo el barrido K ∈ [0, 1]** sin sobresaltos.
- 10⁻³ es un valor "limpio" y conservador.

### Veredicto: **dt = 10⁻³**

---

## 3. Elección de tSim

### Cómo lo determinamos

Corrimos los **casos potencialmente más lentos** de cada topología con tSim largo (100 → 500 → 2000) hasta ver dónde realmente se estabiliza r(t).

### Casos analizados

![tSim a tSim=500 con N=1000](postproc/tsim_calibration.png)

Y para confirmar el estado asintótico, corridas más largas:

![Comportamiento asintótico a tSim=2000 con N=600](postproc/tsim_n600_long.png)

### Resultados por topología

#### Red completa

Sincroniza **instantáneamente** (t < 1) para cualquier K > 0.05. Esto es porque K_c efectivo para all-to-all con N grande es K_c ≈ 2/(π·N·g(0)) ≈ 10⁻⁴ — todo nuestro rango K ∈ [0, 1] está varios órdenes de magnitud por encima.

→ **tSim_completa = 50** (50× margen sobre el transitorio observado).

#### Red aleatoria

Incluso con p=0.01 (la más sparse), sincroniza en t ≈ 2–3 (el grafo aleatorio tiene diámetro ~log(N)/log(⟨k⟩), muy chico). Para p mayores, sincroniza en t < 1.

→ **tSim_aleatoria = 50** (~15× margen).

#### Red anillo

**Aquí está el problema.** El anillo tiene propagación **local**: información viaja sólo a 2v vecinos a cada lado. El tiempo de propagación del transitorio escala como τ ~ N/v.

Además, para v intermedio (3–7) y K moderado (0.5–1), aparecen **estados quiméricos** y ondas viajeras con transitorios muy largos.

Comportamiento asintótico confirmado a tSim=2000:

| Caso | r en t=300 | r asintótico (t≈1500) | Δ |
|------|-----------|----------------------|---|
| ring v=5 K=1.0 | ~0.2 (mínimo local!) | 0.54 | 0.34 |
| ring v=5 K=0.5 | ~0.25 (bajando) | 0.45 | 0.20 |
| ring v=10 K=0.1 | ~0.1 (subiendo) | 0.37 | 0.27 |
| ring v=1 K=0.5 | ~0.06 (oscilante) | 0.05 (oscilante) | OK |

Si midiéramos r_estacionario en t=300, daríamos **valores transitorios incorrectos** para los casos lentos.

→ **tSim_anillo = 1500** (cubre los transitorios observados, con algo de margen).

---

## 4. Resumen ejecutivo para la cátedra / writeup

> "Calibramos los parámetros numéricos mediante experimentos de convergencia:
> - **dt = 10⁻³**: elegido tras un test de convergencia con dt = 10⁻ˣ, x ∈ {1, 2, 3, 4} sobre red completa N=1000 K=0.5. Para dt ≥ 10⁻² el integrador RK4 es inestable; para dt ≤ 10⁻³ converge a precisión de máquina.
> - **N = 600**: cumple N > 500 con costo ~8× menor que N=1000 y calidad estadística similar (fluctuaciones de r ~ 4%).
> - **tSim por topología**, según el transitorio observado en pruebas piloto: 50 unidades para red completa y aleatoria (sincronización en t < 5), 1500 unidades para anillo (transitorios largos por propagación local en topologías con vecindad pequeña)."

---

## 5. Archivos relevantes

- `postproc/dt_convergence.py` — script del test de convergencia de dt
- `postproc/tsim_calibration.py` — script del análisis de estacionariedad
- `postproc/tsim_n600_long.py` — script de la verificación asintótica a N=600
- `outputs/dt_test/` — CSVs de las 8 corridas con distintos dt
- `outputs/tsim_test/` — CSVs de las 11 corridas con N=1000
- `outputs/tsim_test_n600/` — CSVs de las corridas con N=600 (cortas + largas)
- `postproc/*.png` — gráficos generados
