
import cv2
import face_recognition
import psycopg2

# Conexão com o contêiner do PostgreSQL
DB_CONFIG = {
    "dbname": "postgres", # Nome padrão da imagem do pgvector
    "user": "postgres",
    "password": "sua_senha",
    "host": "localhost",
    "port": "5432"
}

# Inicia a captura de vídeo. Tente 1 ou 2 se o celular via USB não abrir no 0.
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

print("Aperte 'ESPAÇO' para capturar o rosto. 'ESC' para fechar.")

while True:
    sucesso, frame = cap.read()
    if not sucesso: break
        
    cv2.imshow("Cadastro Biometrico - TCC", frame)
    key = cv2.waitKey(1)
    
    if key == 32: # Tecla Espaço pressionada
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rostos = face_recognition.face_locations(rgb_frame)
        
        # Garante que a câmera está vendo apenas uma pessoa
        if len(rostos) == 1:
            # Extrai a assinatura matemática do rosto
            encoding = face_recognition.face_encodings(rgb_frame, rostos)[0]
            
            # Converte para string no formato esperado pelo pgvector: "[0.12, -0.04...]"
            vetor_str = str(encoding.tolist())
            nome_usuario = input("Digite o nome do morador: ")
            
            # Insere no banco de dados
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO moradores (nome, status_ativo, vetor_facial) VALUES (%s, %s, %s)",
                (nome_usuario, True, vetor_str)
            )
            conn.commit()
            cur.close()
            conn.close()
            print(f"[{nome_usuario}] cadastrado com sucesso!")
        else:
            print("Erro: Fique sozinho na frente da câmera.")
            
    elif key == 27: # Tecla ESC pressionada
        break

cap.release()
cv2.destroyAllWindows()