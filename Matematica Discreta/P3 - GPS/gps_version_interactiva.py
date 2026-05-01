"""
gps_version_interactiva.py

Sistema de navegación GPS con interfaz visual tipo Google Maps.
Muestra rutas sobre el grafo real de calles de Madrid.
"""

import pygame
import sys
import math
from typing import Dict, List, Optional, Tuple
import networkx as nx
import pandas as pd
from callejero import carga_callejero, busca_direccion, AdressNotFoundError
from callejero import carga_grafo, procesa_grafo
from pruebas import dijkstra, camino_minimo

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GPS Madrid - Navegación")

# Colores
COLORS = {
    'background': (248, 249, 250),
    'panel': (255, 255, 255),
    'primary': (26, 115, 232),
    'primary_dark': (21, 101, 192),
    'secondary': (234, 67, 53),
    'success': (52, 168, 83),
    'warning': (249, 171, 0),
    'text': (32, 33, 36),
    'text_light': (95, 99, 104),
    'border': (218, 220, 224),
    'streets': (180, 180, 180),
    'streets_highlight': (200, 200, 200),
    'route': (26, 115, 232),
    'route_walk': (52, 168, 83),
    'start': (15, 157, 88),
    'end': (234, 67, 53),
    'button_hover': (245, 245, 245)
}

# Fuentes
font_small = pygame.font.SysFont('Arial', 12)
font_medium = pygame.font.SysFont('Arial', 14)
font_large = pygame.font.SysFont('Arial', 16)
font_title = pygame.font.SysFont('Arial', 20, bold=True)

class Button:
    """Clase para botones interactivos."""
    
    def __init__(self, x, y, width, height, text, color=COLORS['primary'], text_color=(255, 255, 255), icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.icon = icon
        self.hovered = False
        
    def draw(self, surface):
        if self.hovered:
            pygame.draw.rect(surface, COLORS['button_hover'], self.rect, border_radius=8)
        else:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=8)
        
        pygame.draw.rect(surface, COLORS['border'], self.rect, 1, border_radius=8)
        
        # Dibujar icono si existe
        text_x = self.rect.centerx
        if self.icon:
            icon_text = font_medium.render(self.icon, True, self.text_color)
            icon_rect = icon_text.get_rect(center=(self.rect.centerx, self.rect.centery - 8))
            surface.blit(icon_text, icon_rect)
            text_x = self.rect.centerx
            text_y = self.rect.centery + 12
            
            text_surf = font_small.render(self.text, True, COLORS['text'])
            text_rect = text_surf.get_rect(center=(text_x, text_y))
            surface.blit(text_surf, text_rect)
        else:
            text_surf = font_medium.render(self.text, True, COLORS['text'])
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        
    def is_hovered(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InputBox:
    """Clase para campos de entrada de texto."""
    
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        
    def draw(self, surface):
        color = COLORS['primary'] if self.active else COLORS['border']
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)
        
        if self.text:
            text_surf = font_medium.render(self.text, True, COLORS['text'])
        else:
            text_surf = font_medium.render(self.placeholder, True, COLORS['text_light'])
            
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return False

