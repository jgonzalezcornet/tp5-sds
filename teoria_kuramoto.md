# TP5 — Sistema 1: Oscilador de Kuramoto

**Investigación teórica para el TP5 de Simulación de Sistemas (2026Q1)**

Fuentes utilizadas (exclusivas, según instrucciones del enunciado):

1. **Bibliografía web:** *Neuronal Dynamics* (Gerstner, Kistler, Naud, Paninski). Cambridge University Press, online en `https://neuronaldynamics.epfl.ch/online/index.html`. Citaremos como **[ND]** con capítulo y sección.
2. **Teorica5a.pdf** (clase teórica de la cátedra): "Dinámica neuronal y sincronización". Citaremos como **[T5a]** con número de slide (1–14).
3. **TP5_Enunciado.pdf** (consigna). Citaremos como **[E]**.

> **Nota importante sobre la bibliografía web:**
> El libro *Neuronal Dynamics* **no posee un capítulo dedicado al modelo de Kuramoto** (verificado revisando la tabla de contenidos de las 4 partes del libro, capítulos 1–17). El libro cubre la sincronización desde el enfoque de redes de neuronas integrate-and-fire y modelos biofísicos. La información específica del modelo de Kuramoto (ecuación, parámetro de orden) está tomada del Teorica5a.pdf y del propio enunciado. Toda la teoría neurocientífica de contexto (qué es una neurona, qué es la sincronización, conectividad, etc.) se cita de **[ND]**.

---

## 1. Contexto neurocientífico

### 1.1. La neurona como unidad de procesamiento

> *"The elementary processing units in the central nervous system are neurons, which are connected to each other in an intricate pattern."* — **[ND] Ch.1.1**

Una neurona típica está compuesta por tres regiones funcionales **[ND] Ch.1.1**:

- **Dendritas:** *"play the role of the 'input device' that collects signals from other neurons and transmits them to the soma."*
- **Soma:** *"the 'central processing unit' that performs an important non-linear processing step: If the total input arriving at the soma exceeds a certain threshold, then an output signal is generated."*
- **Axón:** *"the 'output device', the axon, which delivers the signal to other neurons."*
- **Sinapsis:** *"The site where the axon of a presynaptic neuron makes contact with the dendrite (or soma) of a postsynaptic cell is the synapse."*

Las neuronas se comunican mediante pulsos eléctricos llamados **potenciales de acción** ("spikes"): *"short electrical pulses"* con *"an amplitude of about 100 mV and typically a duration of 1–2 ms"*. Lo central es que *"the form of the action potential does not carry any information. Rather, it is the number and the timing of spikes which matter."* **[ND] Ch.1.1**.

El cerebro está compuesto por ~10¹¹ neuronas y ~10¹⁴–10¹⁵ conexiones sinápticas, opera en paralelo masivo y consume ~20 W **[T5a, slide 2]**.

### 1.2. Dinámica del potencial de membrana

En reposo, *"the neuron is at rest corresponding to a constant membrane potential u_rest"* con una polarización fuertemente negativa de ~−65 mV **[ND] Ch.1.2**.

Etapas de la actividad neuronal **[T5a, slide 5]**:

1. Potencial de reposo
2. Despolarización
3. Umbral
4. Spike
5. Recuperación

> *"as soon as the membrane potential reaches a critical value ϑ, its trajectory shows a behavior quite different from simple summation"* — produce *"a pulse-like excursion with an amplitude of about 100 mV"* **[ND] Ch.1.2**.

### 1.3. ¿Por qué modelar como osciladores?

Muchas neuronas son intrínsecamente oscilantes: emiten spikes con cierta periodicidad. Si idealizamos cada spike-train como una fase que avanza en el tiempo, podemos describir la actividad de cada neurona mediante una **fase** θᵢ(t) ∈ [0, 2π) y una **frecuencia natural** ωᵢ. La pregunta colectiva es: **¿cuándo se sincronizan?** **[T5a, slide 11]**.

