import requests
from requests.exceptions import HTTPError

# Function to write down each row into the CSV file
def add_row_in_csv(file, array):
    for i in range(0, len(array)):
        if ";" in array[i]:
            array[i] = array[i].replace(";", " -")

    # write the header to CSV file
    file.write(";".join(array))
    file.write("\n")

host_url = "https://www.ine.pt"
endpoint = "ine/json_indicador/pindica.jsp"

# Language of the response: PT or EN
response_lang = "PT"

# Indicator code. Each code is specific for one indicator. Ex:
# 0000010: Importações (€) de bens por Local de origem e Tipo de bem, produto por atividade (CPA 2002 ) - Anual - INE, Estatísticas do comércio internacional de bens
# 0000020: Produção das principais culturas agrícolas (t) por Localização geográfica (NUTS - 2013) e Espécie - Anual - INE, Estatísticas da produção vegetal
varcd_cod = "0000020" ## EDIT HERE

############# TEMPORAL DIMENSION #############
# Initial year (inclusive)
initial_year = 2015 ## EDIT HERE
# Final year (inclusive)
final_year = 2015 ## EDIT HERE
# Define year range
years_range = range(initial_year, final_year+1)

############# START CSV DOCUMENT #############

file_name = f"INE_varcd{varcd_cod}_{initial_year}_{final_year}"
# Initialize data as empty (just handy for the headers)
data = {"Indicador": "", "Cultura": "", "Ano": "", "Região": "", "Valor": "", "Valor comentário": ""}

# Start a CSV file in write (w) mode
file = open(f"{file_name}.csv", "w")
# Add the headers as the first line of the CSV file
headers = list(data.keys())
add_row_in_csv(file, headers)

############# FETCH DATA #############

# Iterate over each year (the API doesnt accept a universal call for all years..)
for year in years_range:
    print(f"Fetching data from year: {year}...")

    year_code = f"S7A{year}"
    request_url = f"{host_url}/{endpoint}?op=2&varcd={varcd_cod}&Dim1={year_code}&lang={response_lang}"

    try:
        # Make the API request
        response = requests.get(request_url)
        # If any issues with the request, raise and handle it
        response.raise_for_status()
        
        # Parse JSON content
        content = response.json()[0]
        year_data = content["Dados"][str(year)]

        # For each data point within the year's list get its data
        for data_point in year_data:
            data["Indicador"] = content["IndicadorDsg"]
            data["Cultura"] = data_point["dim_3_t"]
            data["Ano"] = str(year)
            data["Região"] = data_point["geodsg"]

            # Check if data is available or not
            # If 'sinal_conv' present in JSON, then there is a comment on the value
            if "sinal_conv" in data_point:
                data["Valor comentário"] = data_point["sinal_conv_desc"]
                # If 'valor' is on the JSON it might be 'Dado provisório' or 'Dado rectificado'
                if "valor" in data_point:
                    data["Valor"] = data_point["valor"]
                else:
                    data["Valor"] = ""
            else:
                # Else don't show any comment
                data["Valor comentário"] = ""
                data["Valor"] = data_point["valor"]

            # write the data to CSV file
            data_row = list(data.values())
            add_row_in_csv(file, data_row)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

# Close the CSV file
file.close()
