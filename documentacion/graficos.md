---
title: Documentación de gráficos — TP5 Kuramoto
---

# Documentación de los gráficos

Esta nota describe cada gráfico generado en `tp5-visual/graphs/`, qué representa cada eje y por qué se eligieron esos rangos de barrido.

## Parámetros comunes a todas las simulaciones

Estos valores son idénticos en los tres barridos (ver `run_complete.py`, `run_random.py`, `run_ring.py`):

- `N = 600` osciladores.
- Frecuencias naturales gaussianas con `μ_ω = 1.0`, `σ_ω = 0.1`.
- `dt = 0.001` (paso de integración RK4).
- 12 realizaciones (`seed = 1000..1011`) por punto del barrido; las curvas son promedios y las barras de error son la desviación estándar entre realizaciones.
- `r_estacionario`: promedio de `r(t)` en el último 20 % de la corrida.
- `τ`: primer tiempo en que `r(t)` suavizado alcanza `0.95 · r_estacionario`. Sólo se promedia sobre realizaciones que sincronizan (`r_late > 0.5`) y al menos 3 de las 12.

## Acoplamiento crítico K_c

La ecuación que integra el motor (`Dynamics.java:18`) es

dθ_i/dt = ω_i + K · Σ_{j ∈ vecinos(i)} sin(θ_j − θ_i),

donde K multiplica directamente la suma sobre vecinos (sin dividir por N ni por el grado).

El análisis de campo medio del modelo de Kuramoto predice una transición a sincronización cuando el *empuje total* que siente cada oscilador supera un umbral. En esta convención el empuje promedio sobre el oscilador i escala como `K · ⟨k⟩`, donde ⟨k⟩ es el grado promedio. La condición de transición es

K_c · ⟨k⟩ = σ · √(8/π),

de donde

**K_c = σ · √(8/π) / ⟨k⟩.**

Con σ = 0.1 esto da K_c ≈ 0.16 / ⟨k⟩. **K_c depende de la topología** a través de ⟨k⟩:

| Topología | ⟨k⟩ con N=600 | K_c |
|-----------|---------------|------|
| Completa | 599 | ~2.7·10⁻⁴ |
| Aleatoria p=1 | 599 | ~2.7·10⁻⁴ |
| Aleatoria p=0.1 | ~60 | ~2.7·10⁻³ |
| Aleatoria p=0.01 | ~6 | ~0.03 |
| Aleatoria p=1e-4 | ~0.06 | (red fragmentada) |
| Anillo v=10 | 20 | ~8·10⁻³ |
| Anillo v=1 | 2 | ~0.08 |

Por eso los barridos en K son distintos según la topología: para la red completa se barre desde 1e-4 (la transición está en ~3e-4), para la aleatoria desde 1e-3, y para el anillo desde 1e-2.

### Efectos topológicos más allá de K_c

Que K supere K_c efectivo es **necesario pero no suficiente** para sincronizar globalmente, sobre todo en topologías esparsas:

- **Aleatoria con p < p_c ≈ ln(N)/N ≈ 0.011**: la red está fragmentada (no hay componente gigante). Aunque K → ∞, las fases de componentes desconectadas no pueden comunicarse y r no llega a 1.
- **Anillo con v chico**: aun siendo conexo, el anillo soporta *estados twisted* (la fase da una o más vueltas a lo largo del anillo). Son mínimos locales estables en los que el sistema queda atrapado por tiempo muy largo. Además la información se propaga sólo entre vecinos cercanos, así que los transitorios son enormes (de ahí t_sim = 1500 en lugar de 50).

Estos efectos no se reducen a "más K siempre sincroniza"; la geometría de la red impone restricciones propias.

## ¿Por qué usamos escala logarítmica en K, p y τ?

Porque el barrido de esos parámetros cubre varios órdenes de magnitud y, en escala lineal, los puntos chicos quedarían aplastados contra el origen. Por ejemplo, el barrido en K va de 1e-4 a 1 (4 órdenes); en escala lineal los valores 0.0001, 0.001, 0.01 son visualmente indistinguibles de cero comparados con 1, y la transición de fase se ve como un único salto sin estructura.

