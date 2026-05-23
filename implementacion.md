# TP5 — Sistema 1: Implementación del motor de simulación (Java)

Motor de simulación del modelo de Kuramoto en Java, modularizado en 6 archivos en `motor/` (total ~7.6 kB, holgadamente bajo el límite de 20 kB del enunciado). Sólo motor de simulación: el análisis y la animación se hacen aparte sobre los CSV generados.

---

## 1. Estructura del código

Seis clases, cada una con una sola responsabilidad. Sin dependencias externas (solo `java.io` y `java.util`).

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `Config.java` | `Config` (record) | Lleva todos los parámetros + parseo de CLI (`fromArgs`). |
| `Network.java` | `Network` + enum `Topology` | Construye la lista de vecinos (`int[][]`) según la topología. |
| `Dynamics.java` | `Dynamics` | Evalúa el campo f(θ)ᵢ = ωᵢ + K · Σⱼ∈vec(i) sin(θⱼ − θᵢ). |
| `Integrator.java` | `Integrator` | Un paso de RK4. Tiene buffers preasignados (`k1..k4`, `tmp`). |
| `Output.java` | `Output` | Escribe la cabecera y cada fila del CSV (computa r(t) en cada fila). |
| `KuramotoSim.java` | `KuramotoSim` | `main`: orquesta inicialización, loop temporal y volcado. |

**Dirección de las dependencias** (sin ciclos):

```
KuramotoSim  ──┬──→ Config
               ├──→ Network ──→ Topology
               ├──→ Integrator ──→ Dynamics
               └──→ Output ──→ Config
```

### Estructura de datos elegida

En vez de guardar Aᵢⱼ como matriz densa N×N (250 000 entradas para N=500), guardamos para cada nodo i un **arreglo de índices de sus vecinos** (`int[] nbr[i]`). Esto:

- Permite recorrer sólo los vecinos reales en `deriv` → mucho más rápido para redes esparsas (anillo con v=1, aleatoria con p chico).
- Es equivalente a la matriz para el caso completo (N−1 vecinos por nodo).
- Aprovecha el hecho de que el grafo no cambia durante la simulación.

### Reproducibilidad: dos semillas

- `seed`: controla `ωᵢ` y `θᵢ(0)`. Misma `seed` → mismas condiciones iniciales **independientemente de la topología**.
- `netSeed`: controla el sorteo de Aᵢⱼ (sólo relevante para topología `random`). Default = `seed`.

Esto facilita comparar topologías sobre la misma condición inicial, y promediar sobre realizaciones independientes de la red o de las condiciones iniciales por separado.

---

## 2. Parámetros (CLI)

Todos parametrizables vía `--clave valor`. Default entre paréntesis.

### Parámetros del modelo

| Flag | Tipo | Default | Descripción |
|------|------|---------|-------------|
| `--N` | int | 500 | Número de osciladores. El enunciado pide N > 500. |
| `--K` | double | 1.0 | Intensidad de acoplamiento global K ∈ [0, 1]. |
| `--topology` | string | `complete` | Una de `complete` / `random` / `ring` (case-insensitive). |
| `--p` | double | 0.5 | Probabilidad de conexión (solo `random`). |
| `--v` | int | 1 | Vecindad a cada lado del anillo (solo `ring`), v ∈ [1, 10]. |
| `--muOmega` | double | 1.0 | Media de la normal para ωᵢ. |
| `--sigmaOmega` | double | 0.1 | Desvío estándar de la normal para ωᵢ. |

### Parámetros numéricos

| Flag | Tipo | Default | Descripción |
|------|------|---------|-------------|
| `--dt` | double | 0.01 | Paso de integración (fijo). Probar dt = 10⁻ˣ con x ∈ {1, 2, 3, 4}. |
| `--tSim` | double | 100.0 | Tiempo total simulado. |

### Parámetros de salida y reproducibilidad

| Flag | Tipo | Default | Descripción |
|------|------|---------|-------------|
| `--seed` | long | 42 | Semilla para ωᵢ y θᵢ(0). |
| `--netSeed` | long | = seed | Semilla para Aᵢⱼ (solo `random`). |
| `--output` | string | `kuramoto.csv` | Archivo de salida. |
| `--dumpEvery` | int | 1 | Vuelca al CSV cada `dumpEvery` pasos (1 = cada paso). |
| `--dumpPhases` | boolean | true | Si `false`, solo escribe `t, r` (mucho más liviano). |

---

## 3. Formato del archivo de salida (CSV)

```
# N=500 K=1.000000 dt=0.010000 tSim=100.000000 topology=COMPLETE p=0.500000 v=1 muOmega=1.000000 sigmaOmega=0.100000 seed=42 netSeed=42 dumpEvery=1
t,r,theta_0,theta_1,...,theta_{N-1}
0.0,0.0763...,1.4234...,3.1415...,...
0.01,0.0791...,1.4334...,3.1525...,...
...
```

- **Primera línea:** comentario (empieza con `#`) con todos los parámetros, para autodocumentar el archivo.
- **Segunda línea:** nombres de columna.
- **Filas siguientes:** valores. Si `--dumpPhases false`, solo aparecen `t` y `r`.

### Por qué incluir r ya calculado

`r(t)` se computa dentro del motor en `writeRow` (~O(N) por fila). Volcarlo evita que el postproceso tenga que recomputarlo desde las fases, y permite el modo "solo r" con `--dumpPhases false` para los barridos donde no se necesita la animación.

---

## 4. Compilación y ejecución

