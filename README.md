# Dashboard Grupo Maipú — BI + IA con Streamlit

## 1) Preparar entorno
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Credenciales y seguridad
- Copia `.streamlit/credentials.toml.example` a `.streamlit/credentials.toml` y edítalo.
- Genera hashes con:
```python
from streamlit_authenticator import Hasher
print(Hasher(["TuClaveFuerte123!"]).generate())
```
- Mantén **privado** `credentials.toml` y `data/`.

## 3) Ejecutar
```bash
streamlit run app.py
```

## 4) Despliegue
- **Infra propia:** Docker + Nginx (TLS) + SSO si es posible.
- **Streamlit Cloud (privado):** repo **privado**, invitar solo correos corporativos, usar *Secrets* para claves.

## 5) Extensiones
- RFM/LTV, cohortes, churn/propensión (IA).
- Logging y backups cifrados.

## 6) Buenas prácticas
- Repo privado y revisión de PRs.
- Sin datos reales en commits.
- Escaneo con Bandit/Flake8 en CI.
