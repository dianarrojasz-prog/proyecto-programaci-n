"""
Simulación Molecular del Agua — Cambio de Fase
Solo requiere Python estándar (tkinter ya viene incluido).
Ejecutar: python simulacion_molecular_agua.py
"""

import tkinter as tk
import math
import random

# ── Configuración ──────────────────────────────────────────────────────────
WIDTH      = 760
HEIGHT     = 580
SIM_X      = 20
SIM_Y      = 115
SIM_W      = WIDTH - 40
SIM_H      = 280
COLS, ROWS = 6, 4
FPS_MS     = 16

O_COLOR  = {'solid': '#1D9E75', 'liquid': '#378ADD', 'gas': '#D85A30'}
H_COLOR  = '#85B7EB'
BG_GRAD  = {
    'solid':  ('#EEF8FF', '#D0EAF8'),
    'liquid': ('#E3F4FB', '#A8D8EE'),
    'gas':    ('#FFF5EE', '#FDDCC8'),
}
BADGE_STYLE = {
    'solid':  {'bg': '#E1F5EE', 'fg': '#085041'},
    'liquid': {'bg': '#E6F1FB', 'fg': '#042C53'},
    'gas':    {'bg': '#FAECE7', 'fg': '#4A1B0C'},
}
DESC_BORDER = {'solid': '#0F6E56', 'liquid': '#185FA5', 'gas': '#D85A30'}
DESC_BG     = {'solid': '#F0FFF8', 'liquid': '#F0F7FF', 'gas': '#FFF5EE'}

PHASE_DATA = {
    'solid': {
        'name': 'Hielo (sólido)', 'badge': 'SÓLIDO',
        'mobility': 'Muy baja — vibración',
        'distance': '~2.76 Å', 'energy': 'Mínima',
        'desc': (
            "Hielo: Las moléculas forman una red cristalina hexagonal estable. "
            "Cada H2O establece hasta 4 enlaces de hidrogeno con sus vecinas, "
            "creando una estructura rigida y ordenada. El hielo es menos denso "
            "que el agua liquida porque la red hexagonal deja espacios vacios."
        ),
    },
    'liquid': {
        'name': 'Agua (liquido)', 'badge': 'LIQUIDO',
        'mobility': 'Media — fluye y difunde',
        'distance': '~2.82 Å', 'energy': 'Moderada',
        'desc': (
            "Agua liquida: Los enlaces de hidrogeno se rompen y forman "
            "continuamente. Las moleculas se desplazan libremente manteniendo "
            "cohesion parcial. La estructura es aleatoria y cambiante cada "
            "picosegundo."
        ),
    },
    'gas': {
        'name': 'Vapor (gaseoso)', 'badge': 'GAS',
        'mobility': 'Muy alta — movimiento libre',
        'distance': '> 30 Å (dispersas)', 'energy': 'Alta',
        'desc': (
            "Vapor de agua: Las moleculas tienen energia suficiente para escapar "
            "de los enlaces de hidrogeno. Se mueven de forma libre e independiente, "
            "chocando aleatoriamente. La densidad es ~1600 veces menor que en "
            "estado liquido."
        ),
    },
}


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

def get_phase(temp):
    if temp < 0:   return 'solid'
    if temp < 100: return 'liquid'
    return 'gas'


# ── Molécula ───────────────────────────────────────────────────────────────
class Molecule:
    def __init__(self, bx, by, row, col):
        self.bx = bx; self.by = by
        self.x = float(bx); self.y = float(by)
        self.vx = (random.random() - 0.5) * 0.5
        self.vy = (random.random() - 0.5) * 0.5
        self.angle = random.random() * math.pi * 2
        self.av = (random.random() - 0.5) * 0.02
        self.row = row; self.col = col

    def update(self, phase, temp):
        if phase == 'solid':
            jitter = 0.18 + (temp + 50) / 50 * 0.25
            ang_sp = 0.006 + (temp + 50) / 50 * 0.012
            attr = 0.13; damp = 0.82
        elif phase == 'liquid':
            lf = temp / 100
            jitter = 0.55 + lf * 1.0
            ang_sp = 0.025 + lf * 0.06
            attr = 0.007; damp = 0.93
        else:
            gf = (temp - 100) / 50
            jitter = 1.5 + gf * 3.5
            ang_sp = 0.08 + gf * 0.15
            attr = 0.0; damp = 0.975

        self.vx += (self.bx - self.x) * attr + (random.random() - 0.5) * jitter
        self.vy += (self.by - self.y) * attr + (random.random() - 0.5) * jitter
        self.vx *= damp; self.vy *= damp
        self.x  += self.vx; self.y += self.vy
        self.angle += self.av + (random.random() - 0.5) * ang_sp

        pad = 18
        if self.x < SIM_X + pad:          self.x = SIM_X + pad;          self.vx *= -0.5
        if self.x > SIM_X + SIM_W - pad:  self.x = SIM_X + SIM_W - pad;  self.vx *= -0.5
        if self.y < SIM_Y + pad:          self.y = SIM_Y + pad;          self.vy *= -0.5
        if self.y > SIM_Y + SIM_H - pad:  self.y = SIM_Y + SIM_H - pad;  self.vy *= -0.5