**Configuración del TP** (calibrada experimentalmente, ver `calibracion.md`):
- N = 600
- dt = 10⁻³
- tSim = 50 (completa, aleatoria) / 1500 (anillo)

```bash
cd motor
javac *.java   # compila las 6 clases en .class

# Ejemplo 1: red completa, K=0.5
java KuramotoSim --N 600 --K 0.5 --topology complete \
                 --dt 0.001 --tSim 50 \
                 --seed 42 --output complete_K0.5_seed42.csv \
                 --dumpEvery 10 --dumpPhases true

# Ejemplo 2: red aleatoria, K=1, p=0.3, semillas separadas
java KuramotoSim --N 600 --K 1.0 --topology random --p 0.3 \
                 --dt 0.001 --tSim 50 \
                 --seed 42 --netSeed 7 \
                 --output random_p0.3_K1_s42_n7.csv \
                 --dumpPhases false

# Ejemplo 3: red anillo, v=3 — OJO: tSim mucho mayor por la física del anillo
java KuramotoSim --N 600 --K 0.7 --topology ring --v 3 \
                 --dt 0.001 --tSim 1500 \
                 --seed 42 --output ring_v3_K0.7.csv \
                 --dumpEvery 100
```

---

## 5. Algoritmo

### 5.1. Inicialización

1. Sortear ωᵢ ~ 𝒩(1, 0.1²) con la RNG de `seed` (usando `nextGaussian()`).
2. Sortear θᵢ(0) ~ 𝒰[0, 2π) con la misma RNG.
3. Construir lista de vecinos según topología (con RNG de `netSeed` si corresponde).

### 5.2. Loop principal — RK4

Sea f(θ)ᵢ = ωᵢ + K · Σⱼ∈vec(i) sin(θⱼ − θᵢ). Para cada paso:

```
k1 = f(θ)
k2 = f(θ + dt/2 · k1)
k3 = f(θ + dt/2 · k2)
k4 = f(θ + dt   · k3)
θ ← θ + dt/6 · (k1 + 2·k2 + 2·k3 + k4)
```

El sistema es autónomo (f no depende explícitamente de t), por eso `deriv` no recibe un argumento de tiempo.

**Preasignación:** los buffers `k1..k4` y `tmp` se alocan una vez fuera del loop. No se asigna memoria por iteración.

### 5.3. Cálculo de r(t)

```
cx = (1/N) · Σⱼ cos(θⱼ)
cy = (1/N) · Σⱼ sin(θⱼ)
r  = √(cx² + cy²)
```

### 5.4. Construcción de la matriz de conectividad

- **complete:** `nbr[i] = {0, 1, ..., N-1} \ {i}` — N−1 vecinos por nodo.
- **random:** para cada par (i, j) con i < j, sortear `nextDouble() < p`. Si sí, agregar j a `nbr[i]` **y** i a `nbr[j]` (red **no dirigida** — el enunciado no exige una interpretación, optamos por simétrica por convención).
- **ring:** `nbr[i] = {(i−v) mod N, ..., (i−1) mod N, (i+1) mod N, ..., (i+v) mod N}` — exactamente 2v vecinos. La aritmética usa `((i-d) % N + N) % N` para manejar correctamente índices negativos en Java.

---

## 6. Consideraciones de performance

Para N=500, t_sim=100, dt=0.01 (10 000 pasos):

| Topología | Vecinos por nodo | Ops/paso (4 evaluaciones f) | Tiempo aprox. |
|-----------|------------------|-----------------------------|---------------|
| Completa | 499 | ~10⁶ | segundos |
| Aleatoria (p=0.3) | ~150 | ~3·10⁵ | rápido |
| Anillo (v=3) | 6 | ~1.2·10⁴ | muy rápido |

El cuello de botella en red completa es la doble suma para sin(θⱼ − θᵢ). No vale la pena ofuscar el código con optimizaciones (FFT, separabilidad sin/cos) para este tamaño de problema.

---

## 7. Lo que el motor **no hace** (a propósito)

- No genera gráficos.
- No genera animaciones.
- No calcula τ_s (tiempo de sincronización), solo emite r(t); el umbral y la detección del estacionario se hacen en postproceso.
- No promedia sobre realizaciones; eso se hace ejecutando el motor N veces con distintas `--seed` y agregando los CSV en postproceso.
- No barre K, p, v automáticamente; cada combinación se corre como un proceso separado (fácilmente paralelizable con `xargs -P` o un script).

Esto sigue al pie de la letra el requisito de la consigna: *"el análisis y módulo de animación se ejecuta en forma independiente tomando estos archivos de texto como input."* (Enunciado, p.1).

---

## 8. Resumen de archivos generados

| Archivo | Contenido | Tamaño |
|---------|-----------|--------|
| `motor/Config.java` | Record de parámetros + parseo CLI. | ~1.8 kB |
| `motor/Network.java` | Topología + construcción de vecinos. | ~1.8 kB |
| `motor/Dynamics.java` | Campo f(θ) de Kuramoto. | ~0.5 kB |
| `motor/Integrator.java` | RK4 con buffers preasignados. | ~1.0 kB |
| `motor/Output.java` | CSV: cabecera + filas, computa r(t). | ~1.3 kB |
| `motor/KuramotoSim.java` | `main`, orquestación. | ~1.2 kB |
| `kuramoto.csv` (o el que se indique con `--output`) | Salida CSV: cabecera con parámetros + columnas `t, r, [θ_i...]`. | — |

**Total fuente: ~7.6 kB** (límite del enunciado: 20 kB).
