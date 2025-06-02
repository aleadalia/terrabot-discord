import json
import boto3
import os
import requests
from datetime import datetime
import hashlib
import hmac

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

# Discord API
DISCORD_TOKEN = os.environ['BOT_TOKEN']
DISCORD_APP_ID = os.environ.get('DISCORD_APP_ID', '')
DISCORD_PUBLIC_KEY = os.environ.get('DISCORD_PUBLIC_KEY', '')

def lambda_handler(event, context):
    try:
        # Verificar si es una interacción de Discord
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Verificar signature de Discord (opcional pero recomendado)
        if not verify_discord_signature(headers, body):
            print("Invalid Discord signature")
        
        # Parse el webhook payload
        data = json.loads(body)
        
        # Manejar diferentes tipos de interacciones de Discord
        interaction_type = data.get('type')
        
        if interaction_type == 1:  # PING
            return {
                'statusCode': 200,
                'body': json.dumps({'type': 1})  # PONG
            }
        elif interaction_type == 2:  # APPLICATION_COMMAND
            return handle_slash_command(data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'OK'})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def verify_discord_signature(headers, body):
    # Implementar verificación de signature de Discord (opcional)
    return True

def handle_slash_command(data):
    command_data = data.get('data', {})
    command_name = command_data.get('name', '')
    user = data.get('member', {}).get('user', {})
    username = user.get('username', 'Usuario')
    
    response_content = process_command(f"/{command_name}", username)
    
    if response_content:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 4,  # CHANNEL_MESSAGE_WITH_SOURCE
                'data': {
                    'content': response_content
                }
            })
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'type': 4,
            'data': {
                'content': 'Comando no reconocido'
            }
        })
    }

def process_command(command, username):
    cmd = command.lower().split()
    
    if cmd[0] == '/help':
        return """**Comandos disponibles:**
• `/help` - Muestra esta ayuda
• `/joke` - Cuenta un chiste
• `/time` - Muestra la hora actual
• `/stats` - Estadísticas del bot
• `/ping` - Verifica conectividad"""
    
    elif cmd[0] == '/joke':
        jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae bugs! 🐛",
            "¿Cuál es la diferencia entre HTML y HTML5? Unos 4 años de universidad 😅",
            "¿Por qué los desarrolladores odian la naturaleza? Tiene demasiados bugs 🌲🐛",
            "¿Cómo llamas a un algoritmo que no funciona? Un algo-ritmo! 🎵"
        ]
        import random
        return random.choice(jokes)
    
    elif cmd[0] == '/time':
        return f"⏰ Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    elif cmd[0] == '/ping':
        return "🏓 Pong! Bot funcionando correctamente ✅"
    
    elif cmd[0] == '/stats':
        try:
            response = table.get_item(Key={'id': 'stats'})
            stats = response.get('Item', {'commands': 0})
            stats['commands'] = stats.get('commands', 0) + 1
            table.put_item(Item={'id': 'stats', 'commands': stats['commands']})
            return f"📊 Comandos procesados: {stats['commands']}"
        except Exception as e:
            print(f"DynamoDB error: {e}")
            return "📊 Estadísticas no disponibles temporalmente"
    
    return None