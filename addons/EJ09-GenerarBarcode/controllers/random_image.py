# -*- coding: utf-8 -*-
import base64
import io
import random
from PIL import Image
from odoo import http
from odoo.http import request, content_disposition

class RandomImageController(http.Controller):
    
    @http.route('/random_image', type='http', auth='public')
    def generate_random_image(self, width=100, height=100, **kwargs):
        """
        Genera una imagen con píxeles aleatorios
        
        Parámetros:
        - width: ancho de la imagen (por defecto 100)
        - height: alto de la imagen (por defecto 100)
        
        Ejemplos:
        - http://localhost:8069/random_image?width=300&height=200
        - http://localhost:8069/random_image?width=500
        """
        try:
            width = int(width)
            height = int(height)
            if width <= 0 or height <= 0:
                return request.make_response(
                    'Error mas de 0.',
                    headers=[('Content-Type', 'text/plain')]
                )
            img = Image.new('RGB', (width, height), color='white')
            pixels = img.load()

            for i in range(width):
                for j in range(height):
                    red = random.randint(0, 255)
                    green = random.randint(0, 255)
                    blue = random.randint(0, 255)
                    pixels[i, j] = (red, green, blue)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
#PNG
            return request.make_response(
                buffer.getvalue(),
                headers=[
                    ('Content-Type', 'image/png'),
                    ('Content-Disposition', content_disposition('random_image.png'))
                ]
            )
            
        except ValueError:
            return request.make_response(
                'Parámetros inválidos. Use números enteros.',
                headers=[('Content-Type', 'text/plain')]
            )
        except Exception as e:
            return request.make_response(
                f'Error generando imagen: {str(e)}',
                headers=[('Content-Type', 'text/plain')]
            )
    
    @http.route('/random_image_base64', type='http', auth='public')
    def generate_random_image_base64(self, width=100, height=100, **kwargs):
        """
        Genera una imagen con píxeles aleatorios y devuelve en Base64
        
        Parámetros:
        - width: ancho de la imagen (por defecto 100)
        - height: alto de la imagen (por defecto 100)
        
        Ejemplo:
        - http://localhost:8069/random_image_base64?width=300&height=200
        """
        try:
            width = int(width)
            height = int(height)
            
            if width <= 0 or height <= 0:
                return request.make_response(
                    '{"error": "Dimensiones inválidas"}',
                    headers=[('Content-Type', 'application/json')]
                )

            img = Image.new('RGB', (width, height), color='white')
            pixels = img.load()
            
            for i in range(width):
                for j in range(height):
                    red = random.randint(0, 255)
                    green = random.randint(0, 255)
                    blue = random.randint(0, 255)
                    pixels[i, j] = (red, green, blue)
 #64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return request.make_response(
                img_base64,
                headers=[('Content-Type', 'text/plain')]
            )
            
        except Exception as e:
            return request.make_response(
                f'{{"error": "{str(e)}"}}',
                headers=[('Content-Type', 'application/json')]
            )