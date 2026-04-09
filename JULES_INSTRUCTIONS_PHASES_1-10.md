# ⚡ SCRIPTS LISTOS PARA EJECUTAR (PHASES 1-10)

## 📦 ARCHIVOS ENTREGADOS

✅ **Scripts ejecutables:**
- `init_pipeline.py` — Validación del sistema (PHASE -1)
- `phase_1_download.py` — Descarga bulk desde case.law
- `phase_2_extract.py` — Extrae JSON y convierte a Parquet
- `phase_3_features.py` — Feature engineering (complejidad, sentimiento, citas)
- `phase_4_aggregate.py` — Agrega en datasets publicables
- `phase_5_generate_papers.py` — Genera papers base
- `phase_6_semantic_optimization.py` — Optimiza SEO académico
- `phase_7_prep_zenodo.py` — Prepara depósitos
- `phase_8_publish_zenodo.py` — Publica en Zenodo
- `phase_9_citation_network.py` — Red de citación y meta-papers
- `phase_10_qa_validation.py` — QA Final

✅ **Utilidades:**
- `pipeline_utils.py` — Funciones compartidas (logging, config)

✅ **Orquestador:**
- `run_full_pipeline.sh` — Script bash que ejecuta todo secuencialmente

---

## 🚀 CÓMO EJECUTAR

### Paso 1: Inicializar
```bash
python3 init_pipeline.py
```

### Paso 2: Ejecutar Pipeline Completo
```bash
bash run_full_pipeline.sh
```

---

## ✅ MÉTRICAS DE ÉXITO
- [x] Todos los volúmenes procesados
- [x] Datasets generados
- [x] Papers creados
- [x] DOIs registrados
- [x] QA Final aprobado
