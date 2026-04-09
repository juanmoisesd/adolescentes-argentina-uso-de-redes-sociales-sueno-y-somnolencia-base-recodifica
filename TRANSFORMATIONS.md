# Data Transformations

The following logic was applied during the ETL (Extract, Transform, Load) process:

1. **Renaming**: Columns were renamed from Spanish/Original to English standardized names.
2. **Filtering**: Records with more than 50% missing data were excluded.
3. **Normalization**: Scores were normalized to a 0-1 range for comparative analysis.
4. **Aggregation**: Daily usage was summed into weekly averages.
