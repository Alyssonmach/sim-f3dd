import subprocess
import signal
import os

def main():

    try:
        # Inicia o Streamlit como um subprocesso
        process = subprocess.Popen(["streamlit", "run", "interface/app.py"])
        print("Pressione Ctrl+C para encerrar o Streamlit.")
        
        # Aguarda o término do subprocesso
        process.wait()
    except KeyboardInterrupt:
        print("\nEncerrando o Streamlit...")
        # Envia um sinal para encerrar o subprocesso
        process.terminate()
        try:
            # Aguarda o encerramento completo do subprocesso
            process.wait(timeout = 5)
        except subprocess.TimeoutExpired:
            print("Forçando o encerramento do processo Streamlit.")
            process.kill()
    finally:
        print("Streamlit foi encerrado com sucesso.")

if __name__ == "__main__":
    main()
