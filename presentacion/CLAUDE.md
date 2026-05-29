# TP5 Presentation Guardrails

Este archivo define las reglas que se deben respetar al editar la presentacion de `TP5`, en especial `presentacion/presentacion.tex` y su PDF final.

## Alcance

- Aplica a cualquier cambio sobre la presentacion del `Sistema 1` en este repo.
- Aplica al esqueleto actual y a sus futuras iteraciones con graficos.
- Si hay conflicto entre documentos, manda primero el enunciado oficial.

## Fuentes a consultar y prioridad

1. `../TP5_Enunciado.pdf`
2. `../teoria_kuramoto.md`
3. `../calibracion.md`
4. `../implementacion.md`
5. `../../tp4_sds/importante/guia_presentaciones.pdf`
6. `../../tp4_sds/importante/correcciones_tp2_y_tp3.pdf`
7. `../../tp4_sds/importante/presentacion_tp4.pdf`
8. `../../tp4_sds/presentacion.tex`
9. `../../tp4_sds/importante/tp2_presentacion.pdf`
10. `../../tp4_sds/importante/tp3_presentacion.pdf`

## Objetivo del archivo actual

- `presentacion/presentacion.tex` es un esqueleto de trabajo pedido por el usuario.
- Debe incluir solo estas partes: `Introduccion`, `Modelo`, `Representacion`, `Simulaciones`, `Observables` y `Resultados`.
- En `Resultados`, por ahora debe quedar solo la diapositiva-titulo de la seccion.
- No agregar `Implementacion` ni `Conclusiones` salvo pedido explicito.

## Regla importante del enunciado

- El enunciado oficial del `Sistema 1` dice que la version final de entrega deberia mostrar solo resultados, en muy pocas diapositivas, antes del `Sistema 2`.
- Ese ajuste final no invalida este esqueleto: primero se trabaja con esta estructura y despues se compacta si hace falta.

## Estructura base a respetar

- Usar una portada inicial.
- Separar secciones con una diapositiva que tenga solo el titulo de la seccion.
- No numerar las secciones dentro de la presentacion.
- Numerar las diapositivas.
- Mantener la presentacion en estilo Beamer sobrio, tomando como referencia `../../tp4_sds/presentacion.tex`.

## Reglas de estilo para diapositivas

- No escribir parrafos largos ni mucho texto por slide.
- Evitar frases de relleno; mostrar directamente ecuaciones, variables y definiciones.
- Las figuras no deben tener titulos dentro de la figura ni captions debajo.
- La configuracion del caso mostrado debe ir al costado de la figura o en una linea corta, no como caption.
- Los ejes deben tener nombre claro y unidades entre parentesis cuando corresponda.
- Usar unidades MKS cuando aparezcan unidades.
- El tamano de fuente dentro de figuras y ejes debe ser comparable con el del resto de la diapositiva.
- Usar notacion cientifica correcta; evitar formatos tipo `1E2` o `10^2` en texto plano.
- No mostrar digitos de mas si no aportan informacion frente al error.
- No agregar una seccion final de bibliografia en la presentacion.
- Si hace falta citar, hacerlo en la diapositiva puntual con cita abreviada.
- Vectores en negrita y sin italica.
- Escalares en italica y sin negrita.
- Unidades y numeros sin negrita y sin italica.

## Correcciones arrastradas de TP2 y TP3 que no se pueden repetir

- No sobrecargar slides con texto.
- No redactar cosas del estilo "el modelo se basa principalmente en..." si se puede mostrar directo la formulacion matematica.
- No confundir parametros del modelo con parametros del estudio.
- No listar como parametro de entrada algo que en realidad es solo tiempo total de simulacion o cantidad de pasos, salvo que se estudie explicitamente.
- Aclarar siempre el rango de parametros estudiados.
- En slides con animaciones, dejar un fotograma representativo y link en el PDF.
- No usar leyendas redundantes o incorrectas.
- Si hay una sola serie de datos, evitar leyenda innecesaria.
- Verificar que colores y leyendas correspondan correctamente.
- No poner titulos dentro de las figuras.
- Asegurar analisis cuantitativo real; no quedarse solo en lo cualitativo.
- Basar cualquier conclusion en resultados cuantitativos mostrados.
- Si hay promedios sobre varias corridas, indicar cuantas realizaciones se usaron.
- En implementacion, si alguna vez se agrega, describir el motor y no el postproceso.

## Contenido tecnico minimo del TP5 Sistema 1

- Modelo de Kuramoto:
  - `d theta_i / dt = omega_i + K sum_j A_ij sin(theta_j - theta_i)`
- Distribuciones:
  - `omega_i ~ N(1, 0.1^2)`
  - `theta_i(0) ~ U[0, 2pi)`
- Topologias:
  - completa
  - aleatoria con probabilidad `p`
  - anillo con vecindad `v`
- Parametro de orden:
  - `r(t) = |(1/N) sum_j e^{i theta_j}|`
- Parametros numericos elegidos:
  - `N = 600`
  - `dt = 10^-3`
  - `tSim = 50` para completa y aleatoria
  - `tSim = 1500` para anillo
- Barridos:
  - completa: `K in [0,1]`
  - aleatoria: `p in [0,1]`, `K in [0,1]`
  - anillo: `v in {1,...,10}`, `K in [0,1]`
- Realizaciones:
  - mas de `10` por punto

## Checklist antes de cerrar cambios

- `presentacion/presentacion.tex` mantiene la estructura pedida por el usuario.
- `Resultados` queda como titulo de seccion solo hasta tener graficos.
- No hay secciones extras no pedidas.
- No hay bloques largos de texto.
- Las ecuaciones y observables estan definidos con claridad.
- Los rangos de parametros aparecen explicitamente.
- Se indica cantidad de realizaciones cuando corresponde.
- La presentacion sigue el estilo de `TP4` pero adaptada a `Kuramoto`.
