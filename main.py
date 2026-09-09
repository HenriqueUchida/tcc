import cv2
import face_recognition
import psycopg2
from ultralytics import YOLO

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "sua_senha",
    "host": "localhost",
    "port": "5432"
}

def reconhecer_morador(vetor_ao_vivo):
    """
    Usa o operador de distância euclidiana (<->) do pgvector 
    para encontrar o rosto mais parecido no banco de dados.
    """
    vetor_str = str(vetor_ao_vivo.tolist())
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Busca a menor distância matemática entre o rosto da câmera e os do banco
    query = """
        SELECT id_morador, nome, vetor_facial <-> %s::vector AS distancia 
        FROM moradores 
        WHERE status_ativo = true 
        ORDER BY distancia ASC 
        LIMIT 1;
    """
    cur.execute(query, (vetor_str,))
    resultado = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Limiar de 0.6 é o padrão recomendado para o modelo do face_recognition
    if resultado and resultado[2] < 0.6:
        return resultado[0], resultado[1]
    return None, None

def registrar_entrada(id_morador, track_id):
    """ Salva a sessão no banco para o cruzamento futuro com a balança """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessoes_tracking (id_morador, track_id) VALUES (%s, %s)",
        (id_morador, track_id)
    )
    conn.commit()
    cur.close()
    conn.close()

# Carrega o modelo YOLOv8 mais leve (nano) para rodar bem sem placa de vídeo dedicada
model = YOLO('yolov8n.pt') 

# Dicionário em memória RAM para não consultar o banco a cada frame
# Formato: { track_id_do_yolo: "Nome do Morador" }
sessoes_ativas = {} 

cap = cv2.VideoCapture(1)
if not cap.isOpened(): cap = cv2.VideoCapture(0)

while cap.isOpened():
    sucesso, frame = cap.read()
    if not sucesso: break

    # Rastreia objetos da classe 0 (pessoas) mantendo os IDs (persist=True)
    resultados = model.track(frame, persist=True, tracker="bytetrack.yaml", classes=[0], verbose=False)
    
    if resultados[0].boxes is not None and resultados[0].boxes.id is not None:
        boxes = resultados[0].boxes.xyxy.cpu().numpy()
        track_ids = resultados[0].boxes.id.cpu().numpy()
        
        for box, track_id in zip(boxes, track_ids):
            track_id = int(track_id)
            x1, y1, x2, y2 = map(int, box)
            
            # Se o YOLO gerou um ID novo que ainda não conhecemos
            if track_id not in sessoes_ativas:
                # Recorta apenas a imagem da pessoa para otimizar o processamento
                roi_pessoa = frame[y1:y2, x1:x2]
                roi_rgb = cv2.cvtColor(roi_pessoa, cv2.COLOR_BGR2RGB)
                rostos = face_recognition.face_locations(roi_rgb)
                
                if rostos:
                    # Encontrou rosto: extrai o vetor e consulta o PostgreSQL
                    vetor_ao_vivo = face_recognition.face_encodings(roi_rgb, rostos)[0]
                    id_morador, nome = reconhecer_morador(vetor_ao_vivo)
                    
                    if nome:
                        sessoes_ativas[track_id] = nome
                        registrar_entrada(id_morador, track_id)
                    else:
                        sessoes_ativas[track_id] = "Desconhecido"
                else:
                    sessoes_ativas[track_id] = "Buscando rosto..."

            # Renderiza as caixas e textos na interface do vídeo
            nome_exibicao = sessoes_ativas.get(track_id, "")
            cor = (0, 255, 0) if nome_exibicao not in ["Desconhecido", "Buscando rosto..."] else (0, 0, 255)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
            cv2.putText(frame, f"ID:{track_id} - {nome_exibicao}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)

    cv2.imshow("Monitoramento - TCC", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()