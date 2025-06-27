import pygame
import time
import random

# Inicialización de Pygame y configuración de pantalla
pygame.init()
ANCHO, ALTO = 900, 600
AREAJUEGO = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('CACHIMBLOQUES')
FPS = 60
RELOJ = pygame.time.Clock()

# Colores y dimensiones
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
JANCHO, JALTO = 100, 20
BALL_SIZE = 15

# Clase Bloque genérica
class Bloque:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    def draw(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)

# Mostrar texto en pantalla
def mensaje(texto, x, y, size=40):
    fuente = pygame.font.Font('freesansbold.ttf', size)
    surf = fuente.render(texto, True, BLANCO)
    rect = surf.get_rect(center=(x, y))
    AREAJUEGO.blit(surf, rect)

# Mostrar vidas y nivel
def dibujar_vidas(vidas):
    fuente = pygame.font.Font('freesansbold.ttf', 30)
    txt = fuente.render(f'Vidas: {vidas}', True, BLANCO)
    AREAJUEGO.blit(txt, (10, 10))

def dibujar_nivel(nivel):
    fuente = pygame.font.Font('freesansbold.ttf', 30)
    txt = fuente.render(f'Nivel: {nivel}', True, BLANCO)
    AREAJUEGO.blit(txt, (ANCHO - 160, 10))