Esto exige distintos niveles de descripción **[T5a, slide 7]**:

1. **Modelos biofísicos detallados** (Hodgkin–Huxley).
2. **Modelos reducidos** (FitzHugh–Nagumo, integrate-and-fire).
3. **Modelos colectivos** (Kuramoto).

> *"Compromiso: Realismo biológico vs simplicidad matemática."* **[T5a, slide 7]**

---

## 2. Modelos neuronales (jerarquía)

### 2.1. Hodgkin–Huxley (biofísico detallado)

*"action potentials are the result of currents that pass through ion channels in the cell membrane."* **[ND] Ch.2**.

Ecuación general:

```
C_m · dV/dt = I − I_Na − I_K − I_L         [T5a, slide 8]
```

> *"the 1952 work combined experimental measurements from squid giant axons with mathematical descriptions using differential equations"* — galardonado con el Nobel de 1963 **[ND] Ch.2**.

**Ventaja:** gran realismo biológico. **Desventaja:** muchos parámetros y alto costo computacional **[T5a, slide 8]**.

### 2.2. FitzHugh–Nagumo (modelo reducido)

> *"FitzHugh and Nagumo demonstrated that 'the four equations of Hodgkin and Huxley can be replaced by two'"* **[ND] Ch.4.2**.

Aprovecha **separación de escalas de tiempo** **[ND] Ch.4.2, Ch.4.6**:

- Eliminación de variable rápida (gating m, quasi-steady-state).
- Combinación de variables lentas (n, h → variable de recuperación w).

Ecuaciones (sistema 2 del TP, no es lo nuestro):

```
dv/dt = v − v³/3 − w + I
dw/dt = ε(v + a − bw)         [T5a, slide 9]
```

Captura excitabilidad, spikes y recuperación. Se puede estudiar mediante **análisis del plano de fase** **[ND] Ch.4.3**. Los puntos fijos son *"the intersection of the u-nullcline and the w-nullcline"*. Cuando I crece, *"the fixed point loses stability as soon as the slope of the u-nullcline becomes larger than ε"*, y emerge un ciclo límite que *"result[s] in voltage pulses similar to a train of action potentials."* **[ND] Ch.4.3**.

### 2.3. Integrate-and-Fire (modelo simplificado)

```
τ · dV/dt = −V + I            [T5a, slide 10]
```

> *"La neurona integra señales. Cuando alcanza un umbral: genera un spike; el potencial se reinicia."* **[T5a, slide 10]**

> *"Idea: Capturar la dinámica esencial con mínima complejidad."* **[T5a, slide 10]**

### 2.4. Kuramoto (modelo colectivo de fase)

Este es **nuestro modelo a implementar**. Describe cada neurona como un **oscilador de fase puro**, ignorando la forma del spike: lo que importa es **cuándo** dispara, no cómo.

```
dθᵢ/dt = ωᵢ + K · Σⱼ Aᵢⱼ · sin(θⱼ − θᵢ)       [T5a, slide 11] [E p.1]
```

> *"Cada neurona tiene una frecuencia natural. Las interacciones favorecen sincronización. Competencia entre: heterogeneidad / acoplamiento."* **[T5a, slide 11]**

---

## 3. El modelo de Kuramoto en detalle (a implementar)

### 3.1. Ecuación de movimiento

Para cada neurona i ∈ {1, …, N} (con N > 500 según [E]):

```
dθᵢ/dt = ωᵢ + K · Σⱼ Aᵢⱼ · sin(θⱼ − θᵢ)
```

donde **[E p.1]**:

- **θᵢ** ∈ [0, 2π): fase de la neurona i.
- **ωᵢ:** frecuencia natural de la neurona i.
  - Distribución: *Normal(μ=1, σ=0.1)*.
- **K** ≥ 0: intensidad de acoplamiento **global**.
- **Aᵢⱼ:** matriz de conectividad (define la topología de la red).

