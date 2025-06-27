import pygame
import sys
import time
import random

#CONFIGURACIÓN DE RESOLUCIÓN LÓGICA Y PANTALLA REDIMENSIONABLE

pygame.init()
pygame.mixer.init()                        # inicializa el sistema de audio
pygame.mixer.music.load('musica1.ogg')     # carga tu archivo de música
lose_life_sound = pygame.mixer.Sound('lose_life.ogg')
pygame.mixer.music.play(-1)                # -1 = bucle infinito
crash_sound = pygame.mixer.Sound('crash_sound.ogg')


LOGICAL_W, LOGICAL_H = 900, 600
display = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
game_surf = pygame.Surface((LOGICAL_W, LOGICAL_H))
pygame.display.set_caption('CACHIMBLOQUES')
FPS = 60
clock = pygame.time.Clock()

# Cargamos las imagenes
bg_menu = pygame.image.load('facultad.png').convert()
bg_menu = pygame.transform.smoothscale(bg_menu, (LOGICAL_W, LOGICAL_H))

credit_screen = pygame.image.load('credit_screen.png').convert()
credit_screen = pygame.transform.smoothscale(credit_screen, (LOGICAL_W, LOGICAL_H))

back_arrow = pygame.image.load('back_arrow.png').convert_alpha()
ARROW_SIZE = 50
back_arrow = pygame.transform.smoothscale(back_arrow, (ARROW_SIZE, ARROW_SIZE))
back_arrow_rect = back_arrow.get_rect(topleft=(20, 20))

