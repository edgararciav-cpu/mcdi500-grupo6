# Bitácora de decisiones · Fase 2

Generada por `F2/F2_Preprocesamiento.ipynb`. Una fila por decisión, con su motivo y su impacto medido.

| Paso | Decisión | Motivo | Impacto medido |
|---|---|---|---|
| 2.3 | Conservar las filas con TT repetido | un TT agrupa varias caídas del mismo elemento en fechas distintas; la clave TT + elemento + inicio es única | 0 duplicados exactos; 1081 TT en 2708 filas conservadas |
| 2.4 | Conservar las duraciones atípicas (IQR) | son caídas largas reales, en buena parte P3E; son las que bajan el uptime | 2.348 atípicas sobre 892 min (14.5 %) |
| 3.2 | Reparar la doble codificación del texto | el exporte guardó el UTF-8 como si fuera cp1252 (Windows) | 43.811 celdas con tildes rotas → 0 |
| 3.3 | Unificar vacíos y variantes de escritura | NA, N/A, na, no aplica y 0000-00-00 significan lo mismo; Pendiente y PENDIENTE también | 29.667 marcadores → NaN; 252 valores reescritos en 2 columnas |
| 3.4 | Quitar columnas casi vacías y fuera de alcance | más de 95 % sin dato, o pertenecen a la clasificación GMI o al foco de energía | 49 → 29 columnas (16 casi vacías, 4 fuera de alcance) |
| 3.5 | Convertir fechas, duración, conteos y banderas a su tipo | el exporte entrega todo como texto | duración en minutos; 2 duraciones inválidas → NaN con bandera cierre_invalido |
| 3.6 | Duración vacía: se deja vacía en el limpio y mediana por grupo en el modelo, con bandera | son incidencias no normalizadas (vacío no aleatorio); la mediana por grupo es la que menos reduce la desviación | 5.320 vacías; cambio de la desviación con mediana por grupo: -11.7 % |
| 4.1 | Derivar es_tx, tipo_enlace, afecta_uptime, duracion_log y variables de tiempo y región | la pregunta pide el tipo de enlace y la pérdida de servicio; ninguna viene como columna | 588 fallas TX clasificadas en 5 tipos de enlace; 2.384 incidencias afectan el uptime |
| 4.1 | Proveedor de los enlaces satelitales = TGS Starlink | el exporte deja vacío el proveedor de los enlaces satelitales; el NOC confirma que es TGS Starlink | 15 fallas satelitales con proveedor completado |
| 4.2 | Codificar criticidad e impacto con orden declarado | el orden alfabético no respeta la gravedad | criticidad 0 (P4) a 5 (P1), P3 y P3E en el mismo nivel; impacto 0 (Sin Impacto) a 3 (Amplio) |
| 4.3 | One-hot de tipo de incidencia, estado, región y tipo de enlace (frecuencia mínima 1 %) | son nominales: no tienen orden | 4 variables → 32 columnas 0/1; tipo_enlace sin agrupar |
| 4.4 | Minutos fuera de servicio cortados al 31-10 a las 23:59 | el uptime es mensual: los minutos de noviembre de una caída que empezó en octubre son del uptime de noviembre (regla del NOC) | 6 incidencias cerraron en noviembre; 19.029 min de noviembre descontados en 6 sitios |
| 4.4 | Tabla de recurrencia por sitio con minutos reales (fusión recursiva de intervalos) | una incidencia puede tumbar varios sitios; sumar duraciones traslapadas cuenta dos veces el mismo tiempo | 559 sitios; 149 con 2 o más fallas; 30 min de traslape descontados |
| 5 | StandardScaler en duracion_log; MinMaxScaler en q_sitios y tiempo_respuesta | duracion_log es casi simétrica; q_sitios tiene IQR 0; tiempo_respuesta toma 5 valores | media de duracion_log_esc = 0.00, desv = 1.00 |
