# Política de Seguridad — Dashboard Grupo Maipú

- El repositorio **debe** ser Privado en GitHub.
- Los datos de clientes **no** se suben al repo. Usar `data/` solo con dummies.
- Acceso al dashboard:
  - **A)** Infra propia (VM/VPC/VPN) detrás de proxy con TLS + SSO (Azure AD/Google) o `streamlit-authenticator`.
  - **B)** Streamlit Community Cloud en modo **privado** invitando únicamente correos corporativos.
- Rotar `cookie_key` trimestralmente y usar contraseñas **hash** (bcrypt).
- HTTPS extremo a extremo.
- Registrar accesos en proxy y cumplir normativa local (LOPD/GDPR).
