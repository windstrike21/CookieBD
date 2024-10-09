import os
import pandas as pd

# Directorio donde se encuentran los archivos CSV
directory = '/home/user/Escritorio/CookieBD/'

# Obtener la lista de archivos CSV en el directorio
csv_files = [f for f in os.listdir(directory) if f.startswith('ecommerce_urls_') and f.endswith('.csv')]

# Ordenar los archivos por el rango de números en el nombre
csv_files.sort(key=lambda x: int(x.split('_')[2].split('-')[0]))

# Lista para almacenar los dataframes
df_list = []

# Leer cada archivo CSV y agregarlo a la lista de dataframes
for csv_file in csv_files:
    file_path = os.path.join(directory, csv_file)
    df = pd.read_csv(file_path)
    df_list.append(df)

# Concatenar todos los dataframes en uno solo
df_combined = pd.concat(df_list, ignore_index=True)

# Guardar el dataframe combinado en un nuevo archivo CSV
df_combined.to_csv('/home/user/Escritorio/CookieBD/ecommerce_urls_combined.csv', index=False)

print("Archivos combinados exitosamente en ecommerce_urls_combined.csv")