### 3.2. Condiciones iniciales

- **Fases iniciales:** θᵢ(0) uniformes en [0, 2π) **[E p.2]**.
- **Frecuencias naturales:** ωᵢ ~ N(1, 0.1²) **[E p.1]** — fijas durante toda la simulación.

### 3.3. Parámetro de orden (medida de sincronización)

El **parámetro de orden** mide qué tan alineadas están las fases:

```
r(t) = | (1/N) · Σⱼ [cos(θⱼ), sin(θⱼ)] |       [E p.2]
```

Equivalente complejo (más cómodo numéricamente):

```
r(t) · e^(i·ψ(t)) = (1/N) · Σⱼ e^(i·θⱼ)
```

Interpretación **[E p.2]**:
- **r ≈ 0:** fases distribuidas uniformemente → **desincronizado**.
- **r ≈ 1:** todas las fases iguales → **sincronización global**.
- **ψ(t):** fase media del colectivo.

### 3.4. Competencia heterogeneidad ↔ acoplamiento

Hay dos fuerzas opuestas:

- **Heterogeneidad (σ de ωᵢ):** cada oscilador "quiere" girar a su frecuencia natural → dispersa las fases.
- **Acoplamiento (K · Aᵢⱼ):** el término sin(θⱼ − θᵢ) atrae las fases entre sí.

Si K es chico → gana la heterogeneidad → r ≈ 0.
Si K supera un valor crítico **K_c** → emerge sincronización colectiva (transición de fase) → r crece **[T5a, slide 11]**.

**Identificar K_c** experimentalmente es uno de los objetivos del TP **[E p.2, red totalmente conectada]**.

### 3.5. Topologías de red (los 3 casos a estudiar)

**[T5a, slide 12]** muestra las 3 topologías: red completa, anillo y small-world (no se pide).

#### a) Red totalmente conectada (all-to-all)

```
Aᵢⱼ = 1   ∀ i ≠ j
Aᵢᵢ = 0
```

Cada neurona "ve" a todas las demás. **[E p.2]**

Esto es el equivalente neuronal del esquema de conectividad que **[ND] Ch.12.3** llama *"the simplest coupling scheme"*: *"All connections have the same strength."* (Ec. 12.6 del libro: w_ij = J₀/N).

#### b) Red aleatoria (Erdős–Rényi)

```
Aᵢⱼ = 1   con probabilidad p
Aᵢⱼ = 0   con probabilidad 1−p
(i ≠ j)
```

p ∈ [0, 1], al menos 10 valores **[E p.2]**. Conecta con el esquema *"random connectivity with fixed probability"* de **[ND] Ch.12.3**: el número medio de inputs por neurona es ⟨C⟩ = p · N (Ec. 12.7).

#### c) Red anillo (regular, con vecindad v)

```
Aᵢⱼ = 1   si j ∈ {i−v, …, i−1, i+1, …, i+v}  (mod N)
Aᵢⱼ = 0   en otro caso
```

v ∈ [1, 10] **[E p.2]**. Cada neurona se conecta a sus 2v vecinos más cercanos en un anillo (índices periódicos).

### 3.6. Mecanismo de emergencia de oscilaciones colectivas

**[ND] Ch.13.4** describe los regímenes de actividad poblacional que en términos generales describen el sistema:

- **Asynchronous Irregular (AI):** *"neurons in the population fire at different times ('asynchronous' firing) and the distribution of interspike intervals is fairly broad"* → análogo a **r ≈ 0** en Kuramoto.
- **Synchronous Regular (SR):** *"periodic oscillations of the population activity and a sharply peaked interval distribution of individual neurons"* → análogo a **r ≈ 1**.
- **Synchronous Irregular (SI fast/slow):** estados intermedios.

> *"a momentary fluctuation leads to an increase in the total amount of activity in the excitatory population. This causes...an increase in inhibition and...a suppression of excitation. If this feedback loop is strong enough, an oscillation [...] may appear."* — **[ND] Ch.13.4**

