# LabIA - Estudio clínico estructurado (uso académico)

Aplicación modular para analizar exámenes de laboratorio con OCR, normalización y motor de interpretación académica.

> ⚠️ **Aviso ético**: Uso exclusivamente académico. No reemplaza evaluación médica ni genera diagnósticos definitivos.

## Ahora en HTML

La salida principal se genera en **HTML** y además se incluye una interfaz web HTML tipo dashboard clínico.

## Arquitectura

```text
/app
   /ocr
   /lab_parser
   /reference_database
   /interpretation_engine
   /ui
   /export
```

## Ejecución rápida

### 1) Generar reporte HTML desde CLI

```bash
python main.py \
  --input sample_ocr.txt \
  --edad 67 \
  --sexo M \
  --categoria adulto \
  --erc --etapa-erc 4 \
  --output reporte.html
```

### 2) Levantar interfaz web HTML

```bash
python main_web.py --port 8080
```

Abrir: `http://localhost:8080`

## Funcionalidades clave

- Entrada por TXT OCR o PDF.
- Normalización de unidades y validación de coherencia.
- Rangos por edad/categoría, sexo y ERC por etapa.
- Clasificación por estado y severidad.
- Reglas sindromáticas académicas.
- Reporte en HTML con:
  - Tabla interpretativa
  - Patrones detectados
  - Parámetros no reconocidos
  - Alertas
  - Conclusión académica

## Pruebas

```bash
python -m pytest -q
```
