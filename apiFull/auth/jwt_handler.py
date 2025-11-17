import jwt
from datetime import datetime, timedelta
from flask import current_app

class JWTHandler:
    @staticmethod
    def generate_token(user_id, username, role='user'):
        """
        Genera un token JWT para un usuario
        
        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            role: Rol del usuario
        
        Returns:
            str: Token JWT
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_EXPIRATION_HOURS', 24)),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def decode_token(token):
        """
        Decodifica y valida un token JWT
        
        Args:
            token: Token JWT a decodificar
        
        Returns:
            dict: Payload del token o error
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expirado'}
        except jwt.InvalidTokenError:
            return {'error': 'Token inválido'}