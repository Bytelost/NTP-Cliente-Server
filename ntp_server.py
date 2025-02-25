import socket
import struct
import time

NTP_PORT = 123  # Porta padrão do NTP
NTP_TIMESTAMP_DELTA = 2208988800  # Diferença entre as épocas Unix (1970) e NTP (1900)

def ntp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", NTP_PORT))  # Ouvindo em todas as interfaces
    
    print(f"NTP Server listening on port {NTP_PORT}")

    while True:
        data, addr = server.recvfrom(48)  # Recebe pacote de 48 bytes do cliente
        recv_timestamp = time.time() + NTP_TIMESTAMP_DELTA  # Tempo de recebimento (NTP)
        
        # Extrai o timestamp de origem do cliente
        orig_timestamp = struct.unpack("!12I", data)[10] + struct.unpack("!12I", data)[11] / (2**32)

        # Calcula o timestamp de transmissão (tempo atual do servidor)
        trans_timestamp = time.time() + NTP_TIMESTAMP_DELTA
        
        # Monta resposta NTP (modo 4 - servidor)
        response = struct.pack(
            "!B B B b 11I",
            0b00100100,  # Leap Indicator (0), Versão (4), Modo (4 - Servidor)
            1,  # Stratum (1 - Primário)
            0,  # Poll Interval
            -6,  # Precision (-6 ≈ 15.6ms)
            0,  # Root Delay
            0,  # Root Dispersion
            0x4C4F434C,  # Reference ID (pode ser o IP do servidor)
            int(trans_timestamp), int((trans_timestamp % 1) * (2**32)),  # Reference Timestamp
            int(orig_timestamp), int((orig_timestamp % 1) * (2**32)),  # Origem (cliente)
            int(recv_timestamp), int((recv_timestamp % 1) * (2**32)),  # Recebimento (servidor)
            int(trans_timestamp), int((trans_timestamp % 1) * (2**32))  # Transmissão (servidor)
        )

        server.sendto(response, addr)  # Envia resposta ao cliente
        print(f"Respondendo para {addr}")

ntp_server()