En escala logarítmica cada orden de magnitud ocupa el mismo ancho en el eje, los puntos quedan equiespaciados, y se ve la forma real de la transición. Hay además un motivo físico: cuando exploramos un fenómeno cuyo valor crítico no conocemos a priori, lo natural es muestrear logarítmicamente, y el gráfico respeta cómo fue diseñado el barrido.

Por eso:
- `K` y `p` se grafican en log (barridos sobre 3–4 órdenes de magnitud).
- `τ` se grafica en log sólo en la comparativa entre topologías, porque entre completa y anillo difieren en órdenes de magnitud.
- `v` (vecindad del anillo) se grafica en lineal: va de 1 a 10, valores enteros, un único orden de magnitud.
- `r` se grafica en lineal porque está acotado a [0, 1] por definición.

## ¿Por qué no muestreamos linealmente K y p en [0, 1]?

El enunciado pide al menos 10 puntos en [0, 1]. Un muestreo lineal del tipo `K = 0.1, 0.2, ..., 1.0` cumple la letra de la consigna pero produce un gráfico sin información útil.

**Caso K (red completa).** El acoplamiento crítico es K_c ≈ 2.7·10⁻⁴ (ver sección anterior). Un muestreo lineal `K = 0.1, 0.2, ..., 1.0` deja **los 10 puntos varios órdenes de magnitud por encima de K_c** y todos dan `r ≈ 1`. La transición no se ve en ningún lado.

**Caso p (red aleatoria).** Para Erdős–Rényi con N nodos, la red se vuelve conexa alrededor del umbral

p_c ~ ln(N)/N.

Con N = 600 eso da p_c ≈ 0.011, es decir **toda la física interesante ocurre en p ~ 1e-3 – 1e-2**. Un muestreo `p = 0.1, 0.2, ..., 1.0` dejaría todos los puntos dos órdenes de magnitud por encima del umbral: la red ya está conectada en todos ellos y el gráfico sería una línea horizontal en `r ≈ 1`. El enunciado (versión 2) recoge exactamente este punto y prescribe muestrear `p ∈ [1e-4, 1e-1]` con al menos 10 valores distribuidos logarítmicamente.

Por eso el barrido es

p ∈ {1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 0.01, 0.02, 0.05, 0.1},

10 valores log-equiespaciados dentro de [1e-4, 1e-1], con la transición (p_c ≈ 0.011) holgadamente cubierta.

**Criterio general.** Cuando no se conoce a priori dónde está la transición, conviene muestrear logarítmicamente: la resolución es uniforme en todas las escalas y la transición se ve igual si cae en 1e-4 o en 0.5. El muestreo lineal sólo es razonable cuando ya se sabe que el fenómeno vive en una escala particular. En este TP la teoría predice K_c = σ·√(8/π) / ⟨k⟩ (de ~1e-4 en redes densas a ~1e-1 en esparsas) y p_c ≈ ln(N)/N, así que el muestreo log se justifica explícitamente por la física conocida del problema.

---

## 1. Red totalmente conectada (`graphs/complete/`)

Barrido en K = {0, 1e-4, 3e-4, 5e-4, 1e-3, 3e-3, 0.01, 0.03, 0.1, 0.3, 1}. Es una grilla cuasi-logarítmica que cubre cuatro órdenes de magnitud, desde régimen incoherente (`K ≪ K_c`) hasta sincronización completa (`K ≫ K_c`). Se incluye `K = 0` como control (sin acoplamiento, `r` debe quedar acotado a ~1/√N).

Tiempo de simulación corto (`tSim = 50`) porque en la red completa la sincronización ocurre en pocas unidades de tiempo.

### 1.1 `r(t):k.png` — Evolución temporal del parámetro de orden

- **Eje X**: tiempo (0 a 50).
- **Eje Y**: parámetro de orden `r(t) ∈ [0, 1]` (0 = fases uniformes, 1 = todas en fase).
- **Curvas**: una por cada K del barrido, promediadas sobre las 12 seeds. El colormap viridis ordena de K bajo (incoherente, `r` chico) a K alto (sincronización rápida, `r → 1`).

