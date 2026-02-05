import threading
import time
import os

from scrapers.pci_scraper import rodar as pci
#from scrapers.ifs import rodar as ifsp
# adicione outros scrapers aqui

INTERVALO = 60 * 60 * 12  # 12 horas

def loop_scrapers():
    while True:
        try:
            print("🔄 Atualizando dados...")
            pci()
          
            print("✅ Atualização concluída.")
        except Exception as e:
            print("❌ Erro nos scrapers:", e)

        time.sleep(INTERVALO)

def iniciar_scrapers():
    t = threading.Thread(target=loop_scrapers, daemon=True)
    t.start()