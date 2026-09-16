from pathlib import Path

import face_recognition
import psycopg2


PASTA_FACES = Path("./fotos/")

EXTENSOES_PERMITIDAS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}


def conectar_banco():
    return psycopg2.connect(
        host="localhost",
        database="TCC",
        user="TCC",
        password="estaacabando"
    )


def gerar_vetor(caminho_foto):
    imagem = face_recognition.load_image_file(caminho_foto)

    rostos = face_recognition.face_encodings(imagem)

    if len(rostos) == 0:
        raise ValueError(
            "Nenhum rosto encontrado na imagem."
        )

    if len(rostos) > 1:
        raise ValueError(
            "Mais de um rosto encontrado na imagem."
        )

    return rostos[0]


def cadastrar_fotos():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    for foto in PASTA_FACES.iterdir():

        if not foto.is_file():
            continue

        if foto.suffix.lower() not in EXTENSOES_PERMITIDAS:
            continue

        nome = foto.stem

        print(f"Processando: {foto.name}")

        try:

            vetor = gerar_vetor(str(foto))

            cursor.execute(
                """
                INSERT INTO usuario
                    (nome, vetor_facial)
                VALUES
                    (%s, %s::vector)
                """,
                (
                    nome,
                    str(vetor.tolist())
                )
            )

            print(
                f"Usuário '{nome}' cadastrado com sucesso."
            )

        except ValueError as erro:

            print(
                f"Erro ao processar '{foto.name}': {erro}"
            )

    conexao.commit()

    cursor.close()
    conexao.close()


if __name__ == "__main__":
    cadastrar_fotos()