Se ve la transición de fase: para K pequeños `r` queda bajo; al cruzar K_c aparece la rama sincronizada y se estabiliza en un plateau cercano a 1.

### 1.2 `r(K)-estacionario.png` — Curva de bifurcación

- **Eje X**: K en escala **logarítmica** (porque el barrido cubre 4 órdenes de magnitud).
- **Eje Y**: `r_∞(K)` con barras de error (std entre seeds). Limitado a [0, 1.05].

La teoría de Kuramoto predice que, cerca del acoplamiento crítico, el parámetro de orden estacionario crece como

r_∞(K) ≈ √((K − K_c) / K_c)   para K ≳ K_c,

y vale aproximadamente cero para K < K_c. Por eso, si se grafica `r_∞` vs `K` en eje lineal, se observa una rama plana en cero hasta K_c y luego una rama tipo raíz cuadrada que sube hasta saturar cerca de 1: esta es la forma característica de la transición.

En nuestro gráfico el eje K es logarítmico, por lo que esa raíz cuadrada se ve comprimida y aparece visualmente como un **salto abrupto**: los puntos a la izquierda de K_c ≈ 2.7·10⁻⁴ quedan pegados a 0 y los de la derecha cerca de 1.

El punto K = 0 del barrido (incluido como control sin acoplamiento) se descarta de este gráfico porque `log(0) = −∞` y no se puede ubicar en el eje. El código filtra explícitamente los K > 0 antes de graficar.

### 1.3 `t_est(K).png` — Tiempo de sincronización

- **Eje X**: K en escala logarítmica.
- **Eje Y**: τ (tiempo en alcanzar el 95 % de `r_∞`).

Sólo se grafican los K donde al menos 3 de 12 realizaciones sincronizaron, por eso aparecen menos puntos que en `r(K)`. τ diverge cerca de K_c (critical slowing down) y decae para K grande.

---

## 2. Red aleatoria de Erdős–Rényi (`graphs/random/`)

Barridos:
- `p ∈ {1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 0.01, 0.02, 0.05, 0.1}` — escala log, 10 valores en [1e-4, 1e-1] (rango fijado por el enunciado v2); cubre desde redes esparsas y fragmentadas (grado medio `〈k〉 = p·(N−1) ≈ 0.06` en p=1e-4) hasta `p = 0.1` (`〈k〉 ≈ 60`, ya bien conectada).
- `K ∈ {1e-3, 3e-3, 0.01, 0.03, 0.1, 0.3, 1.0}` — escala log, alrededor y por encima de K_c.

Tiempo de simulación `tSim = 50`, igual que la completa: en cuanto la red tenga una componente gigante densa la dinámica se parece a la completa.

### 2.1 `r(p)-k=0.1.png` — Corte a K = 0.1

- **Eje X**: probabilidad de conexión `p`, escala log (porque el barrido es log).
- **Eje Y**: `r_∞(p)` con error bars.

Muestra cómo, fijado K = 0.1 (valor fijado por el enunciado v2), la sincronización depende de la conectividad. Para `p ≲ 1e-3` la red está fragmentada y `r` queda pegado a ~1/√N; la transición ocurre alrededor de `p ≈ p_c ≈ 0.011` y, para `p ≳ 0.02`, la red ya tiene una componente gigante densa y `r → 1`. A este K moderado el salto coincide con el umbral de percolación de Erdős–Rényi, no con el de acoplamiento.

### 2.2 `r(p,K).png` — Mapa de calor `r_∞(p, K)`

- **Eje X**: `p` (log).
- **Eje Y**: `K` (log).
- **Color**: `r_∞` (viridis, 0 → 1).

Diagrama de fases: la frontera diagonal separa la región sincronizada (arriba-derecha, K y p altos) de la incoherente (abajo-izquierda). Ambos ejes son log porque los dos barridos lo son.

### 2.3 `t_est(p,K).png` — Mapa de calor `τ(p, K)`

Mismo dominio que el anterior; color (plasma) representa τ. Las celdas en blanco/NaN son combinaciones (p, K) donde menos de 3 realizaciones sincronizaron y no se calcula τ.

---

## 3. Red en anillo con vecindad v (`graphs/ring/`)