En Kuramoto el mecanismo es más directo: el término sin(θⱼ − θᵢ) **siempre** empuja fases cercanas a igualarse (∂/∂θᵢ sin(θⱼ−θᵢ) > 0 cuando |θⱼ−θᵢ| < π/2), produciendo atracción de fase.

**[ND] Ch.14.2.3** analiza la transición a oscilaciones colectivas mediante perturbaciones:

```
A(t) = A₀ + A₁ · e^(iωt + λt)
```

cuando λ > 0, el estado asíncrono pierde estabilidad — análogo a la transición de fase en Kuramoto al cruzar K_c **[ND] Ch.14.2.3**.

### 3.7. Plasticidad sináptica (contexto, no se implementa)

> *"Las conexiones neuronales cambian con la actividad. El orden temporal de los spikes es importante. Si la neurona presináptica dispara antes: potenciación. Si dispara después: depresión."* — STDP, **[T5a, slide 6]**

En este TP **Aᵢⱼ es fija** (no hay plasticidad), pero conceptualmente la sincronización se relaciona con esta idea: spikes coincidentes → potenciación → más sincronización.

---

## 3.8. Tabla de parámetros del Sistema 1 (especificación literal del enunciado)

A continuación se detalla **cada parámetro** del modelo tal como aparece en el enunciado **[E]**, indicando su valor o rango, cómo se determina y si es fijo o se barre.

> **Valores numéricos elegidos para este TP** (calibrados experimentalmente, ver `calibracion.md` o `calibracion.pdf` para todo el detalle):
>
> - **N = 600** (cumple N > 500, costo computacional ~8× menor que N=1000)
> - **dt = 10⁻³** (mínimo estable de RK4, converge a precisión de máquina)
> - **tSim** depende de la topología:
>   - **completa: 50** (sincroniza en t < 1)
>   - **aleatoria: 50** (sincroniza en t < 3 incluso para p chico)
>   - **anillo: 1500** (transitorios largos por propagación local)

### Parámetros del modelo (comunes a las 3 topologías)

| Símbolo | Significado | Valor / Rango | Cómo se determina | Cita |
|---------|-------------|---------------|-------------------|------|
| `N` | Número de neuronas (osciladores) | **N = 600** (consigna: N > 500) | Elegido tras balancear costo (∝ N³) vs calidad estadística (~1/√N). | [E p.1] *"un conjunto de N > 500 neuronas simplificadas interactuantes"* |
| `ωᵢ` | Frecuencia natural de la neurona i | ωᵢ ~ **𝒩(μ=1, σ=0.1)** | Muestreo aleatorio de una **distribución normal con media 1 y desvío estándar 0.1**, una vez por realización. Constantes durante la integración. | [E p.1] *"Las frecuencias naturales deben elegirse aleatoriamente de una distribución normal de valor medio 1 y desvío 0.1"* |
| `θᵢ(0)` | Fase inicial de la neurona i | **U[0, 2π)** | Muestreo aleatorio uniforme en el intervalo [0, 2π), una vez por realización. | [E p.2] *"Las fases iniciales se eligen aleatoriamente en el intervalo [0,2π)"* |
| `K` | Intensidad de acoplamiento global | **K ∈ [0, 1]** | Parámetro de control que se **barre** entre 0 y 1. | [E p.2, red totalmente conectada] *"distintos valores de K = [0,1]"* |
| `Aᵢⱼ` | Matriz de conectividad | Depende de la topología (ver más abajo) | A_ii = 0 siempre. | [E p.1] |
| `dt` | Paso de integración | **dt = 10⁻³** (fijo) | Elegido por test de convergencia: dt ≥ 10⁻² inestable, dt ≤ 10⁻³ precisión de máquina. Ver §4.1. | [E p.1] *"Las simulaciones tendrán un dt fijo e intrínseco de la simulación."* |
| `tSim` | Tiempo total simulado | **Por topología: 50 / 50 / 1500** | Calibrado por análisis de estacionariedad de r(t). Ver `calibracion.md`. | — |

