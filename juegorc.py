import pygame
import random

pygame.init()

# --- Configuración general ---
ANCHO = 700
ALTO = 500
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("🎣 Juego de Pesca - Escape y Captura")

# Colores básicos
AZUL = (0, 100, 255)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
GRIS = (200, 200, 200)
NARANJA = (255, 165, 0)
PURPLE = (160, 32, 240)

# --- Cargar imágenes ---
anzuelo_img = pygame.image.load("imagenes/anzuelo.png").convert_alpha()
anzuelo_img = pygame.transform.scale(anzuelo_img, (25, 25))

imagenes_peces = {
    "extrachico": pygame.transform.scale(pygame.image.load("imagenes/extrachico.png").convert_alpha(), (150, 105)),
    "chico": pygame.transform.scale(pygame.image.load("imagenes/chico.png").convert_alpha(), (225, 114)),
    "mediano": pygame.transform.scale(pygame.image.load("imagenes/mediano.png").convert_alpha(), (180, 150)),
    "normal": pygame.transform.scale(pygame.image.load("imagenes/normal.png").convert_alpha(), (270, 126)),
    "grande": pygame.transform.scale(pygame.image.load("imagenes/grande.png").convert_alpha(), (240, 120)),
    "extragrande": pygame.transform.scale(pygame.image.load("imagenes/extragrande.png").convert_alpha(), (675, 360))
}

# --- Fondo ---
fondo = pygame.image.load("imagenes/fondo.png").convert()
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# --- Anzuelo ---
anzuelo_x = ANCHO // 2
anzuelo_y = 50
anzuelo_vel = 5
anzuelo_ancho = 10
anzuelo_alto = 10
anzuelo_max_y = ALTO - 30

# --- Tipos de peces ---
TIPOS_PEZ = {
    "extrachico": {"color": VERDE, "resistencia": 2, "vel_barra": 2, "puntos": 1, "prob": 0.22},
    "chico": {"color": AMARILLO, "resistencia": 3, "vel_barra": 3, "puntos": 2, "prob": 0.20},
    "mediano": {"color": NARANJA, "resistencia": 5, "vel_barra": 4, "puntos": 3, "prob": 0.18},
    "normal": {"color": GRIS, "resistencia": 6, "vel_barra": 4, "puntos": 4, "prob": 0.16},
    "grande": {"color": ROJO, "resistencia": 8, "vel_barra": 5, "puntos": 5, "prob": 0.14},
    "extragrande": {"color": PURPLE, "resistencia": 10, "vel_barra": 6, "puntos": 7, "prob": 0.10},
}

# --- Cooldown de captura ---
COOLDOWN_TIEMPO = 2.0  # segundos
cooldown_restante = 0

# --- Peces iniciales ---
num_peces = 6
peces = []
for _ in range(num_peces):
    tipo = random.choices(list(TIPOS_PEZ.keys()), weights=[p["prob"] for p in TIPOS_PEZ.values()])[0]
    img_pez = imagenes_peces[tipo]
    ancho_pez, alto_pez = img_pez.get_size()
    peces.append({
        "x": random.randint(-200, ANCHO - ancho_pez),
        "y": random.randint(120, ALTO - alto_pez - 80),  # ✅ evita que salgan fuera del agua
        "vel": random.uniform(2, 4),
        "tipo": tipo,
        "capturado": False,
        "resistencia": TIPOS_PEZ[tipo]["resistencia"],
        "dir": 1  # ✅ ahora todos van a la derecha ➡️
    })

# --- Barra de captura ---
capturando = False
barra_x = 150
barra_ancho = 300
barra_alto = 30
barra_pos = barra_x
barra_direccion = 1
pe_anzuelo = None
zona_ancho_inicial = 60
zona_ancho = zona_ancho_inicial

hits = 0
zona_pos = random.randint(barra_x, barra_x + barra_ancho - zona_ancho)
puntaje = 0
fuente = pygame.font.SysFont(None, 30)

