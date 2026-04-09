import pandas as pd
import os

def process():
    input_file = "data/clean/cleaned.csv"
    output_file = "data/analysis_ready/dataset.csv"

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    df = pd.read_csv(input_file)

    # Standardize column names
    mapping = {
        'pais': 'country',
        'año': 'year',
        'horas_pantalla': 'screen_use',
        'horas_sueño': 'sleep_duration',
        'nota_academica': 'academic_performance',
        'calidad_sueño': 'sleep_quality'
    }
    df = df.rename(columns=mapping)

    # Add constant columns required by schema if missing
    df['unit'] = 'hours'
    df['source'] = 'Mendeley Data'
    df['notes'] = 'Processed from raw'
    df['value'] = df['sleep_duration'] # Using sleep as primary metric for 'value'

    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    process()
