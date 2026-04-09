# De-identification Protocol

The following steps were taken to ensure the anonymity of the dataset:
1. **Removal of Direct Identifiers**: Names, IDs, and contact info (if any) were removed.
2. **K-Anonymity**: Aggregated fields were checked to ensure no individual can be identified by a combination of attributes.
3. **Noise Injection**: Where necessary, slight variations were added to prevent re-identification through triangulation.
4. **Generalization**: Dates and specific locations were generalized.
