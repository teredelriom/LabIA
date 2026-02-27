# LabIA - Estudio clínico estructurado (uso académico)

Aplicación modular para analizar exámenes de laboratorio con flujo OCR, normalización y motor de interpretación académica.

> ⚠️ **Aviso ético**: Uso exclusivamente académico. No reemplaza evaluación médica ni genera diagnósticos definitivos.

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

## Mejoras aplicadas tras revisión

- Soporte de entrada `.txt` **y** `.pdf`.
- OCR PDF con estrategia progresiva:
  1) extracción de texto embebido (`pdfplumber`),
  2) fallback OCR por imagen (`pytesseract + pdf2image`) si está disponible.
- Manejo de parámetros no reconocidos para mapeo manual posterior.
- Manejo robusto de errores de normalización sin abortar todo el análisis.
- `.gitignore` agregado para evitar archivos temporales de Python/reportes.

## Funcionalidades implementadas

- Carga de texto OCR (simulando extracción de PDF) y PDF opcional.
- Matching semántico por alias (`Hb`, `HGB` → `Hemoglobina`, etc.).
- Normalización de unidades y validación de coherencia.
- Rangos por categoría (`nino`, `adulto`, `adulto_mayor`), sexo y ERC por etapa.
- Clasificación por estado (`bajo`, `alto`, `críticamente alto/bajo`) y severidad.
- Reglas sindromáticas académicas:
  - Anemia microcítica
  - Leucocitosis + neutrofilia
  - Patrón hepatocelular
  - Compromiso renal (creatinina + eGFR)
- Generación de informe en Markdown.
- Base de referencias extensible mediante `data/references.json`.

## Ejecución

### Entrada TXT

```bash
python main.py \
  --input sample_ocr.txt \
  --edad 67 \
  --sexo M \
  --categoria adulto \
  --erc --etapa-erc 4 \
  --output reporte.md
```

### Entrada PDF (si hay dependencias OCR instaladas)

```bash
python main.py --input laboratorio.pdf --edad 45 --sexo F --categoria adulto --output reporte.md
```

## Pruebas

```bash
python -m pytest -q
```

## Cómo ampliar módulos de exámenes

1. Editar `data/references.json`.
2. Agregar nuevo bloque en `parameters` con:
   - `parameter`
   - `aliases`
   - `standard_unit`
   - `conversion`
   - `by_category`
   - opcional: `by_sex`, `ckd_overrides`
   - `source`, `updated_at`
3. El motor lo reconocerá automáticamente por alias.

## Sugerencias priorizadas (siguiente iteración)

1. Migrar de CLI a API (FastAPI) + dashboard clínico.
2. Agregar persistencia de histórico por paciente (comparación longitudinal).
3. Implementar módulo de calculadoras: eGFR, anion gap, osmolaridad, corrección de sodio.
4. Validación de calidad OCR con score de confianza y revisión asistida.
5. Exportación PDF final con branding académico y anexos de referencias.