### Parámetros específicos de cada topología

#### (a) Red totalmente conectada

| Símbolo | Valor | Cita |
|---------|-------|------|
| `Aᵢⱼ` | **= 1 ∀ i ≠ j** (A_ii = 0) | [E p.2] *"Considerando Aᵢⱼ = 1 para todo i distinto de j"* |
| Realizaciones por valor de K | **>10**, promediadas | [E p.2] *"Simular varias (>10) realizaciones independientes de las condiciones iniciales y promediar los resultados obtenidos del parámetro de orden"* |

#### (b) Red aleatoria (Erdős–Rényi)

| Símbolo | Valor / Rango | Cita |
|---------|---------------|------|
| `Aᵢⱼ` | **= 1 con probabilidad p, = 0 con probabilidad 1−p** (∀ i ≠ j) | [E p.2] *"Aᵢⱼ = 1 con probabilidad p para todo i distinto de j"* |
| `p` | **p ∈ [0, 1]**, al menos **10 valores** | [E p.2] *"con p = [0,1] (tomar como mínimo 10 valores)"* |
| Realizaciones por (p, K) | **>10** independientes (de red **y** de condiciones iniciales) | [E p.2] *"simular varias (>10) realizaciones independientes de la red y condiciones iniciales y promediar los resultados"* |
| Para análisis r(p) | Fijar **K = 1** | [E p.2] *"Para K = 1, estudiar la sincronización global como función de p"* |
| Mapas 2D | r y τ_s como función de **(p, K)** | [E p.2] |

#### (c) Red anillo

| Símbolo | Valor / Rango | Cita |
|---------|---------------|------|
| `Aᵢⱼ` | **= 1 sii j ∈ {i−v, …, i−1, i+1, …, i+v}** con **índices periódicos** (mod N) | [E p.2] *"Aᵢⱼ = 1 solo si j = [i-v, … , i-1, i+1, …, i+v] (considerando índices periódicos)"* |
| `v` | **v ∈ [1, 10]** (entero, vecindad) | [E p.2] *"con v = [1,10]"* |
| Realizaciones por (v, K) | **>10** independientes (de condiciones iniciales) | [E p.2] *"simular varias (>10) realizaciones independientes de las condiciones iniciales y promediar los resultados obtenidos del parámetro de orden"* |
| Para análisis r(v) | Fijar **K = 1** | [E p.2] *"Para K = 1, estudiar la sincronización global como función de v"* |
| Mapas 2D | r y τ_s como función de **(v, K)** | [E p.2] |

### Resumen de qué se barre y qué se promedia (estructura experimental)

| Topología | Barrido | Promediado sobre | Cantidad de realizaciones |
|-----------|---------|------------------|---------------------------|
| Completa | K ∈ [0, 1] | semillas de θᵢ(0) y ωᵢ | >10 por valor de K |
| Aleatoria | p ∈ [0, 1] (≥10 valores) × K ∈ [0, 1] | semillas de Aᵢⱼ, θᵢ(0), ωᵢ | >10 por par (p, K) |
| Anillo | v ∈ {1,…,10} × K ∈ [0, 1] | semillas de θᵢ(0), ωᵢ | >10 por par (v, K) |

### Observación sobre la matriz Aᵢⱼ

El enunciado no explicita si Aᵢⱼ es **simétrica** (Aᵢⱼ = Aⱼᵢ). Para las tres topologías propuestas:

