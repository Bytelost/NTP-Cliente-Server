import ntplib
from time import ctime

def get_ntp_time(server="pool.ntp.org"):
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return ctime(response.tx_time)
    except Exception as e:
        print(f"Erro ao obter hora NTP: {e}")
        return None

if __name__ == "__main__":
    ntp_time = get_ntp_time()
    if ntp_time:
        print(f"Hora NTP: {ntp_time}")
