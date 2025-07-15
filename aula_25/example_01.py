from datetime import datetime
import polars as pl
import os
import gc  # Garbage Collector

ENDERECO_DADOS = r'../../dados/'
ENDERECO_DADOS_BRONZE = r'../../bronze/'

try:
    print('Obtendo os dados ...')
    inicio = datetime.now()

    df_bolsa_familia = None

    # lista dos csvs, que serão processados
    lista_arquivos = []

    lista_dir_arquivos = os.listdir(ENDERECO_DADOS)

    with pl.StringCache():
        print('Iniciando a leitura dos arquivos CSV...')

        # pegando apenas os csvs
        for arquivo in lista_dir_arquivos:
            if arquivo.endswith('.csv'):
                lista_arquivos.append(arquivo)

        # print(lista_arquivos)

        # Leitura dos CSVs
        for arquivo in lista_arquivos:
            print(f'Lendo o arquivo {arquivo}')

            df = pl.read_csv(ENDERECO_DADOS + arquivo, separator=';', encoding='iso-8859-1')

            # Converter coluna UF, NOME MUNICÍPIO em categorical
            df = df.with_columns(
                pl.col('UF').cast(pl.Categorical),
                pl.col('NOME MUNICÍPIO').cast(pl.Categorical)
            )

            if df_bolsa_familia is None:
                df_bolsa_familia = df
            else:
                df_bolsa_familia = pl.concat([df_bolsa_familia, df])

            del df

            # print(df_bolsa_familia.head())

            print(f'Arquivo {arquivo} processado com sucesso')

        print(df_bolsa_familia.head())

        # Converter para float o valor da parcela
        df_bolsa_familia = df_bolsa_familia.with_columns(
            pl.col('VALOR PARCELA').str.replace(',', '.').cast(pl.Float64)
        )
        # Convertendo MÊS COMPETÊNCIA para string
        df_bolsa_familia = df_bolsa_familia.with_columns(
            pl.col('MÊS COMPETÊNCIA').cast(pl.Utf8)
        )
        # Convertendo MÊS REFERÊNCIA para string
        df_bolsa_familia = df_bolsa_familia.with_columns(
            pl.col('MÊS REFERÊNCIA').cast(pl.Utf8)
        )

        print('Dados concatenados com sucesso!')
        print('Iniciando a gravação do arquivo Parquet...')

        df_bolsa_familia.write_parquet(ENDERECO_DADOS_BRONZE + 'bolsa_familia_str_cache.parquet')

        print(df_bolsa_familia.head())
        print(df_bolsa_familia.shape)

        del df_bolsa_familia

        gc.collect()

        print('Gravação do arquivo parquet concluida com sucesso')

        fim = datetime.now()

        print(f'Tempo de execução: {fim - inicio}')

except Exception as e:
    print(f'Erro ao obter os dados: {e}')