- **Completa:** trivialmente simétrica (todos 1).
- **Aleatoria:** se puede interpretar de dos formas — (i) cada par {i,j} con i<j se sortea una sola vez y se replica (red **no dirigida**, simétrica), o (ii) cada par ordenado (i,j) con i≠j se sortea independientemente (red **dirigida**). La interpretación más usual en el contexto de Kuramoto y la implícita en el modelo de Erdős–Rényi clásico es la **no dirigida**, así que sortearemos Aᵢⱼ para i<j y replicaremos Aⱼᵢ = Aᵢⱼ.
- **Anillo:** simétrica por construcción (si j está en la vecindad de i, entonces i está en la vecindad de j).

### Constantes que NO aparecen en el modelo (a diferencia del Sistema 2)

A diferencia del modelo FitzHugh–Nagumo (Sistema 2, no es nuestro caso), el Kuramoto **no tiene** corriente externa I, ni parámetros internos del oscilador (a, b, ε). Sólo ωᵢ y K controlan la dinámica.

---

## 4. Integrador: Runge–Kutta de orden 4 (RK4)

Para un sistema dθ/dt = f(θ, t) con θ = (θ₁, …, θ_N), un paso de RK4 con paso h es:

```
k₁ = f(θ(t), t)
k₂ = f(θ(t) + h/2 · k₁, t + h/2)
k₃ = f(θ(t) + h/2 · k₂, t + h/2)
k₄ = f(θ(t) + h   · k₃, t + h)

θ(t + h) = θ(t) + (h/6) · (k₁ + 2k₂ + 2k₃ + k₄)
```

donde la función de derecho es, vectorialmente,

```
f(θ)ᵢ = ωᵢ + K · Σⱼ Aᵢⱼ · sin(θⱼ − θᵢ)
```

**Nota:** las ωᵢ son constantes en el tiempo, por lo que f no depende explícitamente de t (sistema autónomo) → k₂ y k₃ se evalúan en (θ + h/2 · k_prev) sin necesidad de offset temporal en f.

**dt:** fijo durante toda la simulación (requisito del enunciado **[E p.1]**).

### 4.1. Elección de `dt` y `t_sim` — resultado de la calibración

Ni la bibliografía web (*Neuronal Dynamics*) ni el `Teorica5a.pdf` ni el enunciado prescriben valores numéricos. Los determinamos experimentalmente. **El detalle completo está en `calibracion.md` / `calibracion.pdf`** — acá resumimos los resultados.

#### Escala temporal natural del sistema

La única escala temporal es el período de oscilación: T = 2π / ⟨ω⟩ ≈ 6.28.

#### dt — test de convergencia (resumen)

Corrimos la misma realización (N=1000, completa, K=0.5, seed=42) con dt ∈ {10⁻¹, 5·10⁻², 2·10⁻², 10⁻², 5·10⁻³, 2·10⁻³, 10⁻³, 10⁻⁴} y comparamos r(t).

**Resultado:**

| dt | error vs ref. | diagnóstico |
|----|---------------|-------------|
| 10⁻¹, 5·10⁻², 2·10⁻², **10⁻²** | ~1 | **inestable** (RK4 más allá de su región de estabilidad) |
| 5·10⁻³ | 8.7·10⁻⁹ | converge, pero al borde del threshold |
| **10⁻³** | **3.8·10⁻¹⁵** | **precisión de máquina** ✓ |

Hay un **acantilado de estabilidad** entre dt = 10⁻² (inestable) y dt = 5·10⁻³. Elegimos **dt = 10⁻³** por tener margen de seguridad para todo K ∈ [0, 1] y para los casos sparse (donde el threshold puede correrse).

#### tSim — calibración por topología

Tras correr los casos potencialmente más lentos con tSim largo (100 → 500 → 2000), encontramos comportamientos muy distintos según la topología:

- **Completa:** sincroniza en t < 1 (K_c efectivo ~10⁻⁴, todo nuestro rango es supercrítico). → **tSim_completa = 50**.
- **Aleatoria:** sincroniza en t < 3 incluso para p=0.01 (el diámetro del grafo aleatorio es chico). → **tSim_aleatoria = 50**.
- **Anillo:** transitorios MUY largos (estados quiméricos, propagación local). Para v=5, K=0.5/1.0, r(t) sigue evolucionando incluso a t=400 (mínimo local) y recién se estabiliza alrededor de t~1000–1500. → **tSim_anillo = 1500**.