GEAR_SIZE = 40  
gear_img = pygame.image.load('gear.png').convert_alpha()
gear_img = pygame.transform.smoothscale(gear_img, (GEAR_SIZE, GEAR_SIZE))
gear_rect = gear_img.get_rect(center=(LOGICAL_W // 2, GEAR_SIZE // 2 + 10))

game_win_img = pygame.image.load('win_image.png').convert_alpha()
game_lose_img = pygame.image.load('lose_image.png').convert_alpha()
d_bg = 400
d_end = 200
end_img_width = 400
end_img_height = 200
WIN_IMG = pygame.transform.smoothscale(game_win_img, (end_img_width, end_img_height))
LOSE_IMG = pygame.transform.smoothscale(game_lose_img, (end_img_width, end_img_height))
win_bg_img = pygame.image.load('win_bg.png').convert()
lose_bg_img = pygame.image.load('lose_bg.png').convert()
WIN_BG = pygame.transform.smoothscale(win_bg_img, (LOGICAL_W, LOGICAL_H))
LOSE_BG = pygame.transform.smoothscale(lose_bg_img, (LOGICAL_W, LOGICAL_H))

level_menu_bg_img = pygame.image.load('level_menu_bg.png').convert()
LEVEL_MENU_BG = pygame.transform.smoothscale(level_menu_bg_img, (LOGICAL_W, LOGICAL_H))

level_bg_img = pygame.image.load('level_bg.png').convert()
LEVEL_BG = pygame.transform.smoothscale(level_bg_img, (LOGICAL_W, LOGICAL_H))

# Colores y constantes
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
PAL_WIDTH, PAL_HEIGHT = 100, 20
BALL_SIZE = 15

#  UTILIDADES DE DIBUJO Y ESCALADO
def draw_text(surf, text, x, y, size=40):
    font = pygame.font.Font('freesansbold.ttf', size)
    txt = font.render(text, True, BLANCO)
    rect = txt.get_rect(center=(x, y))
    surf.blit(txt, rect)
    return rect

def render_to_screen():
    w, h = display.get_size()
    scaled = pygame.transform.smoothscale(game_surf, (w, h))
    display.blit(scaled, (0, 0))
    pygame.display.update()

#  CLASE BLOQUE Y GENERACIÓN DE NIVEL
class Bloque:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

def crear_bloques(nivel):
    bloques = []
    cols, rows = 9, 10
    ancho_b = LOGICAL_W // cols
    alto_b = 30
    if nivel == 1:
        for y in (100, 200):
            for c in range(cols):
                bloques.append(Bloque(c*ancho_b, y, ancho_b, alto_b))
    elif nivel == 2:
        num_rows = 5
        for r in range(num_rows):
            count = cols - 2*r
            y = r * alto_b + 100
            x_start = r * ancho_b
            for c in range(count):
                bloques.append(Bloque(x_start + c*ancho_b, y, ancho_b, alto_b))
    else:
        shape_w = 3
        # Columna izquierda
        for r in range(rows):
            y = r * alto_b + 100
            bloques.append(Bloque(0, y, ancho_b, alto_b))
        # Bloques centrales
        for i in range(shape_w):
            bloques.append(Bloque(i*ancho_b, 100, ancho_b, alto_b))
            bloques.append(Bloque(i*ancho_b, (rows//2)*alto_b + 100, ancho_b, alto_b))
        # Columnas y bordes derechos
        for offset in (3, 6):
            for r in range(rows):
                y = r * alto_b + 100
                bloques.append(Bloque(offset*ancho_b, y, ancho_b, alto_b))
                bloques.append(Bloque((offset+shape_w-1)*ancho_b, y, ancho_b, alto_b))
            for c in range(shape_w):
                x = (offset + c) * ancho_b
                bloques.append(Bloque(x, 100, ancho_b, alto_b))
                bloques.append(Bloque(x, (rows-1)*alto_b + 100, ancho_b, alto_b))
    return bloques

#  FUNCIONES DE PANTALLA Y BUCLES PRINCIPALES
def wait_for_key(cb):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); quit()
            if e.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
            if e.type == pygame.KEYDOWN:
                cb()
                return

def show_credits():
    while True:
        #Pintar la pantalla de créditos
        game_surf.blit(credit_screen, (0, 0))

        #Coordenadas lógicas del ratón
        win_w, win_h = display.get_size()
        mx, my      = pygame.mouse.get_pos()
        lx = mx * LOGICAL_W / win_w
        ly = my * LOGICAL_H / win_h

        #Detectar hover sobre la flechita
        hover_arrow = back_arrow_rect.collidepoint(lx, ly)

        #Si está en hover, dibujar un “resplandor” amarillo detrás
        if hover_arrow:
            glow = back_arrow_rect.inflate(20, 20)
            pygame.draw.ellipse(game_surf, (255, 255, 0), glow)

        #Dibujar la flechita encima
        game_surf.blit(back_arrow, back_arrow_rect)

        #Escalar y mostrar en pantalla
        render_to_screen()

        #Manejar eventos: sólo clic en la flechita vuelve al menú
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                break
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hover_arrow:
                    return
                
def get_text_surface_and_rect(text, x, y, size=40):
    font = pygame.font.Font('freesansbold.ttf', size)
    surf = font.render(text, True, BLANCO)
    rect = surf.get_rect(center=(x, y))
    return surf, rect

def level_menu():
    while True:
        #Fondo
        game_surf.blit(LEVEL_MENU_BG, (0, 0))

        #Ratón en coords lógicas
        win_w, win_h = display.get_size()
        mx, my      = pygame.mouse.get_pos()
        lx = mx * LOGICAL_W / win_w
        ly = my * LOGICAL_H / win_h

        opts = []
        for idx, y in enumerate((200, 250, 300), start=1):
            text = f'Nivel {idx}'
            surf, rect = get_text_surface_and_rect(text,LOGICAL_W//2, y, size=30)
            over = rect.collidepoint(lx, ly)
            box_col = (255,50,50) if over else (200,30,30)
            box = pygame.Rect(rect.left-30, rect.centery-10, 20, 20)
            pygame.draw.rect(game_surf, box_col, box)
            game_surf.blit(surf, rect)
            opts.append((idx, rect))

        hover_back = back_arrow_rect.collidepoint(lx, ly)
        if hover_back:
            glow = back_arrow_rect.inflate(20, 20)
            pygame.draw.ellipse(game_surf, (255,255,0), glow)
        game_surf.blit(back_arrow, back_arrow_rect)

        render_to_screen()

        #Manejo de eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); quit()
            if e.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                break

            # Clic en la flecha = volver al menú principal
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # mapeo a lógico
                lx_c = e.pos[0] * LOGICAL_W / win_w
                ly_c = e.pos[1] * LOGICAL_H / win_h
                if back_arrow_rect.collidepoint(lx_c, ly_c):
                    return

                # clic en algún nivel
                for nivel, rect in opts:
                    if rect.collidepoint(lx_c, ly_c):
                            pygame.mixer.music.stop()     # ⬅️ detiene la música antes de entrar al nivel
                            game_loop(nivel, vidas=3)
                            time.sleep(1)
                            return

            # Fallback con teclado
            if e.type == pygame.KEYDOWN and e.unicode in ('1','2','3'):
                pygame.mixer.music.stop()       # ⬅️ detiene la música al pulsar 1/2/3
                game_loop(int(e.unicode), vidas=3)
                time.sleep(1)
                return

                if e.type == pygame.KEYDOWN and e.unicode in ('1','2','3'):
                    pygame.mixer.music.stop()
                    game_loop(int(e.unicode), vidas=3)

                return

def main_menu():
    while True:
        # 0) Si la música está parada, la recargamos y la ponemos en bucle
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load('musica1.ogg')
            pygame.mixer.music.play(-1)



        # 1) Pinta el fondo completo
        game_surf.blit(bg_menu, (0,0))

        # 2) Calcula la posición del ratón
        win_w, win_h = display.get_size()
        mx, my      = pygame.mouse.get_pos()
        lx = mx * LOGICAL_W / win_w
        ly = my * LOGICAL_H / win_h

        # 3) Opción JUGAR
        play_s, play_r = get_text_surface_and_rect('Jugar',750, 410,size=40)
        hover_play     = play_r.collidepoint(lx, ly)
        color_play     = (255, 50, 50) if hover_play else (200, 30, 30)
        box_play       = pygame.Rect(play_r.left-30,play_r.centery-10,20, 20)
        pygame.draw.rect(game_surf, color_play, box_play)
        game_surf.blit(play_s, play_r)

        # 4) Opción CRÉDITOS
        cred_s, cred_r = get_text_surface_and_rect('Créditos',750, 500,size=40)
        hover_cred     = cred_r.collidepoint(lx, ly)
        color_cred     = (255, 50, 50) if hover_cred else (200, 30, 30)
        box_cred       = pygame.Rect(cred_r.left-30,cred_r.centery-10,20, 20)
        pygame.draw.rect(game_surf, color_cred, box_cred)
        game_surf.blit(cred_s, cred_r)

        # 5) Escala y muestra
        render_to_screen()

        # 6) Eventos de ratón y teclado
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); quit()
            if e.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                break

            # Clic izquierdo
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hover_play:
                    level_menu(); break
                if hover_play:
                    level_menu()
                    break
                if hover_cred:
                    show_credits(); break

            # Fallback con teclado
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    level_menu(); break
                if e.key == pygame.K_1:
                    level_menu()
                    break
                if e.key == pygame.K_2:
                    show_credits(); break

def pause_menu():
    # Rectángulos de los botones
    btn_w, btn_h = 200, 50
    cont_rect = pygame.Rect(
        (LOGICAL_W//2 - btn_w//2, LOGICAL_H//2 - 30),
        (btn_w, btn_h)
    )
    exit_rect = pygame.Rect(
        (LOGICAL_W//2 - btn_w//2, LOGICAL_H//2 + 40),
        (btn_w, btn_h)
    )

    background = game_surf.copy()

    while True:
        # --- Manejo de eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                lx = mx * LOGICAL_W // display.get_width()
                ly = my * LOGICAL_H // display.get_height()
                if cont_rect.collidepoint(lx, ly):
                    return None
                elif exit_rect.collidepoint(lx, ly):
                    return 'exit'

        #Dibujado del fondo con transparencia
        # 1) Restauramos el fotograma del juego
        game_surf.blit(background, (0, 0))

        # 2) Creamos un overlay semitransparente
        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        # El último valor (ej. 120) es el alpha: 0 completamente transparente, 255 opaco
        overlay.fill((0, 0, 0, 120))
        game_surf.blit(overlay, (0, 0))

        #Dibujado del menú encima
        # Título PAUSA
        draw_text(game_surf, "PAUSA", LOGICAL_W//2, LOGICAL_H//2 - 80, size=60)

        # Estado de hover
        mx, my = pygame.mouse.get_pos()
        lx = mx * LOGICAL_W // display.get_width()
        ly = my * LOGICAL_H // display.get_height()
        hover_cont = cont_rect.collidepoint(lx, ly)
        hover_exit = exit_rect.collidepoint(lx, ly)

        # Botón "Continuar"
        base_color = (50, 50, 50)
        hover_color = (80, 80, 80)
        pygame.draw.rect(
            game_surf,
            hover_color if hover_cont else base_color,
            cont_rect,
            border_radius=8
        )
        draw_text(game_surf, "Continuar", cont_rect.centerx, cont_rect.centery, size=30)
        if hover_cont:
            glow_rect = cont_rect.inflate(6, 6)
            pygame.draw.rect(game_surf, (255, 255, 0), glow_rect, width=3, border_radius=10)

        # Botón "Salir"
        pygame.draw.rect(
            game_surf,
            hover_color if hover_exit else base_color,
            exit_rect,
            border_radius=8
        )
        draw_text(game_surf, "Salir", exit_rect.centerx, exit_rect.centery, size=30)
        if hover_exit:
            glow_rect = exit_rect.inflate(6, 6)
            pygame.draw.rect(game_surf, (255, 255, 0), glow_rect, width=3, border_radius=10)

        # --- Mostrar en pantalla ---
        render_to_screen()
        clock.tick(FPS)

def show_end_screen(win, score):
    pygame.mixer.music.stop()    # ← detiene la música en la pantalla final
    pygame.mixer.music.stop()  #  carga y reproduce el audio de victoria o derrota
    fichero = 'music_win.ogg' if win else 'music_lose.ogg'
    pygame.mixer.music.load(fichero)
    pygame.mixer.music.play()    # sin bucle, que suene una sola vez

    base_color = (50, 50, 50)
    hover_color = (80, 80, 80)
    btn_w, btn_h = 200, 50
    # Botón más abajo cambiando el offset vertical a +180
    btn_rect = pygame.Rect(
        (LOGICAL_W//2 - btn_w//2, LOGICAL_H//2 + 180),
        (btn_w, btn_h)
    )

    while True:
        # Fondo
        bg = WIN_BG if win else LOSE_BG
        game_surf.blit(bg, (0, 0))

        # Ícono central de victoria o derrota
        img = WIN_IMG if win else LOSE_IMG
        img_rect = img.get_rect(center=(LOGICAL_W//2, LOGICAL_H//2 - 80))
        game_surf.blit(img, img_rect)

        # Título
        title = '¡FELICIDADES CACHIMBO, GANASTE!' if win else '¡A ESTUDIAR, CACHIMBO, PERDISTE!'
        draw_text(game_surf, title, LOGICAL_W//2, LOGICAL_H//2 + 60, size=50)

        # Score
        draw_text(game_surf, f'Score: {score}', LOGICAL_W//2, LOGICAL_H//2 + 110, size=40)

        # Botón 'Salir'
        mx, my = pygame.mouse.get_pos()
        lx = mx * LOGICAL_W / display.get_width()
        ly = my * LOGICAL_H / display.get_height()
        hover = btn_rect.collidepoint(lx, ly)

        pygame.draw.rect(
            game_surf,
            hover_color if hover else base_color,
            btn_rect,
            border_radius=8
        )
        draw_text(game_surf, 'Salir', btn_rect.centerx, btn_rect.centery, size=30)

        if hover:
            glow = btn_rect.inflate(6, 6)
            pygame.draw.rect(game_surf, (255, 255, 0), glow, width=3, border_radius=10)

        # Renderizado y manejo de eventos
        render_to_screen()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and hover:
                return  # vuelve al menú inicial
                pygame.mixer.music.stop()  # corta el audio de win/lose
                return  # vuelve al menú inicial
       
def game_loop(nivel, vidas):
    global display
    pygame.mixer.music.stop()

    # Inicialización del nivel
    pygame.mixer.music.load('musica2.ogg')   # carga la música de los niveles
    pygame.mixer.music.play(-1)

    bloques = crear_bloques(nivel)
    initial_blocks = len(bloques)   # ← Número original de bloques
    initial_vidas  = vidas
    jposx = (LOGICAL_W - PAL_WIDTH) // 2
    movpx = movpy = 0
    esperando = True
    jmov = 0

    while True:
        # 1) Manejo de eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif e.type == pygame.VIDEORESIZE:
                display = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    resultado = pause_menu()
                    if resultado == 'exit':
                        pygame.mixer.music.stop()    # ← detiene musica2
                        return
                elif e.key == pygame.K_SPACE and esperando:
                    movpy = -(5 + nivel)
                    movpx = 0
                    esperando = False
                elif e.key == pygame.K_LEFT:
                    jmov = -8
                elif e.key == pygame.K_RIGHT:
                    jmov = 8

            elif e.type == pygame.KEYUP and e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                jmov = 0

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                lx = mx * LOGICAL_W // display.get_width()
                ly = my * LOGICAL_H // display.get_height()
                if gear_rect.collidepoint(lx, ly):
                    resultado = pause_menu()
                    if resultado == 'exit':
                        pygame.mixer.music.stop()  # ← detiene musica2
                        return

        # 2) Lógica de movimiento de la bola y la paleta
        if esperando:
            pelota = pygame.Rect(
                jposx + PAL_WIDTH//2 - BALL_SIZE//2,
                LOGICAL_H - PAL_HEIGHT - BALL_SIZE - 20,
                BALL_SIZE, BALL_SIZE
            )
        else:
            pelota.x += movpx
            pelota.y += movpy

        # Rebotes contra paredes
        if pelota.left <= 0 or pelota.right >= LOGICAL_W:
            movpx = -movpx
        if pelota.top <= 0:
            movpy = -movpy

        # Movimiento de la paleta
        jposx = max(0, min(jposx + jmov, LOGICAL_W - PAL_WIDTH))
        paleta = pygame.Rect(jposx, LOGICAL_H - PAL_HEIGHT - 20, PAL_WIDTH, PAL_HEIGHT)

        # Rebote en paleta
        if pelota.colliderect(paleta) and movpy > 0:
            movpy = -movpy
            offset = (pelota.centerx - paleta.centerx) / (PAL_WIDTH / 2)
            movpx = offset * (5 + nivel)

        # Colisión con bloques
        for b in bloques[:]:
            if pelota.colliderect(b.rect):
                crash_sound.play()     # ← suena efecto de choque
                bloques.remove(b)
                movpy = -movpy
                break

        # Vida perdida
        if pelota.bottom >= LOGICAL_H:
            vidas -= 1
            lose_life_sound.play()           # ← suena cuando pierdes una vida

            if vidas > 0:
                esperando = True
                movpx = movpy = 0
            else:
                broken_blocks   = initial_blocks - len(bloques)
                lives_not_lost  = 0
                score           = broken_blocks * 100 + lives_not_lost * 500
                show_end_screen(False, score)
                return  # retorna al menú inicial

        # Nivel completado
        if not bloques:
             # --- Victoria: calculamos score y mostramos pantalla final ---
            broken_blocks   = initial_blocks  # todos
            lives_not_lost  = vidas
            score           = broken_blocks * 100 + lives_not_lost * 500
            show_end_screen(True, score)
            return  # retorna al menú inicial

        # 3) Dibujado del frame
        game_surf.blit(LEVEL_BG, (0, 0))

        # -- Efecto “brillo” si el ratón está sobre el engranaje --
        mx, my = pygame.mouse.get_pos()
        lx = mx * LOGICAL_W // display.get_width()
        ly = my * LOGICAL_H // display.get_height()
        if gear_rect.collidepoint(lx, ly):
            glow = gear_rect.inflate(12, 12)
            pygame.draw.ellipse(game_surf, (255, 255, 0), glow, width=4)

        # -- Engranaje fijo arriba al centro --
        game_surf.blit(gear_img, gear_rect)

        # -- Bloques --
        for b in bloques:
            b.draw(game_surf)

        # -- Bola y paleta --
        pygame.draw.ellipse(game_surf, (0, 255, 0), pelota)
        pygame.draw.rect(game_surf, (255, 0, 0), paleta)

        # -- HUD (vidas y nivel) --
        draw_text(game_surf, f'Vidas: {vidas}', 100, 30)
        draw_text(game_surf, f'Nivel: {nivel}', LOGICAL_W - 100, 30)

        # -- Escalar a la ventana real y actualizar --
        render_to_screen()
        clock.tick(FPS)

if __name__ == '__main__':
    main_menu()