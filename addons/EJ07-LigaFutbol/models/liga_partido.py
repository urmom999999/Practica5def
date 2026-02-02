# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LigaPartido(models.Model):
    #Nombre y descripcion del modelo
    _name = 'liga.partido'
    _description = 'Un partido de la liga'


    #Atributos del modelo


    #PARA CUANDO NO HAY UN ATRIBUTO LLAMADO NAME PARA MOSTRAR LOS Many2One en Vistas
    # https://www.odoo.com/es_ES/forum/ayuda-1/how-defined-display-name-in-custom-many2one-91657
    
   

    #Nombre del equipo que juega en casa casa
    equipo_casa = fields.Many2one(
        'liga.equipo',
        string='Equipo local',
    )
    #Goles equipo de casa
    goles_casa= fields.Integer()

    #Nombre del equipo que juega fuera
    equipo_fuera = fields.Many2one(
        'liga.equipo',
        string='Equipo visitante',
    )
    #Goles equipo de casa
    goles_fuera= fields.Integer()
    
    def abrir_wizard_crear_partido(self):
        """Abre el wizard para crear un nuevo partido"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Crear Nuevo Partido',
            'res_model': 'liga.partido.wizard',
            'view_mode': 'form',
            'target': 'new',
            'views': [[False, 'form']],
    }
    #Constraints de atributos
    @api.constrains('equipo_casa')
    def _check_mismo_equipo_casa(self):
        for record in self:
            if not record.equipo_casa:
                raise models.ValidationError('Debe seleccionarse un equipo local.')
            if record.equipo_casa == record.equipo_fuera:
                raise models.ValidationError('Los equipos del partido deben ser diferentes.')


     #Constraints de atributos
    @api.constrains('equipo_fuera')
    def _check_mismo_equipo_fuera(self):
        for record in self:
            if not record.equipo_fuera:
                raise models.ValidationError('Debe seleccionarse un equipo visitante.')
            if record.equipo_fuera and record.equipo_casa == record.equipo_fuera:
                raise models.ValidationError('Los equipos del partido deben ser diferentes.')




    
    '''
    Funcion para actualizar la clasificacion de los equipos, re-calculandola entera
    '''
    def gollocal(self):
        for partido in self.search([]):
            partido.goles_casa += 2
        self.actualizoRegistrosEquipo()

    def golvisit(self):
        for partido in self.search([]):
            partido.goles_fuera += 2
        self.actualizoRegistrosEquipo()


    def actualizar_clasificacion(self):
        """
        Función para actualizar la clasificación de todos los equipos
        """
#reinicio
        equipos = self.env['liga.equipo'].search([])
        for equipo in equipos:
            equipo.write({
                'victorias': 0,
                'empates': 0,
                'derrotas': 0,
                'goles_a_favor': 0,
                'goles_en_contra': 0,
                'puntos': 0,
            })
        
        partidos = self.env['liga.partido'].search([])
        for partido in partidos:
            goles_casa = partido.goles_casa or 0
            goles_fuera = partido.goles_fuera or 0
            diferencia = abs(goles_casa - goles_fuera)
            
 #Actualizar equipo local
            if partido.equipo_casa:
                equipo_casa = partido.equipo_casa
                nuevo_puntos_casa = equipo_casa.puntos
                nueva_victorias_casa = equipo_casa.victorias
                nueva_empates_casa = equipo_casa.empates
                nueva_derrotas_casa = equipo_casa.derrotas
                nuevo_goles_favor_casa = equipo_casa.goles_a_favor + goles_casa
                nuevo_goles_contra_casa = equipo_casa.goles_en_contra + goles_fuera
                
                if goles_casa > goles_fuera:
                    nueva_victorias_casa += 1
                    if diferencia >= 4:
                        nuevo_puntos_casa += 4  
                    else:
                        nuevo_puntos_casa += 3 
                elif goles_casa < goles_fuera:
                    nueva_derrotas_casa += 1
                    if diferencia >= 4:
                        nuevo_puntos_casa -= 1 
                else:
                    nueva_empates_casa += 1
                    nuevo_puntos_casa += 1  
                
                equipo_casa.write({
                    'victorias': nueva_victorias_casa,
                    'empates': nueva_empates_casa,
                    'derrotas': nueva_derrotas_casa,
                    'goles_a_favor': nuevo_goles_favor_casa,
                    'goles_en_contra': nuevo_goles_contra_casa,
                    'puntos': nuevo_puntos_casa,
                })
            
#visitante
            if partido.equipo_fuera:
                equipo_fuera = partido.equipo_fuera
                nuevo_puntos_fuera = equipo_fuera.puntos
                nueva_victorias_fuera = equipo_fuera.victorias
                nueva_empates_fuera = equipo_fuera.empates
                nueva_derrotas_fuera = equipo_fuera.derrotas
                nuevo_goles_favor_fuera = equipo_fuera.goles_a_favor + goles_fuera
                nuevo_goles_contra_fuera = equipo_fuera.goles_en_contra + goles_casa
                
                if goles_fuera > goles_casa:
                    nueva_victorias_fuera += 1
                    if diferencia >= 4:
                        nuevo_puntos_fuera += 4 
                    else:
                        nuevo_puntos_fuera += 3 
                elif goles_fuera < goles_casa:
                    nueva_derrotas_fuera += 1
                    if diferencia >= 4:
                        nuevo_puntos_fuera -= 1  
                else:
                    nueva_empates_fuera += 1
                    nuevo_puntos_fuera += 1 
                
                equipo_fuera.write({
                    'victorias': nueva_victorias_fuera,
                    'empates': nueva_empates_fuera,
                    'derrotas': nueva_derrotas_fuera,
                    'goles_a_favor': nuevo_goles_favor_fuera,
                    'goles_en_contra': nuevo_goles_contra_fuera,
                    'puntos': nuevo_puntos_fuera,
                })
        
        return True
    



    def actualizar(self):
            """Método para actualizar manualmente la clasificación"""
            self.actualizar_clasificacion()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Clasificación actualizada',
                    'message': 'La clasificación se ha actualizado correctamente.',
                    'type': 'success',
                    'sticky': False,
            }
        }
    
    @api.model_create_multi
    def create(self, vals_list):
            """Sobreescribir método create"""
            records = super().create(vals_list)
            records.actualizar_clasificacion()
            return records
        
    def write(self, vals):
            """Sobreescribir método write"""
            result = super().write(vals)
            self.actualizar_clasificacion()
            return result
        
    def unlink(self):
            """Sobreescribir método unlink"""
            result = super().unlink()
            self.actualizar_clasificacion()
            return result