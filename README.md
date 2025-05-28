# 🤖 TerraBot - Serverless Discord Bot

Serverless Discord Bot desplegado con AWS Lambda, DynamoDB, API Gateway y Terraform.

## 🚀 Tecnologías Utilizadas

- **AWS Lambda** - Función serverless
- **DynamoDB** - Base de datos NoSQL
- **API Gateway** - Endpoint para webhooks
- **Terraform** - Infrastructure as Code
- **GitHub Actions** - CI/CD Pipeline
- **Discord.py** - Interacción con Discord API

## 📋 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/help` | Muestra la lista de comandos |
| `/joke` | Cuenta un chiste de programación |
| `/time` | Muestra la hora actual |
| `/stats` | Estadísticas del bot |
| `/ping` | Verifica conectividad |

## 🛠️ Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/aleadalia/terrabot-discord.git
cd terrabot-discord

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Desplegar con Terraform
cd terraform
terraform init
terraform plan
terraform apply