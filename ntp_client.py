import socket
import struct
import time

NTP_SERVER = "pool.ntp.org"  # Pode ser alterado para um servidor local
NTP_PORT = 123
NTP_TIMESTAMP_DELTA = 2208988800  # Ajuste entre 1900 e 1970

def ntp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)  # Timeout de 5 segundos

    # Construção do pacote NTP (modo 3 - Cliente)
    request = struct.pack(
        "!B B B b 11I",
        0b00100011,  # Leap Indicator (0), Versão (4), Modo (3 - Cliente)
        0,  # Stratum (não utilizado pelo cliente)
        0,  # Poll Interval
        -6,  # Precision (-6 ≈ 15.6ms)
        0, 0, 0,  # Root Delay, Root Dispersion, Reference ID
        0, 0,  # Reference Timestamp
        0, 0,  # Origem Timestamp
        0, 0,  # Recebimento Timestamp
        0, 0   # Transmissão Timestamp
    )

    orig_timestamp = time.time()  # Tempo de envio do cliente
    client.sendto(request, (NTP_SERVER, NTP_PORT))

    try:
        data, _ = client.recvfrom(48)  # Recebe pacote de 48 bytes
        dest_timestamp = time.time()  # Tempo de chegada da resposta

        # Extrai os timestamps do pacote recebido
        unpacked = struct.unpack("!B B B b 11I", data)
        recv_timestamp = unpacked[10] + unpacked[11] / (2**32)
        trans_timestamp = unpacked[12] + unpacked[13] / (2**32)

        # Corrige os timestamps para o formato Unix
        recv_timestamp -= NTP_TIMESTAMP_DELTA
        trans_timestamp -= NTP_TIMESTAMP_DELTA

        # Calcula offset e delay
        offset = ((recv_timestamp - orig_timestamp) + (trans_timestamp - dest_timestamp)) / 2
        delay = (dest_timestamp - orig_timestamp) - (trans_timestamp - recv_timestamp)

        # Exibe resultados
        print(f"Offset: {offset:.6f} seconds")
        print(f"Round-trip delay: {delay:.6f} seconds")
        print(f"Updated time: {time.ctime(time.time() + offset)}")

    except socket.timeout:
        print("No response from NTP server.")

ntp_client()
