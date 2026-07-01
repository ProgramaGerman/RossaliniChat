import os
import time
import subprocess
import httpx
from dotenv import load_dotenv

load_dotenv()

def test_integration():
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    print(f"Verificando API Key... (Comienza con: {api_key[:12]}...)")
    assert api_key != "", "La API Key de OpenRouter está vacía."

    # Levantamos el servidor de FastAPI en un puerto secundario (e.g. 8009)
    print("Iniciando servidor FastAPI local en el puerto 8009...")
    uvicorn_path = os.path.join(".venv", "Scripts", "uvicorn")
    server_process = subprocess.Popen(
        [uvicorn_path, "app.main:app", "--host", "127.0.0.1", "--port", "8009"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Esperamos a que el servidor responda /health
    url_health = "http://127.0.0.1:8009/health"
    url_analyze = "http://127.0.0.1:8009/api/analyze/text"
    
    client = httpx.Client(timeout=120.0)
    
    server_ok = False
    for i in range(10):
        try:
            resp = client.get(url_health)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                print("Servidor FastAPI iniciado correctamente.")
                server_ok = True
                break
        except Exception:
            pass
        time.sleep(1)

    if not server_ok:
        # Cerrar el proceso si falló el inicio
        server_process.terminate()
        stdout, stderr = server_process.communicate()
        print("STDOUT del servidor:\n", stdout)
        print("STDERR del servidor:\n", stderr)
        raise RuntimeError("No se pudo iniciar el servidor FastAPI local.")

    try:
        # Caso de prueba 1: Verificación de modos
        print("Probando endpoint /api/modes...")
        resp_modes = client.get("http://127.0.0.1:8009/api/modes")
        assert resp_modes.status_code == 200
        modes_list = resp_modes.json()
        print(f"Modos disponibles: {[m['key'] for m in modes_list]}")
        assert len(modes_list) > 0

        # Caso de prueba 2: Consulta de texto real con la API Key de OpenRouter
        # (Esto probará el modelo gratuito nvidia/nemotron-nano-12b-v2-vl:free por defecto)
        test_context = "Ella: 'Oye, al final vas a venir al concierto hoy?'"
        print(f"Enviando consulta de análisis de texto para: '{test_context}'")
        
        payload = {"context": test_context}
        resp_analyze = client.post(url_analyze, json=payload)
        
        print(f"Status Code de /analyze/text: {resp_analyze.status_code}")
        assert resp_analyze.status_code == 200
        
        result_data = resp_analyze.json()
        print("\n--- Respuesta de OpenRouter por Modo ---")
        for mode, response_text in result_data.get("modes", {}).items():
            print(f"Modo [{mode}]: {response_text}")
            # Verificamos si hay errores explícitos de OpenRouter o API
            assert "Error" not in response_text or "401" not in response_text, f"Se detectó un error crítico en el modo {mode}: {response_text}"
            
        print("\n¡Prueba de integración completada con éxito!")

    finally:
        print("Deteniendo servidor FastAPI...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("Servidor detenido.")

if __name__ == "__main__":
    test_integration()
