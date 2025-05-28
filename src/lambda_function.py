import json
import os
import requests
from datetime import datetime
import boto3
import logging

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicializar DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'terrabot-stats')

def lambda_handler(event, context):
    """
    Función principal de AWS Lambda para manejar webhooks de Discord
    """
    try:
        # Verificar si es un ping de Discord
        if event.get('type') == 1:
            return {
                'statusCode': 200,
                'body': json.dumps({'type': 1})
            }
        
        # Parsear el cuerpo del webhook
        body = json.loads(event.get('body', '{}'))
        
        # Verificar si es un comando
        if body.get('type') == 2:  # APPLICATION_COMMAND
            return handle_slash_command(body)
        
        # Manejar mensajes normales (si tienes Message Content Intent)
        if 'content' in body.get('data', {}):
            return handle_message(body)
            
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'OK'})
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_slash_command(body):
    """Manejar comandos slash de Discord"""
    command_name = body.get('data', {}).get('name')
    
    if command_name == 'help':
        response_text = """
🤖 **TerraBot - Comandos Disponibles**

- `/help` - Muestra esta ayuda
- `/joke` - Cuenta un chiste aleatorio  
- `/time` - Muestra la hora actual
- `/stats` - Estadísticas del bot
- `/ping` - Verifica si el bot responde

🔧 **Powered by AWS Lambda + Terraform**
        """
    
    elif command_name == 'joke':
        jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae a los bugs! 🐛",
            "¿Cómo se llama un algoritmo que canta? Un algo-ritmo! 🎵",
            "¿Qué le dice un bit a otro bit? Nos vemos en el byte! 💾",
            "¿Por qué Terraform es tan bueno organizando? Porque siempre mantiene el estado! 📊"
        ]
        import random
        response_text = random.choice(jokes)
    
    elif command_name == 'time':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        response_text = f"🕐 **Hora actual**: {current_time}"
    
    elif command_name == 'stats':
        stats = get_bot_stats()
        response_text = f"""
📊 **TerraBot Estadísticas**

- Comandos ejecutados: {stats.get('commands_executed', 0)}
- Tiempo activo: {stats.get('uptime', 'N/A')}
- Región AWS: {os.environ.get('AWS_REGION', 'us-east-1')}
- Versión: 1.0.0
        """
    
    elif command_name == 'ping':
        response_text = "🏓 ¡Pong! El bot está funcionando correctamente."
    
    else:
        response_text = "❌ Comando no reconocido. Usa `/help` para ver comandos disponibles."
    
    # Incrementar contador de comandos
    increment_command_counter()
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'type': 4,  # CHANNEL_MESSAGE_WITH_SOURCE
            'data': {
                'content': response_text
            }
        })
    }

def handle_message(body):
    """Manejar mensajes de texto normales"""
    content = body.get('data', {}).get('content', '').lower()
    
    if content.startswith('!'):
        # Comando con prefijo !
        command = content[1:].split()[0]
        
        if command == 'help':
            response = "🤖 Usa comandos slash: `/help`, `/joke`, `/time`, `/stats`, `/ping`"
        else:
            response = f"❌ Comando `!{command}` no reconocido. Usa `/help`"
        
        # En un bot real, aquí enviarías la respuesta de vuelta a Discord
        # Por ahora solo logueamos
        logger.info(f"Comando recibido: {command}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Message processed'})
    }

def get_bot_stats():
    """Obtener estadísticas del bot desde DynamoDB"""
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'stat_name': 'commands_executed'})
        
        return {
            'commands_executed': response.get('Item', {}).get('count', 0),
            'uptime': 'Available since deployment'
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {'commands_executed': 0, 'uptime': 'N/A'}

def increment_command_counter():
    """Incrementar contador de comandos en DynamoDB"""
    try:
        table = dynamodb.Table(table_name)
        table.update_item(
            Key={'stat_name': 'commands_executed'},
            UpdateExpression='ADD #count :inc',
            ExpressionAttributeNames={'#count': 'count'},
            ExpressionAttributeValues={':inc': 1}
        )
    except Exception as e:
        logger.error(f"Error incrementing counter: {str(e)}")