# ── App ────────────────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        root.title("Simulacion Molecular del Agua — Cambio de Fase")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg='#F5F7FA', highlightthickness=0)
        self.canvas.pack()

        self.temp = -30
        self._dragging = False
        self._sl_x1 = 115
        self._sl_x2 = WIDTH - 28
        self._sl_y  = 78
        self._sl_w  = self._sl_x2 - self._sl_x1

        self._init_molecules()
        self._build_static()
        self._build_dynamic()
        self._update_ui()

        self.canvas.bind('<ButtonPress-1>',  self._on_press)
        self.canvas.bind('<B1-Motion>',      self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)

        self._animate()

    # ── Moléculas ──────────────────────────────────────────────────────────
    def _init_molecules(self):
        mx = SIM_W * 0.07; my = SIM_H * 0.12
        sx = (SIM_W - 2 * mx) / (COLS - 1)
        sy = (SIM_H - 2 * my) / (ROWS - 1)
        self._sx = sx; self._sy = sy; self._mx = mx; self._my = my
        self.molecules = []
        for r in range(ROWS):
            for c in range(COLS):
                off = sx * 0.5 if r % 2 == 1 else 0
                bx = SIM_X + mx + c * sx + off
                by = SIM_Y + my + r * sy
                self.molecules.append(Molecule(bx, by, r, c))

    def _update_bases(self, phase):
        sx = self._sx; sy = self._sy; mx = self._mx; my = self._my
        for m in self.molecules:
            off = sx * 0.5 if m.row % 2 == 1 else 0
            m.bx = SIM_X + mx + m.col * sx + off
            m.by = SIM_Y + my + m.row * sy

    # ── UI estática ────────────────────────────────────────────────────────
    def _build_static(self):
        c = self.canvas
        # Tarjeta
        c.create_rectangle(10, 10, WIDTH-10, HEIGHT-10,
                            fill='white', outline='#E5E7EB')
        # Título
        c.create_text(28, 28,
                      text="Simulacion Molecular del Agua — Cambio de Fase",
                      font=('Arial', 13, 'bold'), fill='#1A1A2E', anchor='w')
        # Label slider
        c.create_text(28, 63, text="Temperatura",
                      font=('Arial', 10), fill='#6B7280', anchor='w')
        # Fondo barra
        c.create_rectangle(self._sl_x1, self._sl_y-3,
                            self._sl_x2, self._sl_y+3,
                            fill='#E5E7EB', outline='', tags='slbar')
        # Marcadores
        marks = [(-50,'-50°C'),(0,'0°C'),(50,'50°C'),(100,'100°C'),(150,'150°C')]
        for mt, ml in marks:
            mx2 = self._t2x(mt)
            c.create_line(mx2, self._sl_y+4, mx2, self._sl_y+8, fill='#D1D5DB')
            c.create_text(mx2, self._sl_y+11, text=ml,
                          font=('Arial', 8), fill='#9CA3AF', anchor='n')

        # Leyenda
        leg_y = SIM_Y + SIM_H + 14
        lx = 28
        dots = [('#1D9E75','O solido'),('#378ADD','O liquido'),
                ('#D85A30','O gas'),('#85B7EB','H hidrogeno')]
        for col, lbl in dots:
            c.create_oval(lx, leg_y+1, lx+9, leg_y+10, fill=col, outline='')
            c.create_text(lx+13, leg_y+1, text=lbl, font=('Arial',9),
                          fill='#6B7280', anchor='nw')
            lx += 70
        c.create_line(lx, leg_y+5, lx+20, leg_y+5, fill='#5AA0FF', width=2, dash=(4,3))
        c.create_text(lx+24, leg_y+1, text='Enlace H', font=('Arial',9), fill='#6B7280', anchor='nw')
        lx += 80
        c.create_line(lx, leg_y+5, lx+20, leg_y+5, fill='#A0A0B4', width=2)
        c.create_text(lx+24, leg_y+1, text='Enlace O-H', font=('Arial',9), fill='#6B7280', anchor='nw')

        # Tarjetas info
        card_y = leg_y + 22
        card_h = 48
        card_w = (WIDTH - 60) // 3
        self._card_y = card_y; self._card_h = card_h; self._card_w = card_w
        lbls = ['Movilidad molecular','Distancia promedio','Energia cinetica']
        for i, lbl in enumerate(lbls):
            cx = 28 + i * (card_w + 6)
            c.create_rectangle(cx, card_y, cx+card_w, card_y+card_h,
                                fill='#F9FAFB', outline='#F0F0F0')
            c.create_text(cx+10, card_y+8, text=lbl, font=('Arial',9),
                          fill='#9CA3AF', anchor='nw')

        # Descripción — fondo placeholder
        self._desc_y = card_y + card_h + 8
        self._desc_h = HEIGHT - self._desc_y - 18

    # ── UI dinámica (IDs) ──────────────────────────────────────────────────
    def _build_dynamic(self):
        c = self.canvas
        card_w = self._card_w
        # Slider fill + handle
        self._id_fill   = c.create_rectangle(0,0,0,0, fill='#378ADD', outline='', tags='slfill')
        self._id_handle = c.create_oval(0,0,0,0, fill='#378ADD', outline='white', width=2)
        # Temp / fase / badge
        self._id_temp  = c.create_text(28, SIM_Y-32, text='', font=('Arial',20,'bold'), fill='#1A1A2E', anchor='w')
        self._id_arrow = c.create_text(110, SIM_Y-32, text='→', font=('Arial',14), fill='#6B7280', anchor='w')
        self._id_phase = c.create_text(128, SIM_Y-32, text='', font=('Arial',14,'bold'), fill='#1A1A2E', anchor='w')
        self._id_badge_bg = c.create_rectangle(0,0,0,0, outline='')
        self._id_badge    = c.create_text(0,0, text='', font=('Arial',10,'bold'))
        # Card values
        self._id_cards = []
        for i in range(3):
            cx = 28 + i * (card_w + 6)
            vid = c.create_text(cx+10, self._card_y+26, text='', font=('Arial',10,'bold'), fill='#1A1A2E', anchor='nw')
            self._id_cards.append(vid)
        # Desc
        self._id_desc_bg  = c.create_rectangle(0,0,0,0, outline='')
        self._id_desc_bar = c.create_rectangle(0,0,0,0, outline='')
        self._id_desc_txt = c.create_text(0,0, text='', font=('Arial',10), fill='#374151',
                                          anchor='nw', width=WIDTH-80, justify='left')

    # ── Actualizar UI ──────────────────────────────────────────────────────
    def _update_ui(self):
        t = self.temp
        phase = get_phase(t)
        pd = PHASE_DATA[phase]
        c = self.canvas

        # Slider
        hx = self._t2x(t)
        c.coords(self._id_fill, self._sl_x1, self._sl_y-3, hx, self._sl_y+3)
        c.coords(self._id_handle, hx-8, self._sl_y-8, hx+8, self._sl_y+8)
        fill_col = '#378ADD' if phase == 'liquid' else '#1D9E75' if phase == 'solid' else '#D85A30'
        c.itemconfig(self._id_fill,   fill=fill_col)
        c.itemconfig(self._id_handle, fill=fill_col)

        # Temp + fase
        c.itemconfig(self._id_temp,  text=f"{t}°C")
        c.itemconfig(self._id_phase, text=pd['name'])

        # Badge
        bs = BADGE_STYLE[phase]
        px = c.bbox(self._id_phase)
        bx = (px[2] + 10) if px else 380
        by = SIM_Y - 42
        bw = len(pd['badge']) * 8 + 20; bh = 20
        c.coords(self._id_badge_bg, bx, by, bx+bw, by+bh)
        c.itemconfig(self._id_badge_bg, fill=bs['bg'])
        c.coords(self._id_badge, bx+bw//2, by+bh//2)
        c.itemconfig(self._id_badge, text=pd['badge'], fill=bs['fg'])

        # Tarjetas
        for vid, val in zip(self._id_cards, [pd['mobility'], pd['distance'], pd['energy']]):
            c.itemconfig(vid, text=val)

        # Descripción
        dy = self._desc_y; dh = self._desc_h
        c.coords(self._id_desc_bg, 28, dy, WIDTH-28, dy+dh)
        c.itemconfig(self._id_desc_bg, fill=DESC_BG[phase])
        c.coords(self._id_desc_bar, 28, dy, 32, dy+dh)
        c.itemconfig(self._id_desc_bar, fill=DESC_BORDER[phase])
        c.coords(self._id_desc_txt, 40, dy+8)
        c.itemconfig(self._id_desc_txt, text=pd['desc'])

    # ── Dibujar simulación ─────────────────────────────────────────────────
    def _draw_sim(self):
        t = self.temp
        phase = get_phase(t)
        c = self.canvas
        c.delete('sim')

        # Gradiente de fondo
        g1, g2 = BG_GRAD[phase]
        r1,g1c,b1 = hex_to_rgb(g1)
        r2,g2c,b2 = hex_to_rgb(g2)
        steps = 16
        sh = SIM_H / steps
        for i in range(steps):
            f = i / steps
            col = rgb_to_hex(r1+(r2-r1)*f, g1c+(g2c-g1c)*f, b1+(b2-b1)*f)
            c.create_rectangle(SIM_X, SIM_Y + i*sh,
                                SIM_X+SIM_W, SIM_Y + (i+1)*sh+1,
                                fill=col, outline='', tags='sim')
        c.create_rectangle(SIM_X, SIM_Y, SIM_X+SIM_W, SIM_Y+SIM_H,
                            outline='#E5E7EB', width=1, tags='sim')

        # Enlaces de hidrógeno
        if phase != 'gas':
            threshold = 108 if phase == 'solid' else 88
            alpha_f = 0.55 if phase == 'solid' else max(0.08, 0.45 - (t/100)*0.32)
            hb_r = int(90*alpha_f + r1*(1-alpha_f))
            hb_g = int(160*alpha_f + g1c*(1-alpha_f))
            hb_b = int(255*alpha_f + b1*(1-alpha_f))
            hb_col = rgb_to_hex(hb_r, hb_g, hb_b)
            for i in range(len(self.molecules)):
                for j in range(i+1, len(self.molecules)):
                    mi, mj = self.molecules[i], self.molecules[j]
                    dx = mj.x - mi.x; dy = mj.y - mi.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < threshold:
                        n = max(2, int(dist / 8))
                        for s in range(n):
                            if s % 2 == 0:
                                x1 = mi.x + dx*s/n; y1 = mi.y + dy*s/n
                                x2 = mi.x + dx*(s+1)/n; y2 = mi.y + dy*(s+1)/n
                                c.create_line(x1,y1,x2,y2, fill=hb_col, width=1, tags='sim')

        # Moléculas
        rO, rH = 9, 6
        bond_len = 16
        h_ang = math.pi * 0.35
        oc = O_COLOR[phase]

        for m in self.molecules:
            ang = m.angle
            h1x = m.x + math.cos(ang - h_ang) * bond_len
            h1y = m.y + math.sin(ang - h_ang) * bond_len
            h2x = m.x + math.cos(ang + h_ang) * bond_len
            h2y = m.y + math.sin(ang + h_ang) * bond_len

            c.create_line(m.x, m.y, h1x, h1y, fill='#A0A0B4', width=2, tags='sim')
            c.create_line(m.x, m.y, h2x, h2y, fill='#A0A0B4', width=2, tags='sim')
            c.create_oval(h1x-rH,h1y-rH,h1x+rH,h1y+rH, fill=H_COLOR, outline='#88888833', tags='sim')
            c.create_oval(h2x-rH,h2y-rH,h2x+rH,h2y+rH, fill=H_COLOR, outline='#88888833', tags='sim')
            c.create_oval(m.x-rO,m.y-rO,m.x+rO,m.y+rO, fill=oc, outline='#22222233', tags='sim')
            c.create_oval(m.x-5,m.y-5,m.x-1,m.y-1, fill='white', outline='', tags='sim')

    # ── Slider helpers ─────────────────────────────────────────────────────
    def _t2x(self, t):
        return int(self._sl_x1 + (t + 50) / 200 * self._sl_w)

    def _x2t(self, x):
        return round(-50 + (x - self._sl_x1) / self._sl_w * 200)

    def _on_press(self, e):
        hx = self._t2x(self.temp)
        if abs(e.x - hx) < 14 and abs(e.y - self._sl_y) < 14:
            self._dragging = True
        elif self._sl_x1 <= e.x <= self._sl_x2 and abs(e.y - self._sl_y) < 12:
            self.temp = max(-50, min(150, self._x2t(e.x)))
            self._update_ui()

    def _on_drag(self, e):
        if self._dragging:
            x = max(self._sl_x1, min(self._sl_x2, e.x))
            self.temp = self._x2t(x)
            self._update_ui()

    def _on_release(self, e):
        self._dragging = False

    # ── Loop ──────────────────────────────────────────────────────────────
    def _animate(self):
        phase = get_phase(self.temp)
        self._update_bases(phase)
        for m in self.molecules:
            m.update(phase, self.temp)
        self._draw_sim()
        self.root.after(FPS_MS, self._animate)


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