Usar un único tSim global (p.ej. 500) tendría dos problemas: (i) los casos lentos de anillo darían valores **transitorios incorrectos** de r_estacionario; (ii) los casos rápidos (completa, aleatoria) gastarían 30× más cómputo del necesario.

---

## 5. Observables y objetivos del TP

### 5.1. Lo que hay que medir

1. **r(t)** evolución temporal del parámetro de orden, promediado sobre **>10** realizaciones (semillas de fases iniciales y, para red aleatoria, también de Aᵢⱼ).
2. **r_estacionario(K)** — curva de sincronización global vs. acoplamiento. Identificar **K_c**.
3. **Tiempo de sincronización τ_s(K)** — cuánto tarda en llegar al estado estacionario.
4. Para red aleatoria: r y τ_s como función de p y K (mapa 2D).
5. Para red anillo: r y τ_s como función de v y K (mapa 2D).
6. Comparación final del tiempo de sincronización entre las 3 topologías.

### 5.2. Animaciones

Visualizar los N osciladores como puntos en el círculo unitario (con θᵢ como coordenada angular), o como nodos en una grilla coloreados por θᵢ **[E p.2]**.

---

## 6. Lista de chequeo de implementación

- [ ] Generar ωᵢ ~ N(1, 0.1²) una vez por realización.
- [ ] Generar θᵢ(0) ~ U[0, 2π) una vez por realización.
- [ ] Construir Aᵢⱼ según topología (completa / aleatoria con prob. p / anillo con vecindad v).
- [ ] Implementar la función f(θ) que evalúa el lado derecho.
- [ ] Implementar RK4 con dt fijo.
- [ ] Calcular r(t) en cada paso (o cada k pasos para no saturar I/O).
- [ ] Emitir output a archivo de texto (formato a definir: t, r(t), θ₁..θ_N, o reducido).
- [ ] Módulo de análisis y animación independiente del motor de simulación **[E p.1]**.
- [ ] Promediar sobre **>10** realizaciones independientes.

---

## 7. Resumen de citas

| Cita | Fuente | Tema |
|------|--------|------|
| [ND] Ch.1.1 | neuronaldynamics.epfl.ch/online/Ch1.S1.html | Estructura de la neurona, sinapsis, spikes |
| [ND] Ch.1.2 | neuronaldynamics.epfl.ch/online/Ch1.S2.html | Potencial de reposo, despolarización, umbral |
| [ND] Ch.2 | neuronaldynamics.epfl.ch/online/Ch2.html | Hodgkin–Huxley |
| [ND] Ch.4.2 | neuronaldynamics.epfl.ch/online/Ch4.S2.html | Reducción a 2D, FitzHugh–Nagumo |
| [ND] Ch.4.3 | neuronaldynamics.epfl.ch/online/Ch4.S3.html | Plano de fase, nullclines, ciclo límite |
| [ND] Ch.4.6 | neuronaldynamics.epfl.ch/online/Ch4.S6.html | Separación de escalas de tiempo |
| [ND] Ch.12.3 | neuronaldynamics.epfl.ch/online/Ch12.S3.html | Esquemas de conectividad (all-to-all, random) |
| [ND] Ch.13.4 | neuronaldynamics.epfl.ch/online/Ch13.S4.html | Regímenes AI / SR / SI, mecanismo de oscilación |
| [ND] Ch.14.2.3 | neuronaldynamics.epfl.ch/online/Ch14.S2.html | Inestabilidad del estado asíncrono |
| [T5a] | Teorica5a.pdf, slides 1–14 | Modelo de Kuramoto explícito, topologías |
| [E] | TP5_Enunciado.pdf | Especificación del problema |