class MapView:
    """Vista del grafo de calles de Madrid."""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.grafo = None
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
    def set_grafo(self, grafo):
        """Establece el grafo a visualizar."""
        self.grafo = grafo
        
    def latlon_to_pixel(self, lat, lon):
        """Convierte coordenadas GPS a píxeles en el mapa."""
        if not self.grafo:
            return (0, 0)
            
        # Encontrar límites del grafo
        lats = [data.get('y', 0) for _, data in self.grafo.nodes(data=True) if 'y' in data]
        lons = [data.get('x', 0) for _, data in self.grafo.nodes(data=True) if 'x' in data]
        
        if not lats or not lons:
            return (0, 0)
            
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Normalizar coordenadas
        norm_x = (lon - min_lon) / (max_lon - min_lon) if max_lon != min_lon else 0.5
        norm_y = 1 - (lat - min_lat) / (max_lat - min_lat) if max_lat != min_lat else 0.5
        
        # Convertir a píxeles con margen
        margin = 0.1
        x = self.rect.x + int(norm_x * self.rect.width * (1 - 2*margin) + self.rect.width * margin)
        y = self.rect.y + int(norm_y * self.rect.height * (1 - 2*margin) + self.rect.height * margin)
        
        return (x, y)
    
    def draw(self, surface, ruta_data=None):
        # Fondo del mapa
        pygame.draw.rect(surface, (240, 240, 240), self.rect)
        pygame.draw.rect(surface, COLORS['border'], self.rect, 2)
        
        # Dibujar calles (grafo completo)
        if self.grafo:
            self.dibujar_calles(surface)
        
        # Dibujar ruta si existe
        if ruta_data and 'camino' in ruta_data:
            self.dibujar_ruta(surface, ruta_data)
        
        # Dibujar leyenda
        self.dibujar_leyenda(surface)
    
    def dibujar_calles(self, surface):
        """Dibuja todas las calles del grafo."""
        for u, v, data in self.grafo.edges(data=True):
            if 'x' in self.grafo.nodes[u] and 'y' in self.grafo.nodes[u] and 'x' in self.grafo.nodes[v] and 'y' in self.grafo.nodes[v]:
                start_pos = self.latlon_to_pixel(self.grafo.nodes[u]['y'], self.grafo.nodes[u]['x'])
                end_pos = self.latlon_to_pixel(self.grafo.nodes[v]['y'], self.grafo.nodes[v]['x'])
                
                # Dibujar calle
                pygame.draw.line(surface, COLORS['streets'], start_pos, end_pos, 1)
    
    def dibujar_ruta(self, surface, ruta_data):
        """Dibuja la ruta calculada sobre el grafo."""
        camino = ruta_data['camino']
        grafo = ruta_data['grafo']
        
        # Obtener coordenadas de todos los nodos del camino
        puntos_ruta = []
        for nodo in camino:
            if 'y' in grafo.nodes[nodo] and 'x' in grafo.nodes[nodo]:
                lat = grafo.nodes[nodo]['y']
                lon = grafo.nodes[nodo]['x']
                punto_pixel = self.latlon_to_pixel(lat, lon)
                puntos_ruta.append(punto_pixel)
        
        # Dibujar línea de ruta
        if len(puntos_ruta) >= 2:
            route_color = COLORS['route_walk'] if ruta_data.get('modo_transporte') == 'peaton' else COLORS['route']
            
            # Dibujar línea gruesa de la ruta
            for i in range(len(puntos_ruta) - 1):
                pygame.draw.line(surface, route_color, puntos_ruta[i], puntos_ruta[i+1], 6)
            
            # Añadir efecto de brillo
            for i in range(len(puntos_ruta) - 1):
                pygame.draw.line(surface, (255, 255, 255), puntos_ruta[i], puntos_ruta[i+1], 2)
        
        # Dibujar puntos de inicio y fin
        if puntos_ruta:
            # Punto de inicio (verde)
            start_pos = puntos_ruta[0]
            pygame.draw.circle(surface, COLORS['start'], start_pos, 10)
            pygame.draw.circle(surface, (255, 255, 255), start_pos, 4)
            
            # Punto de fin (rojo)
            end_pos = puntos_ruta[-1]
            pygame.draw.circle(surface, COLORS['end'], end_pos, 10)
            pygame.draw.circle(surface, (255, 255, 255), end_pos, 4)
            
            # Etiquetas
            start_label = font_small.render("INICIO", True, COLORS['start'])
            end_label = font_small.render("DESTINO", True, COLORS['end'])
            
            surface.blit(start_label, (start_pos[0] + 12, start_pos[1] - 8))
            surface.blit(end_label, (end_pos[0] + 12, end_pos[1] - 8))
    
    def dibujar_leyenda(self, surface):
        """Dibuja la leyenda del mapa."""
        legend_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, 180, 100)
        pygame.draw.rect(surface, (255, 255, 255, 230), legend_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['border'], legend_rect, 1, border_radius=8)
        
        title = font_small.render("Mapa de Calles - Madrid", True, COLORS['text'])
        surface.blit(title, (legend_rect.x + 10, legend_rect.y + 10))
        
        # Inicio
        pygame.draw.circle(surface, COLORS['start'], (legend_rect.x + 15, legend_rect.y + 35), 6)
        start_text = font_small.render("Punto de inicio", True, COLORS['text'])
        surface.blit(start_text, (legend_rect.x + 30, legend_rect.y + 30))
        
        # Fin
        pygame.draw.circle(surface, COLORS['end'], (legend_rect.x + 15, legend_rect.y + 55), 6)
        end_text = font_small.render("Punto destino", True, COLORS['text'])
        surface.blit(end_text, (legend_rect.x + 30, legend_rect.y + 50))
        
        # Ruta
        pygame.draw.line(surface, COLORS['route'], (legend_rect.x + 10, legend_rect.y + 75), 
                        (legend_rect.x + 40, legend_rect.y + 75), 4)
        route_text = font_small.render("Ruta calculada", True, COLORS['text'])
        surface.blit(route_text, (legend_rect.x + 50, legend_rect.y + 70))

