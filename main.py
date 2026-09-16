import cv2
import face_recognition
import psycopg2


# ============================================================
# CONFIGURAÇÕES
# ============================================================

TOLERANCIA = 0.5


# ============================================================
# BANCO DE DADOS
# ============================================================

def conectar_banco():
    return psycopg2.connect(
        host="localhost",
        database="TCC",
        user="TCC",
        password="estaacabando"
    )


def buscar_usuario(vetor_facial):
    """
    Envia o vetor facial para o PostgreSQL e procura
    o usuário ativo com o vetor mais próximo.
    """

    conexao = conectar_banco()
    cursor = conexao.cursor()

    vetor = str(vetor_facial.tolist())

    cursor.execute(
        """
        SELECT
            id_morador,
            nome,
            vetor_facial <-> %s::vector AS distancia
        FROM usuario
        WHERE status_ativo = TRUE
        ORDER BY vetor_facial <-> %s::vector
        LIMIT 1
        """,
        (vetor, vetor)
    )

    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    return resultado


# ============================================================
# RECONHECIMENTO FACIAL
# ============================================================

def reconhecer():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError(
            "Não foi possível abrir a câmera."
        )

    print("Câmera iniciada.")
    print("Pressione 'q' para sair.")

    while True:

        ret, frame = camera.read()

        if not ret:
            print("Erro ao capturar imagem da câmera.")
            break

        # ----------------------------------------------------
        # REDUZ A IMAGEM
        # ----------------------------------------------------
        #
        # O reconhecimento facial fica mais rápido trabalhando
        # com uma imagem menor.
        #
        # Depois multiplicamos as coordenadas por 4 para
        # desenhar o resultado na imagem original.
        # ----------------------------------------------------

        frame_pequeno = cv2.resize(
            frame,
            (0, 0),
            fx=0.25,
            fy=0.25
        )

        # ----------------------------------------------------
        # BGR -> RGB
        # ----------------------------------------------------
        #
        # OpenCV utiliza BGR.
        # face_recognition utiliza RGB.
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame_pequeno,
            cv2.COLOR_BGR2RGB
        )

        # ----------------------------------------------------
        # LOCALIZA OS ROSTOS
        # ----------------------------------------------------

        locais_rostos = face_recognition.face_locations(rgb)

        # ----------------------------------------------------
        # GERA OS VETORES
        # ----------------------------------------------------

        vetores = face_recognition.face_encodings(
            rgb,
            locais_rostos
        )

        # ----------------------------------------------------
        # PROCESSA CADA ROSTO ENCONTRADO
        # ----------------------------------------------------

        for local, vetor in zip(locais_rostos, vetores):

            resultado = buscar_usuario(vetor)

            nome = "Desconhecido"

            # ------------------------------------------------
            # VERIFICA SE ENCONTROU ALGUM USUÁRIO
            # ------------------------------------------------

            if resultado is not None:

                id_morador = resultado[0]
                nome_banco = resultado[1]
                distancia = resultado[2]

                # --------------------------------------------
                # DECIDE SE A DISTÂNCIA É ACEITÁVEL
                # --------------------------------------------

                if distancia <= TOLERANCIA:
                    nome = nome_banco

                    print(
                        f"Reconhecido: {nome} "
                        f"(ID: {id_morador}, "
                        f"distância: {distancia:.4f})"
                    )

            # ------------------------------------------------
            # COORDENADAS DO ROSTO
            # ------------------------------------------------

            top, right, bottom, left = local

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # ------------------------------------------------
            # DESENHA O RETÂNGULO
            # ------------------------------------------------

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0, 255, 0),
                2
            )

            # ------------------------------------------------
            # ESCREVE O NOME
            # ------------------------------------------------

            cv2.putText(
                frame,
                nome,
                (left, bottom + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        # ----------------------------------------------------
        # MOSTRA A CÂMERA
        # ----------------------------------------------------

        cv2.imshow(
            "Reconhecimento facial",
            frame
        )

        # ----------------------------------------------------
        # TECLA Q PARA SAIR
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # --------------------------------------------------------
    # FINALIZA
    # --------------------------------------------------------

    camera.release()
    cv2.destroyAllWindows()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    reconhecer()