Barridos:
- `v ∈ {1, 2, …, 10}` — entero, escala lineal. Cada nodo conecta a sus `v` vecinos a cada lado (grado = 2v).
- `K ∈ {0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0}` — escala log, finer cerca de K_c porque la transición es más sensible en anillos.

Tiempo de simulación `tSim = 1500` (30× más largo que las otras topologías): los anillos tienen transitorios muy largos porque la información se propaga sólo a vecinos cercanos y los modos de fase tardan en homogeneizarse.

### 3.1 `r(v)-k=0.1.png` — Corte a K = 0.1

- **Eje X**: vecindad `v` (lineal, valores enteros).
- **Eje Y**: `r_∞(v)` con error bars.

A K = 0.1 (valor fijado por el enunciado v2) la sincronización depende fuertemente de cuántos vecinos ve cada oscilador, pero el acoplamiento ya no es lo bastante grande como para sincronizar globalmente dentro del rango de `v` estudiado: `r_∞` crece de forma aproximadamente monótona con `v` (de ~0.06 en `v=1` a ~0.42 en `v=10`) sin llegar a saturar en 1. Con `v = 1` la red es casi 1D y la sincronización global es muy difícil; al aumentar `v` el grafo se acerca a la red completa y `r` sube, pero a este K moderado haría falta `v` (o K) más grande para alcanzar `r ≈ 1`. Las barras de error crecen con `v` porque, cerca de la transición, distintas realizaciones quedan atrapadas en estados parcialmente sincronizados o *twisted* diferentes.

### 3.2 `r(v,K).png` — Mapa de calor `r_∞(v, K)`

- **Eje X**: `v` lineal (entero).
- **Eje Y**: `K` log.
- **Color**: `r_∞`.

Diagrama de fases del anillo: la frontera sincronización/incoherencia se desplaza hacia K más altos cuando `v` baja, mostrando que la topología "anillo estrecho" exige más acoplamiento.

### 3.3 `t_est(v,K).png` — Mapa de calor `τ(v, K)`

Mismo dominio; color (plasma) = τ. Las celdas vacías son puntos donde no sincroniza lo suficiente como para definir τ. Los τ típicos son mucho más grandes que en la completa o aleatoria, por eso `tSim` se subió a 1500.

---

## 4. Comparativa entre topologías (`graphs/tau_comparison.png`)

- **Eje X**: K, escala log.
- **Eje Y**: τ, escala log.
- **Series**: completa, aleatoria (p = 1), anillo (v = 10), cada una con error bars.

Esta primera versión toma la red aleatoria a `p = 1` (equivalente a la red completa) como referencia del régimen plenamente conectado. La curva log-log permite ver el escaleo de τ con K: pendientes similares en completa y aleatoria(p=1), y un offset hacia arriba para el anillo aún con `v = 10`.

Como el enunciado v2 acota la red aleatoria a `p ∈ [1e-4, 1e-1]`, `p = 1` queda fuera de ese rango. Por eso se incluye además una comparativa análoga (`graphs/tau_comparison_p0.1.png`) tomando la red aleatoria en su régimen *más conectado dentro de la especificación*, `p = 0.1`. A `p = 0.1` el grado medio es `〈k〉 ≈ 60` (frente a 599 en la red completa): la red aleatoria sincroniza sistemáticamente más lento que la completa (offset de ~1 orden de magnitud en τ) pero conserva la misma pendiente de τ(K); el anillo (`v=10`, `〈k〉 = 20`) sigue siendo el más lento de los tres, varios órdenes de magnitud por encima.

---

## Resumen de elecciones de eje

| Eje | Tipo | Motivo |
|-----|------|--------|
| `t` | lineal | rango acotado y resolución uniforme |
| `r` | lineal [0, 1.05] | está acotado por definición |
| `K` | log | barrido cubre 3–4 órdenes de magnitud alrededor de K_c ≈ 0.16 |
| `p` | log | barrido cubre 4 órdenes de magnitud (de fragmentada a completa) |
| `v` | lineal | entero pequeño (1–10), no tiene sentido log |
| `τ` (1D) | lineal | rango moderado dentro de una topología |
| `τ` (comparativa) | log | diferencias de órdenes de magnitud entre topologías |
