import os
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from pipeline_utils import setup_logger

logger = setup_logger("phase_3")

def calculate_features(df):
    df['text'] = df['text'].fillna('').astype(str)

    # 1-3. Textual Complexity Features
    df['char_count'] = df['text'].str.len()
    df['word_count'] = df['text'].str.split().str.len()
    df['avg_word_length'] = df['char_count'] / (df['word_count'] + 1)

    # 4-6. Sentence Metrics
    df['sentence_count'] = df['text'].str.count(r'[.!?]') + 1
    df['avg_sentence_length'] = df['word_count'] / (df['sentence_count'])

    # TTR
    def get_ttr(text):
        words = text.lower().split()
        if not words: return 0
        return len(set(words)) / len(words)
    df['lexical_diversity'] = df['text'].apply(get_ttr)

    # 7-9. Sentiment/Emotional
    positive_words = {'affirm', 'grant', 'uphold', 'valid', 'proper', 'right'}
    negative_words = {'deny', 'reverse', 'error', 'wrong', 'invalid', 'fail', 'reject'}
    def get_sentiment(text):
        words = set(text.lower().split())
        pos = len(words.intersection(positive_words))
        neg = len(words.intersection(negative_words))
        if (pos + neg) == 0: return 0
        return (pos - neg) / (pos + neg)
    df['sentiment_score'] = df['text'].apply(get_sentiment)
    df['emotional_density'] = (df['text'].str.count('!') + 1) / (df['word_count'] + 1)

    # 10-12. Citation/Network
    df['is_highly_cited'] = df['citations_count'] > df['citations_count'].median()
    df['citation_density'] = df['citations_count'] / (df['word_count'] + 1)

    # 13-15. Temporal
    df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
    df['is_recent'] = df['year'] > 2000
    df['age_of_case'] = 2025 - df['year']

    # Fixed: use .str.contains()
    df['has_dissent'] = df['text'].str.lower().str.contains('dissent', na=False)

    return df

def main():
    logger.info("--- PHASE 3: FEATURE ENGINEERING STARTED ---")
    proc_dir = Path("processed_data")
    feat_dir = Path("datasets")
    feat_dir.mkdir(exist_ok=True)

    all_dfs = []
    for pfile in proc_dir.glob("*.parquet"):
        logger.info(f"Calculating features for {pfile.name}...")
        df = pd.read_parquet(pfile)
        df_feats = calculate_features(df)
        all_dfs.append(df_feats)

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        out_path = feat_dir / "all_features.csv"
        combined_df.to_csv(out_path, index=False)
        logger.info(f"✅ Generated combined features file: {out_path} ({len(combined_df)} rows)")

    logger.info("--- PHASE 3 COMPLETE ---")

if __name__ == "__main__":
    main()
