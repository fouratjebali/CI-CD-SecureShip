#!/usr/bin/env bash
set -euo pipefail

export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="root-dev-token"

echo "=== [1/6] Enabling KV secrets engine ==="
vault secrets enable -path=secret kv-v2 2>/dev/null || echo "Already enabled"

echo "=== [2/6] Storing app secrets ==="
vault kv put secret/secureship/db \
  url="postgresql://admin:SuperSecret123@secureship-db:5432/tasks" \
  username="admin" \
  password="SuperSecret123"

vault kv put secret/secureship/app \
  secret_key="$(openssl rand -hex 32)" \
  jwt_algorithm="HS256" \
  jwt_expire_minutes="30"

vault kv put secret/secureship/aws \
  access_key_id="$(openssl rand -hex 10)" \
  secret_access_key="$(openssl rand -hex 20)" \
  region="eu-west-3"

echo "=== [3/6] Enabling AppRole auth ==="
vault auth enable approle 2>/dev/null || echo "Already enabled"

echo "=== [4/6] Creating read-only policy for the app ==="
vault policy write secureship-app - <<EOF
# Allow app to read its own secrets only
path "secret/data/secureship/*" {
  capabilities = ["read", "list"]
}
# Deny everything else
path "secret/*" {
  capabilities = ["deny"]
}
EOF

echo "=== [5/6] Creating AppRole with short-lived tokens ==="
vault write auth/approle/role/secureship-app \
  token_policies="secureship-app" \
  token_ttl="1h" \
  token_max_ttl="4h" \
  secret_id_ttl="24h" \
  token_num_uses=10

# Export credentials for the app to use
ROLE_ID=$(vault read -field=role_id auth/approle/role/secureship-app/role-id)
SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/secureship-app/secret-id)

echo ""
echo "=== [6/6] Enabling audit logging ==="
vault audit enable file file_path=/vault/logs/vault-audit.log 2>/dev/null || echo "Already enabled"

echo ""
echo "============================================"
echo "Vault configured successfully"
echo "--------------------------------------------"
echo "VAULT_ROLE_ID=${ROLE_ID}"
echo "VAULT_SECRET_ID=${SECRET_ID}"
echo "--------------------------------------------"
echo "Add these to your .env file and GitHub Secrets"
echo "============================================"