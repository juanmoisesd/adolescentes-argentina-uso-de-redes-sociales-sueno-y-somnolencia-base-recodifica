import os
import logging
import pandas as pd
from pathlib import Path
from pipeline_utils import setup_logger

logger = setup_logger("phase_4")

def main():
    logger.info("--- PHASE 4: AGGREGATION STARTED ---")
    feat_path = Path("datasets/all_features.csv")
    agg_dir = Path("datasets/aggregated")
    agg_dir.mkdir(parents=True, exist_ok=True)

    if not feat_path.exists():
        logger.error("all_features.csv not found. Run phase 3 first.")
        return

    df = pd.read_csv(feat_path)

    # 1. Textual Complexity Dataset
    tc_cols = ['id', 'name', 'jurisdiction', 'char_count', 'word_count', 'avg_word_length', 'avg_sentence_length', 'lexical_diversity']
    df_tc = df[tc_cols]
    df_tc.to_csv(agg_dir / "dataset_textual_complexity_v1.csv", index=False)
    logger.info("✅ Created dataset_textual_complexity_v1.csv")

    # 2. Citation Network Dataset
    cn_cols = ['id', 'name', 'jurisdiction', 'citations_count', 'is_highly_cited', 'citation_density']
    df_cn = df[cn_cols]
    df_cn.to_csv(agg_dir / "dataset_citation_network_v1.csv", index=False)
    logger.info("✅ Created dataset_citation_network_v1.csv")

    # 3. Temporal Evolution Dataset
    te_cols = ['id', 'name', 'date', 'year', 'is_recent', 'age_of_case']
    df_te = df[te_cols]
    df_te.to_csv(agg_dir / "dataset_temporal_evolution_v1.csv", index=False)
    logger.info("✅ Created dataset_temporal_evolution_v1.csv")

    # 4. Emotional Analysis Dataset
    ea_cols = ['id', 'name', 'sentiment_score', 'emotional_density', 'has_dissent']
    df_ea = df[ea_cols]
    df_ea.to_csv(agg_dir / "dataset_emotional_analysis_v1.csv", index=False)
    logger.info("✅ Created dataset_emotional_analysis_v1.csv")

    logger.info(f"--- PHASE 4 COMPLETE (4 datasets generated in {agg_dir}) ---")

if __name__ == "__main__":
    main()