click_cooldown = 0.15
tiempo_ultimo_click = 0

# --- Mensajes temporales ---
mensaje_captura = None
mensaje_captura_tiempo = 0
mensaje_escape = None
mensaje_escape_tiempo = 0
mensaje_atrapado = None
mensaje_atrapado_tiempo = 0

# --- Reloj ---
reloj = pygame.time.Clock()
jugando = True

# --- Bucle principal ---
while jugando:
    dt = reloj.tick(60) / 1000
    tiempo_ultimo_click -= dt
    if cooldown_restante > 0:
        cooldown_restante -= dt
        if cooldown_restante < 0:
            cooldown_restante = 0

    # Mensajes
    if mensaje_escape_tiempo > 0:
        mensaje_escape_tiempo -= dt
        if mensaje_escape_tiempo <= 0:
            mensaje_escape = None
    if mensaje_captura_tiempo > 0:
        mensaje_captura_tiempo -= dt
        if mensaje_captura_tiempo <= 0:
            mensaje_captura = None
    if mensaje_atrapado_tiempo > 0:
        mensaje_atrapado_tiempo -= dt
        if mensaje_atrapado_tiempo <= 0:
            mensaje_atrapado = None

    pantalla.blit(fondo, (0, 0))

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False

    teclas = pygame.key.get_pressed()

    # Movimiento del anzuelo
    if not capturando and cooldown_restante == 0:
        if teclas[pygame.K_LEFT] and anzuelo_x > 0:
            anzuelo_x -= anzuelo_vel
        if teclas[pygame.K_RIGHT] and anzuelo_x < ANCHO - anzuelo_ancho:
            anzuelo_x += anzuelo_vel
        if teclas[pygame.K_UP] and anzuelo_y > 0:
            anzuelo_y -= anzuelo_vel
        if teclas[pygame.K_DOWN] and anzuelo_y < anzuelo_max_y:
            anzuelo_y += anzuelo_vel

    # Dibujar hilo y anzuelo
    pygame.draw.line(pantalla, NEGRO, (anzuelo_x + anzuelo_ancho // 2, 0), (anzuelo_x + anzuelo_ancho // 2, anzuelo_y), 2)
    pantalla.blit(anzuelo_img, (anzuelo_x - 5, anzuelo_y - 5))

    # Dibujar y mover peces
    for pez in peces:
        img_pez = imagenes_peces[pez["tipo"]]
        ancho_pez, alto_pez = img_pez.get_size()

        if not pez["capturado"]:
            pez["x"] += pez["vel"] * pez["dir"]

            # ✅ Si sale del borde derecho, reaparece desde la izquierda
            if pez["x"] > ANCHO + 100:
                pez["x"] = -ancho_pez
                pez["y"] = random.randint(120, ALTO - alto_pez - 80)

            pantalla.blit(img_pez, (pez["x"], pez["y"]))

        # Colisión con anzuelo
        if not capturando and cooldown_restante == 0:
            pez_rect = pygame.Rect(pez["x"], pez["y"], ancho_pez, alto_pez)
            anzuelo_rect = pygame.Rect(anzuelo_x, anzuelo_y, anzuelo_ancho, anzuelo_alto)
            if pez_rect.colliderect(anzuelo_rect):
                capturando = True
                pez["capturado"] = True
                barra_pos = barra_x
                barra_direccion = 1
                zona_ancho = zona_ancho_inicial
                zona_pos = random.randint(barra_x, barra_x + barra_ancho - zona_ancho)
                pe_anzuelo = pez
                pe_anzuelo["resistencia"] = TIPOS_PEZ[pez["tipo"]]["resistencia"]
                hits = 0

    # --- Captura con barra ---
    if capturando and pe_anzuelo:
        vel_barra = TIPOS_PEZ[pe_anzuelo["tipo"]]["vel_barra"]
        barra_pos += barra_direccion * vel_barra
        if barra_pos <= barra_x:
            barra_pos = barra_x
            barra_direccion = 1
        elif barra_pos >= barra_x + barra_ancho - 10:
            barra_pos = barra_x + barra_ancho - 10
            barra_direccion = -1

        mouse_click = pygame.mouse.get_pressed()[0]
        if mouse_click and tiempo_ultimo_click <= 0:
            tiempo_ultimo_click = click_cooldown
            if zona_pos <= barra_pos <= zona_pos + zona_ancho:
                hits += 1
                zona_pos = random.randint(barra_x, barra_x + barra_ancho - zona_ancho)
                zona_ancho = max(20, zona_ancho - 3)
            else:
                hits -= 1
                if hits <= 0:
                    mensaje_escape = fuente.render("¡Se ha escapado!", True, ROJO)
                    mensaje_escape_tiempo = 1.5
                    capturando = False
                    pe_anzuelo["capturado"] = False
                    ancho_pez, alto_pez = imagenes_peces[pe_anzuelo["tipo"]].get_size()
                    pe_anzuelo["x"] = -ancho_pez
                    pe_anzuelo["y"] = random.randint(120, ALTO - alto_pez - 80)
                    hits = 0

        # Captura exitosa
        if hits >= pe_anzuelo["resistencia"]:
            puntaje += TIPOS_PEZ[pe_anzuelo["tipo"]]["puntos"]
            mensaje_captura = fuente.render("¡Captura exitosa!", True, VERDE)
            mensaje_captura_tiempo = 2
            mensaje_atrapado = fuente.render(f"Atrapaste un pez {pe_anzuelo['tipo']} 🎣", True, AMARILLO)
            mensaje_atrapado_tiempo = 2
            cooldown_restante = COOLDOWN_TIEMPO
            capturando = False
            pe_anzuelo["capturado"] = False
            ancho_pez, alto_pez = imagenes_peces[pe_anzuelo["tipo"]].get_size()
            pe_anzuelo["x"] = -ancho_pez
            pe_anzuelo["y"] = random.randint(120, ALTO - alto_pez - 80)
            hits = 0

        # Dibujar barra
        pygame.draw.rect(pantalla, BLANCO, (barra_x, ALTO // 2 - barra_alto // 2, barra_ancho, barra_alto), 2)
        pygame.draw.rect(pantalla, VERDE, (zona_pos, ALTO // 2 - barra_alto // 2 + 1, zona_ancho, barra_alto - 2))
        pygame.draw.rect(pantalla, AMARILLO, (barra_pos, ALTO // 2 - barra_alto // 2 + 1, 10, barra_alto - 2))
        texto_lucha = fuente.render(f"{pe_anzuelo['tipo'].capitalize()} - Hits: {hits}/{pe_anzuelo['resistencia']}", True, BLANCO)
        pantalla.blit(texto_lucha, (ANCHO // 2 - texto_lucha.get_width() // 2, 20))

    # Puntaje
    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, BLANCO)
    pantalla.blit(texto_puntaje, (10, 10))

    # Mensajes
    if mensaje_escape:
        pantalla.blit(mensaje_escape, (ANCHO // 2 - mensaje_escape.get_width() // 2, ALTO // 2 + 40))
    if mensaje_captura:
        pantalla.blit(mensaje_captura, (ANCHO // 2 - mensaje_captura.get_width() // 2, ALTO // 2 + 80))
    if mensaje_atrapado:
        pantalla.blit(mensaje_atrapado, (ANCHO // 2 - mensaje_atrapado.get_width() // 2, ALTO // 2 + 120))

    # Cooldown
    if cooldown_restante > 0:
        texto_cooldown = fuente.render(f"Esperando {cooldown_restante:.1f}s...", True, GRIS)
        pantalla.blit(texto_cooldown, (ANCHO // 2 - texto_cooldown.get_width() // 2, ALTO - 40))

    pygame.display.flip()
pygame.quit()