# Generar bloques para cada nivel
# Nivel 1: dos filas
# Nivel 2: pirámide invertida
# Nivel 3: formas P, O, O
def crear_bloques(nivel):
    bloques = []
    cols, rows = 9, 10
    ancho_b = ANCHO // cols
    alto_b = 30
    if nivel == 1:
        for y in (100, 200):
            for c in range(cols):
                x = c * ancho_b
                bloques.append(Bloque(x, y, ancho_b, alto_b))
    elif nivel == 2:
        num_rows = 5
        for r in range(num_rows):
            count = cols - 2*r
            y = r * alto_b + 100
            x_start = r * ancho_b
            for c in range(count):
                x = x_start + c * ancho_b
                bloques.append(Bloque(x, y, ancho_b, alto_b))
    else:
        shape_w = 3
        for r in range(rows):
            y = r * alto_b + 100
            bloques.append(Bloque(0*ancho_b, y, ancho_b, alto_b))  # P barra vertical
        for i in range(shape_w):
            bloques.append(Bloque(i*ancho_b, 100, ancho_b, alto_b))
            bloques.append(Bloque(i*ancho_b, (rows//2)*alto_b+100, ancho_b, alto_b))
        for offset in (3,6):
            for r in range(rows):
                y = r*alto_b + 100
                bloques.append(Bloque(offset*ancho_b, y, ancho_b, alto_b))
                bloques.append(Bloque((offset+shape_w-1)*ancho_b, y, ancho_b, alto_b))
            for c in range(shape_w):
                x = (offset+c)*ancho_b
                bloques.append(Bloque(x, 100, ancho_b, alto_b))
                bloques.append(Bloque(x, (rows-1)*alto_b+100, ancho_b, alto_b))
    return bloques

# Lógica de juego con colisión pixel a pixel y salida con ESC
def game_loop(nivel, vidas):
    esperando = True
    bloques = crear_bloques(nivel)
    pelota = pygame.Rect((ANCHO-BALL_SIZE)//2, ALTO//2, BALL_SIZE, BALL_SIZE)
    movpx, movpy = 0, 0
    jposx = (ANCHO-JANCHO)//2
    jmovx = 0

    while True:
        AREAJUEGO.fill(NEGRO)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return False, vidas
                if e.key == pygame.K_SPACE and esperando:
                    movpx, movpy = 0, 5 + nivel
                    esperando = False
                if e.key == pygame.K_LEFT:
                    jmovx = -8
                if e.key == pygame.K_RIGHT:
                    jmovx = 8
            if e.type == pygame.KEYUP and e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                jmovx = 0

        # Movimiento paleta
        jposx = max(0, min(jposx+jmovx, ANCHO-JANCHO))
        paleta = pygame.Rect(jposx, ALTO-JALTO-20, JANCHO, JALTO)

        # Colisiones pixel a pixel X
        dx, dy = movpx, movpy
        step_x = 1 if dx>0 else -1 if dx<0 else 0
        for _ in range(abs(dx)):
            pelota.x += step_x
            if pelota.left<=0 or pelota.right>=ANCHO:
                movpx*=-1; pelota.x-=step_x; break
            for bloq in bloques[:]:
                if pelota.colliderect(bloq.rect):
                    bloques.remove(bloq); movpx*=-1; pelota.x-=step_x; break
        # Colisiones pixel a pixel Y
        step_y = 1 if dy>0 else -1 if dy<0 else 0
        for _ in range(abs(dy)):
            pelota.y += step_y
            if pelota.top<=0:
                movpy*=-1; pelota.y-=step_y; break
            if movpy>0 and pelota.colliderect(paleta):
                pelota.bottom=paleta.top-1; movpy*=-1
                offset=(pelota.centerx-paleta.centerx)/(JANCHO/2)
                movpx=int((5+nivel)*offset); break
            for bloq in bloques[:]:
                if pelota.colliderect(bloq.rect):
                    bloques.remove(bloq); movpy*=-1
                    if step_y>0: pelota.bottom=bloq.rect.top-1
                    else: pelota.top=bloq.rect.bottom+1
                    break

        # Dibujar escena
        for bloq in bloques: bloq.draw(AREAJUEGO)
        pygame.draw.rect(AREAJUEGO, (255,0,0), paleta)
        pygame.draw.ellipse(AREAJUEGO, (0,255,0), pelota)
        dibujar_vidas(vidas); dibujar_nivel(nivel)
        pygame.display.update(); RELOJ.tick(FPS)

        # Perder vida
        if pelota.top > ALTO:
            vidas -= 1
            if vidas <= 0:
                # Mensaje de derrota y volver al menú
                AREAJUEGO.fill(NEGRO)
                mensaje('¡A ESTUDIAR, CACHIMBO, PERDISTE!', ANCHO//2, ALTO//2 - 20)
                mensaje('Presione cualquier tecla para volver al menú.', ANCHO//2, ALTO//2 + 20, size=30)
                pygame.display.update()
                wait_for_key(main_menu)
                return False, vidas
            # Reiniciar bola y estado tras perder una vida
            pelota.x, pelota.y = (ANCHO - BALL_SIZE)//2, ALTO//2
            movpx, movpy = 0, 0
            esperando = True
            time.sleep(1)
                # Nivel completado
        if not bloques:
            # Mensaje de felicitación y volver al menú
            AREAJUEGO.fill(NEGRO)
            mensaje('¡FELICIDADES CACHIMBO, GANASTE!', ANCHO//2, ALTO//2 - 20)
            mensaje('Presione cualquier tecla para volver al menú.', ANCHO//2, ALTO//2 + 20, size=30)
            pygame.display.update()
            wait_for_key(main_menu)
            return False, vidas
        if not bloques: return True,vidas

# UI y menús

def wait_for_key(cb):
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); quit()
            if e.type==pygame.KEYDOWN: cb(); return

def show_credits():
    AREAJUEGO.fill(NEGRO)
    mensaje('Gracias por jugar compañeros de la FIEE',ANCHO//2,ALTO//2-40)
    mensaje('Proyecto de POO - Grupo 7',ANCHO//2,ALTO//2)
    mensaje('Presiona cualquier tecla para volver',ANCHO//2,ALTO//2+40,25)
    pygame.display.update(); wait_for_key(main_menu)

def level_menu():
    while True:
        AREAJUEGO.fill(NEGRO)
        mensaje('Selecciona el Nivel',ANCHO//2,100)
        mensaje('1. Nivel 1',ANCHO//2,200,30)
        mensaje('2. Nivel 2',ANCHO//2,250,30)
        mensaje('3. Nivel 3',ANCHO//2,300,30)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); quit()
            if e.type==pygame.KEYDOWN and e.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                success,vidas=game_loop(int(e.unicode),3)
                time.sleep(1); break
        else: continue
        break
    main_menu()

def main_menu():
    while True:
        AREAJUEGO.fill(NEGRO)
        mensaje('CACHIMBLOQUES',ANCHO//2,100)
        mensaje('1. Jugar',ANCHO//2,200,30)
        mensaje('2. Créditos',ANCHO//2,250,30)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); quit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_1: level_menu(); return
                if e.key==pygame.K_2: show_credits(); return

def main(): main_menu()

if __name__=='__main__': main()