import json
import boto3
import os
import requests
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    """Maneja las solicitudes del webhook de Discord"""
    
    # Log del evento para debugging
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Responder a health checks
    if event.get('httpMethod') == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        }
    
    try:
        # Verificar que el body existe
        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No body provided'})
            }
        
        # Parse el webhook payload
        body = json.loads(event['body'])
        logger.info(f"Parsed body: {json.dumps(body)}")
        
        # Manejar verificación de Discord (cuando configuras el webhook)
        if body.get('type') == 1:  # PING
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'type': 1})  # PONG
            }
        
        # Manejar comandos slash de Discord
        if body.get('type') == 2:  # APPLICATION_COMMAND
            return handle_discord_command(body)
        
        # Manejar mensajes normales (si usas un bot tradicional)
        if 'content' in body:
            return handle_discord_message(body)
        
        # Si no es ningún tipo reconocido
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Event type not handled'})
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_discord_command(data):
    """Maneja comandos slash de Discord"""
    command_name = data.get('data', {}).get('name', '')
    user = data.get('member', {}).get('user', {})
    username = user.get('username', 'Usuario')
    
    logger.info(f"Processing slash command: {command_name} from {username}")
    
    response_content = process_slash_command(command_name, username)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'type': 4,  # CHANNEL_MESSAGE_WITH_SOURCE
            'data': {
                'content': response_content
            }
        })
    }

def handle_discord_message(data):
    """Maneja mensajes normales de Discord"""
    content = data.get('content', '')
    author = data.get('author', {})
    channel_id = data.get('channel_id')
    
    # Ignorar mensajes del bot
    if author.get('bot'):
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Bot message ignored'})
        }
    
    # Procesar comandos con prefijo !
    if content.startswith('!'):
        response = process_command(content, author.get('username', 'Usuario'))
        if response:
            # Aquí podrías enviar la respuesta de vuelta a Discord
            # Para esto necesitarías usar la Discord API con el bot token
            pass
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': 'Message processed'})
    }

def process_slash_command(command, username):
    """Procesa comandos slash de Discord"""
    if command == 'help':
        return """
**Comandos disponibles:**
• `/help` - Muestra esta ayuda
• `/joke` - Cuenta un chiste
• `/time` - Muestra la hora actual
• `/stats` - Estadísticas del bot
• `/ping` - Verifica si el bot responde
        """
    
    elif command == 'joke':
        jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae bugs! 🐛",
            "¿Cuál es la diferencia entre HTML y HTML5? Unos 4 años de universidad 😅",
            "¿Por qué los desarrolladores odian la naturaleza? Tiene demasiados bugs 🌲🐛",
            "¿Por qué los programadores nunca van a la playa? Porque no les gusta el C 🏖️",
            "Un SQL query entra en un bar, se acerca a dos tablas y pregunta: '¿Puedo JOIN con ustedes?' 🍻"
        ]
        import random
        return random.choice(jokes)
    
    elif command == 'time':
        return f"⏰ Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    elif command == 'stats':
        try:
            # Obtener estadísticas de DynamoDB
            response = table.get_item(Key={'id': 'stats'})
            stats = response.get('Item', {'commands': 0})
            stats['commands'] += 1
            stats['last_used'] = datetime.now().isoformat()
            
            # Actualizar estadísticas
            table.put_item(Item={
                'id': 'stats', 
                'commands': stats['commands'],
                'last_used': stats['last_used']
            })
            
            return f"📊 Comandos procesados: {stats['commands']}\n🕐 Último uso: {stats.get('last_used', 'N/A')}"
        except Exception as e:
            logger.error(f"Error accessing DynamoDB: {str(e)}")
            return "📊 Estadísticas no disponibles temporalmente"
    
    elif command == 'ping':
        return f"🏓 ¡Pong! Bot funcionando correctamente.\n👋 Hola {username}!"
    
    return f"❓ Comando '{command}' no reconocido. Usa `/help` para ver comandos disponibles."

def process_command(command, username):
    """Procesa comandos con prefijo ! (método tradicional)"""
    cmd = command.lower().split()
    
    if cmd[0] == '!help':
        return """
**Comandos disponibles:**
• `!help` - Muestra esta ayuda
• `!joke` - Cuenta un chiste
• `!time` - Muestra la hora actual
• `!stats` - Estadísticas del bot
• `!echo [mensaje]` - Repite tu mensaje
        """
    
    elif cmd[0] == '!joke':
        jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae bugs! 🐛",
            "¿Cuál es la diferencia entre HTML y HTML5? Unos 4 años de universidad 😅",
            "¿Por qué los desarrolladores odian la naturaleza? Tiene demasiados bugs 🌲🐛"
        ]
        import random
        return random.choice(jokes)
    
    elif cmd[0] == '!time':
        return f"⏰ Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    elif cmd[0] == '!stats':
        try:
            response = table.get_item(Key={'id': 'stats'})
            stats = response.get('Item', {'commands': 0})
            stats['commands'] += 1
            table.put_item(Item={'id': 'stats', 'commands': stats['commands']})
            return f"📊 Comandos procesados: {stats['commands']}"
        except Exception as e:
            logger.error(f"Error with stats: {str(e)}")
            return "📊 Estadísticas no disponibles"
    
    elif cmd[0] == '!echo' and len(cmd) > 1:
        message = ' '.join(cmd[1:])
        return f"🔊 {username} dice: {message}"
    
    return None