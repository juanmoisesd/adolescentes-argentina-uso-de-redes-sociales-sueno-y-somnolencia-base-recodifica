import pandas as pd
import os

def clean():
    input_file = "data/raw/original.csv"
    output_file = "data/clean/cleaned.csv"

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    df = pd.read_csv(input_file)

    # Example cleaning: ensure positive values
    df = df[df['horas_sueño'] > 0]

    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")

if __name__ == "__main__":
    clean()