class GPSInteractivo:
    """Sistema de navegación GPS con interfaz visual."""
    
    def __init__(self):
        self.callejero = None
        self.grafo_procesado = None
        self.modo_transporte = "coche"
        self.modo_optimizacion = "distancia"
        self.ruta_actual = None
        self.estado = "inicializando"
        
        # Elementos de UI
        self.input_origen = InputBox(50, 30, 400, 45, "¿Desde dónde?")
        self.input_destino = InputBox(50, 90, 400, 45, "¿Hacia dónde?")
        
        # Botón de búsqueda
        self.btn_buscar = Button(470, 30, 120, 105, "Buscar Ruta", COLORS['primary'], (255, 255, 255), "🔍")
        
        # Botones de modo
        self.btn_coche = Button(610, 30, 100, 45, "Coche", icon="🚗")
        self.btn_peaton = Button(610, 90, 100, 45, "Caminar", icon="🚶")
        
        # Botones de optimización
        self.btn_distancia = Button(730, 30, 120, 45, "Más corta", icon="📏")
        self.btn_tiempo = Button(730, 90, 120, 45, "Más rápida", icon="⏱️")
        self.btn_semaforos = Button(870, 30, 120, 105, "Evitar\nsemáforos", icon="🚦")
        
        # Botón de confirmar ruta
        self.btn_confirmar = Button(1010, 30, 120, 105, "Confirmar\nRuta", COLORS['success'], (255, 255, 255), "✅")
        
        # Mapa
        self.mapa = MapView(50, 160, 1300, 650)
        
        # Panel de resultados
        self.panel_resultados = pygame.Rect(50, 820, 1300, 70)
        
        self.cargar_datos()
        
    def cargar_datos(self):
        """Carga los datos del callejero y grafo."""
        try:
            self.estado = "cargando"
            self.callejero = carga_callejero()
            grafo = carga_grafo()
            self.grafo_procesado = procesa_grafo(grafo)
            self.mapa.set_grafo(self.grafo_procesado)  # Pasar el grafo al mapa
            self.estado = "listo"
        except Exception as e:
            self.estado = "error"
            print(f"Error cargando datos: {e}")
    
    def _obtener_funcion_peso(self):
        """Obtiene la función de peso según el modo de optimización."""
        if self.modo_optimizacion == "distancia":
            return self._peso_distancia
        elif self.modo_optimizacion == "tiempo":
            return self._peso_tiempo
        elif self.modo_optimizacion == "semaforos":
            return self._peso_semaforos
    
    def _peso_distancia(self, grafo, u, v):
        return grafo[u][v].get('length', 100.0)
    
    def _peso_tiempo(self, grafo, u, v):
        distancia = grafo[u][v].get('length', 100.0)
        if self.modo_transporte == "coche":
            velocidad = grafo[u][v].get('max_speed', 50.0)
        else:  # peatón
            velocidad = 5.0
            
        velocidad_ms = velocidad * 1000 / 3600
        return distancia / velocidad_ms if velocidad_ms > 0 else float('inf')
    
    def _peso_semaforos(self, grafo, u, v):
        tiempo_base = self._peso_tiempo(grafo, u, v)
        if self.modo_transporte == "coche":
            probabilidad_detencion = 0.3
            tiempo_detencion = 20
        else:
            probabilidad_detencion = 0.1
            tiempo_detencion = 10
            
        return tiempo_base + (probabilidad_detencion * tiempo_detencion)
    
    def encontrar_nodo_mas_cercano(self, latitud, longitud):
        """Encuentra el nodo más cercano a unas coordenadas."""
        if self.grafo_procesado is None:
            return None
            
        nodo_mas_cercano = None
        distancia_minima = float('inf')
        
        for nodo, datos in self.grafo_procesado.nodes(data=True):
            if 'y' in datos and 'x' in datos:
                distancia = self._calcular_distancia(latitud, longitud, datos['y'], datos['x'])
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    nodo_mas_cercano = nodo
        
        return nodo_mas_cercano
    
    def _calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula distancia entre dos puntos usando fórmula de Haversine."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def calcular_ruta(self, direccion_origen, direccion_destino):
        """Calcula la ruta entre dos direcciones."""
        try:
            # Buscar coordenadas
            lat_origen, lon_origen, dir_origen = busca_direccion(direccion_origen, self.callejero)
            lat_destino, lon_destino, dir_destino = busca_direccion(direccion_destino, self.callejero)
            
            # Encontrar nodos
            nodo_origen = self.encontrar_nodo_mas_cercano(lat_origen, lon_origen)
            nodo_destino = self.encontrar_nodo_mas_cercano(lat_destino, lon_destino)
            
            if not nodo_origen or not nodo_destino:
                return None
            
            # Calcular ruta
            funcion_peso = self._obtener_funcion_peso()
            camino = camino_minimo(self.grafo_procesado, funcion_peso, nodo_origen, nodo_destino)
            
            if not camino:
                return None
            
            # Calcular métricas
            distancia_total = 0
            tiempo_total = 0
            
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                distancia_total += self.grafo_procesado[u][v].get('length', 0)
                tiempo_segmento = self._peso_tiempo(self.grafo_procesado, u, v)
                tiempo_total += tiempo_segmento
            
            return {
                'camino': camino,
                'distancia_total': distancia_total,
                'tiempo_total': tiempo_total,
                'origen': dir_origen,
                'destino': dir_destino,
                'coordenadas_origen': (lat_origen, lon_origen),
                'coordenadas_destino': (lat_destino, lon_destino),
                'grafo': self.grafo_procesado,
                'modo_transporte': self.modo_transporte,
                'modo_optimizacion': self.modo_optimizacion
            }
            
        except AdressNotFoundError:
            return None
        except Exception as e:
            print(f"Error calculando ruta: {e}")
            return None
    
    def dibujar_interfaz(self):
        """Dibuja toda la interfaz gráfica."""
        # Fondo
        screen.fill(COLORS['background'])
        
        # Barra de búsqueda
        pygame.draw.rect(screen, (255, 255, 255), (40, 20, 1320, 130), border_radius=12)
        pygame.draw.rect(screen, COLORS['border'], (40, 20, 1320, 130), 1, border_radius=12)
        
        # Campos de entrada
        self.input_origen.draw(screen)
        self.input_destino.draw(screen)
        
        # Botones
        self.btn_buscar.draw(screen)
        self.btn_coche.draw(screen)
        self.btn_peaton.draw(screen)
        self.btn_distancia.draw(screen)
        self.btn_tiempo.draw(screen)
        self.btn_semaforos.draw(screen)
        self.btn_confirmar.draw(screen)
        
        # Mapa
        self.mapa.draw(screen, self.ruta_actual)
        
        # Panel de resultados
        if self.ruta_actual:
            self.dibujar_panel_resultados()
        
        # Estado del sistema
        self.dibujar_estado()
    
    def dibujar_panel_resultados(self):
        """Dibuja el panel con los resultados de la ruta."""
        pygame.draw.rect(screen, (255, 255, 255), self.panel_resultados, border_radius=8)
        pygame.draw.rect(screen, COLORS['border'], self.panel_resultados, 1, border_radius=8)
        
        distancia_km = self.ruta_actual['distancia_total'] / 1000
        tiempo_min = self.ruta_actual['tiempo_total'] / 60
        
        # Información de la ruta
        modo_icon = "🚗" if self.modo_transporte == "coche" else "🚶"
        optimizacion_icon = "📏" if self.modo_optimizacion == "distancia" else "⏱️" if self.modo_optimizacion == "tiempo" else "🚦"
        
        info_texts = [
            f"{modo_icon} {self.modo_transporte.upper()} • {optimizacion_icon} {self.modo_optimizacion.upper()}",
            f"📏 {distancia_km:.1f} km",
            f"⏱️ {tiempo_min:.0f} min",
            f"📍 {self.ruta_actual['origen'][:30]}... → 🎯 {self.ruta_actual['destino'][:30]}..."
        ]
        
        x_pos = self.panel_resultados.x + 20
        for i, text in enumerate(info_texts):
            color = COLORS['primary'] if i == 0 else COLORS['text']
            text_surf = font_medium.render(text, True, color)
            screen.blit(text_surf, (x_pos, self.panel_resultados.y + 25 + i * 15))
    
    def dibujar_estado(self):
        """Dibuja el estado del sistema."""
        if self.estado == "cargando":
            status_text = "🔄 Cargando datos..."
            color = COLORS['warning']
        elif self.estado == "error":
            status_text = "❌ Error cargando datos"
            color = COLORS['secondary']
        else:
            status_text = "✅ Sistema listo"
            color = COLORS['success']
        
        status_surf = font_small.render(status_text, True, color)
        screen.blit(status_surf, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 25))
    
    def actualizar_modo_transporte(self, modo):
        """Actualiza el modo de transporte."""
        self.modo_transporte = modo
        if self.ruta_actual and self.input_origen.text and self.input_destino.text:
            self.ruta_actual = self.calcular_ruta(self.input_origen.text, self.input_destino.text)
    
    def actualizar_modo_optimizacion(self, modo):
        """Actualiza el modo de optimización."""
        self.modo_optimizacion = modo
        if self.ruta_actual and self.input_origen.text and self.input_destino.text:
            self.ruta_actual = self.calcular_ruta(self.input_origen.text, self.input_destino.text)
    
    def mostrar_instrucciones(self):
        """Muestra las instrucciones detalladas de la ruta."""
        if not self.ruta_actual:
            return
        
        print("\n" + "="*60)
        print("INSTRUCCIONES DETALLADAS DE LA RUTA")
        print("="*60)
        print(f"📍 Desde: {self.ruta_actual['origen']}")
        print(f"🎯 Hasta: {self.ruta_actual['destino']}")
        print(f"📏 Distancia total: {self.ruta_actual['distancia_total']/1000:.1f} km")
        print(f"⏱️ Tiempo estimado: {self.ruta_actual['tiempo_total']/60:.0f} minutos")
        print(f"🚀 Modo: {self.modo_transporte.upper()} - {self.modo_optimizacion.upper()}")
        print("\n💡 La ruta se muestra en el mapa. Siga la línea azul desde el punto verde hasta el rojo.")
        print("="*60)
    
    def ejecutar(self):
        """Bucle principal de la aplicación."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Manejar campos de entrada
                if self.input_origen.handle_event(event):
                    pass
                if self.input_destino.handle_event(event):
                    pass
                
                # Manejar botones
                if self.btn_buscar.is_clicked(mouse_pos, event):
                    if self.input_origen.text and self.input_destino.text:
                        self.ruta_actual = self.calcular_ruta(
                            self.input_origen.text, 
                            self.input_destino.text
                        )
                
                if self.btn_coche.is_clicked(mouse_pos, event):
                    self.actualizar_modo_transporte("coche")
                if self.btn_peaton.is_clicked(mouse_pos, event):
                    self.actualizar_modo_transporte("peaton")
                
                if self.btn_distancia.is_clicked(mouse_pos, event):
                    self.actualizar_modo_optimizacion("distancia")
                if self.btn_tiempo.is_clicked(mouse_pos, event):
                    self.actualizar_modo_optimizacion("tiempo")
                if self.btn_semaforos.is_clicked(mouse_pos, event):
                    self.actualizar_modo_optimizacion("semaforos")
                
                if self.btn_confirmar.is_clicked(mouse_pos, event):
                    if self.ruta_actual:
                        self.mostrar_instrucciones()
            
            # Actualizar hover de botones
            self.btn_buscar.is_hovered(mouse_pos)
            self.btn_coche.is_hovered(mouse_pos)
            self.btn_peaton.is_hovered(mouse_pos)
            self.btn_distancia.is_hovered(mouse_pos)
            self.btn_tiempo.is_hovered(mouse_pos)
            self.btn_semaforos.is_hovered(mouse_pos)
            self.btn_confirmar.is_hovered(mouse_pos)
            
            # Dibujar interfaz
            self.dibujar_interfaz()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = GPSInteractivo()
    app.ejecutar()