from odoo import http
from odoo.http import request

class LigaController(http.Controller):
#link correcto  http://localhost:8069/eliminarempates
    @http.route('/eliminarempates', auth='public', type='http')
    def eliminar_empates(self):
            Partido = request.env['liga.partido'].sudo()
            partidos = Partido.search([])
            empates = partidos.filtered(lambda p: p.goles_casa == p.goles_fuera)
            total = len(empates)
            empates.unlink()
            return f"Partidos eliminados: {total}"
