import math
import time
import sys
from PIL import Image, ImageTk


# Nessa parte do código você adiciona os movimentos que queira que o seu robô faça.
# Cada movimento é uma tupla com ("tipo", valor, velocidade). Os tipos são:
# - "giro": valor é o ângulo em graus (positivo = sentido horário), velocidade em graus por segundo
# - "reto": valor é a distância em cm, velocidade em cm por segundo.
movimentos = [
    ("giro", 90, 90),
    ("reto", 20, 50),
]


try:
    CTK_AVAILABLE = True
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
except Exception:
    import tkinter as tk
    from tkinter import ttk
    CTK_AVAILABLE = False

MAX_WIDTH = 1000
MAX_HEIGHT = 700
TAPETE_WIDTH_CM = 200
TAPETE_HEIGHT_CM = 114


# Posição inicial em cm
x_atual, y_atual = 20.5, 20.5
angulo_atual = 0
coordenadas = [{
    'x_cm': x_atual,
    'y_cm': y_atual,
    'color': '#e74c3c',
    'angle': angulo_atual,
    'vel': 0,
    'tipo': 'inicio'
}]

# calcula pontos finais
for tipo, valor, vel in movimentos:
    if tipo == "giro":
        angulo_atual = (angulo_atual + valor) % 360
        coordenadas.append({'x_cm': x_atual, 'y_cm': y_atual, 'color': '#e74c3c',
                            'angle': angulo_atual, 'vel': vel, 'tipo': 'giro'})
    elif tipo == "reto":
        rad = math.radians(angulo_atual)
        x_novo = x_atual + valor * math.sin(rad)
        y_novo = y_atual + valor * math.cos(rad)
        x_atual, y_atual = x_novo, y_novo
        coordenadas.append({'x_cm': x_atual, 'y_cm': y_atual, 'color': '#e74c3c',
                            'angle': angulo_atual, 'vel': vel, 'tipo': 'reto'})

# ---------- Janela e widgets (CTK ou Tk fallback) ----------
if CTK_AVAILABLE:
    root = ctk.CTk()
    Frame = ctk.CTkFrame
    Button = ctk.CTkButton
    Slider = ctk.CTkSlider
    Label = ctk.CTkLabel
    OptionMenu = ctk.CTkOptionMenu
    root.geometry("1200x760")
    root.title("Simulador Estratégias — FLL")
else:
    root = tk.Tk()
    Frame = tk.Frame
    Button = tk.Button
    Slider = tk.Scale
    Label = tk.Label
    OptionMenu = tk.OptionMenu
    root.geometry("1200x760")
    root.title("Simulador Estratégias — FLL (Fallback Tk)")

root.configure(bg="#1f2937" if not CTK_AVAILABLE else None)

# ---------- Carrega imagem do tapete ----------
IMAGE_PATH = "estrategia_sem_caminho.png"
try:
    img_original = Image.open(IMAGE_PATH).convert("RGBA")
except FileNotFoundError:
    print(f"Imagem '{IMAGE_PATH}' não encontrada — coloque a imagem na mesma pasta.")
    sys.exit(1)

# escala inicial (ajustada ao MAX)
scale_default = min(MAX_WIDTH / img_original.width, MAX_HEIGHT / img_original.height, 1.0)
width_px = int(img_original.width * scale_default)
height_px = int(img_original.height * scale_default)
img = img_original.resize((width_px, height_px), Image.LANCZOS)
photo = ImageTk.PhotoImage(img)

# ---------- Layout: painel esquerdo (controls) + canvas à direita ----------
panel_left = Frame(root, width=340, height=height_px, bg="#111827" if not CTK_AVAILABLE else None)
panel_left.pack(side="left", fill="y", padx=18, pady=18)
if not CTK_AVAILABLE:
    panel_left.pack_propagate(False)

# header estilizado
if CTK_AVAILABLE:
    header = Label(panel_left, text=" Painel FLL", font=("Inter", 20, "bold"))
else:
    header = Label(panel_left, text=" Painel FLL", font=("Segoe UI", 18, "bold"), fg="white", bg="#111827")
header.pack(pady=(8, 14))

# informações com estilo "cards"
def make_info_card(parent, title, value_text):
    container = Frame(parent, bg="#0b1220" if not CTK_AVAILABLE else None, padx=10, pady=10)
    container.pack(fill="x", pady=8)
    t = Label(container, text=title, font=("Consolas", 9), anchor="w")
    v = Label(container, text=value_text, font=("Consolas", 12, "bold"), anchor="w")
    if not CTK_AVAILABLE:
        t.configure(fg="#9ca3af", bg="#0b1220")
        v.configure(fg="#e6edf3", bg="#0b1220")
    t.pack(anchor="w")
    v.pack(anchor="w", pady=(4,0))
    return v

label_pos = make_info_card(panel_left, "Posição (cm):", "(0.0, 0.0)")
label_angle = make_info_card(panel_left, "Ângulo (°):", "0.0")
label_mouse = make_info_card(panel_left, "Mouse (px / cm):", "—")

# sliders e controles
ctrl_frame = Frame(panel_left, bg="#111827" if not CTK_AVAILABLE else None)
ctrl_frame.pack(fill="x", pady=(12,6))

if CTK_AVAILABLE:
    speed_label = Label(ctrl_frame, text="Velocidade geral", anchor="w")
    speed_label.pack(fill="x")
    slider_speed = Slider(ctrl_frame, from_=0.2, to=3.0, number_of_steps=28, command=None)
    slider_speed.set(1.0)
    slider_speed.pack(fill="x", pady=(6,10))
    zoom_label = Label(ctrl_frame, text="Zoom (tapete)", anchor="w")
    zoom_label.pack(fill="x")
    slider_zoom = Slider(ctrl_frame, from_=0.4, to=1.8, command=None)
    slider_zoom.set(scale_default)
    slider_zoom.pack(fill="x", pady=(6,10))
else:
    speed_label = Label(ctrl_frame, text="Velocidade geral", fg="white", bg="#111827", anchor="w")
    speed_label.pack(fill="x")
    slider_speed = Slider(ctrl_frame, from_=0.2, to=3.0, orient="horizontal", resolution=0.01)
    slider_speed.set(1.0)
    slider_speed.pack(fill="x", pady=(6,10))
    zoom_label = Label(ctrl_frame, text="Zoom (tapete)", fg="white", bg="#111827", anchor="w")
    zoom_label.pack(fill="x")
    slider_zoom = Slider(ctrl_frame, from_=0.4, to=1.8, orient="horizontal", resolution=0.01)
    slider_zoom.set(scale_default)
    slider_zoom.pack(fill="x", pady=(6,10))

# botões
btn_frame = Frame(panel_left, bg="#111827" if not CTK_AVAILABLE else None)
btn_frame.pack(fill="x", pady=(8,0))

def make_button(text, command, fg=None, bgc=None):
    if CTK_AVAILABLE:
        b = Button(btn_frame, text=text, command=command, width=200, corner_radius=10)
    else:
        b = Button(btn_frame, text=text, command=command, fg="white", bg="#0ea5a3", relief="flat", bd=0)
    b.pack(fill="x", pady=6)
    return b

# ---------- Canvas com crosshair, trajetos e animação ----------
canvas_container = Frame(root)
canvas_container.pack(side="right", expand=True, fill="both", padx=18, pady=18)

if CTK_AVAILABLE:
    canvas = ctk.CTkCanvas(canvas_container, width=width_px, height=height_px, highlightthickness=0)
    canvas.pack(expand=True)
else:
    import tkinter as tk
    canvas = tk.Canvas(canvas_container, width=width_px, height=height_px, bg="#0f1724", highlightthickness=2, highlightbackground="#06b6d4")
    canvas.pack(expand=True)

# imagem base
canvas_img_id = canvas.create_image(0, 0, anchor="nw", image=photo)

# ---------- Utilitários: conversões e lista de pontos ----------
def cm_to_pixel(x_cm, y_cm, w_px, h_px):
    x_pixel = x_cm / TAPETE_WIDTH_CM * w_px
    y_pixel = (TAPETE_HEIGHT_CM - y_cm) / TAPETE_HEIGHT_CM * h_px
    return x_pixel, y_pixel

def pixel_to_cm(x_px, y_px, w_px, h_px):
    x_cm = x_px / w_px * TAPETE_WIDTH_CM
    y_cm = (h_px - y_px) / h_px * TAPETE_HEIGHT_CM
    return x_cm, y_cm

points_list = []
def rebuild_points_list(current_w, current_h):
    points_list.clear()
    for pt in coordenadas:
        x_px, y_px = cm_to_pixel(pt['x_cm'], pt['y_cm'], current_w, current_h)
        points_list.append({'x_px': x_px, 'y_px': y_px, 'x_cm': pt['x_cm'], 'y_cm': pt['y_cm'],
                            'color': pt['color'], 'angle': pt['angle'], 'vel': pt['vel'], 'tipo': pt['tipo']})

rebuild_points_list(width_px, height_px)

# ---------- Desenho das trajetórias (linhas polidas e pontos) ----------
traj_tag = "traj"
def redraw_trajectories(current_w, current_h):
    canvas.delete(traj_tag)
    # recompute points to current size
    rebuild_points_list(current_w, current_h)
    # draw smooth line across points in order
    coords = []
    for p in points_list:
        coords.extend([p['x_px'], p['y_px']])
    if len(coords) >= 4:
        canvas.create_line(*coords, width=4, smooth=True, splinesteps=36, fill="#60a5fa", tags=traj_tag)
        canvas.create_line(*coords, width=2, smooth=True, splinesteps=36, fill="#bfdbfe", tags=traj_tag)
    # draw points and arrows
    for p in points_list:
        x, y = p['x_px'], p['y_px']
        canvas.create_oval(x-7, y-7, x+7, y+7, fill="#111827", outline=p['color'], width=3, tags=traj_tag)
        canvas.create_text(x, y-18, text=f"{p['x_cm']:.0f},{p['y_cm']:.0f}", font=("Consolas", 9, "bold"), fill="#e6edf3", tags=traj_tag)
        rad = math.radians(p['angle'])
        ax = x + 18 * math.sin(rad)
        ay = y - 18 * math.cos(rad)
        canvas.create_line(x, y, ax, ay, arrow="last", width=2, fill="#7dd3fc", tags=traj_tag)
    # start/end highlight
    if points_list:
        s = points_list[0]; e = points_list[-1]
        canvas.create_oval(s['x_px']-12, s['y_px']-12, s['x_px']+12, s['y_px']+12, outline="#10b981", width=3, tags=traj_tag)
        canvas.create_oval(e['x_px']-12, e['y_px']-12, e['x_px']+12, e['y_px']+12, outline="#ef4444", width=3, tags=traj_tag)

redraw_trajectories(width_px, height_px)

# ---------- Robô visual ----------
ROBO_W, ROBO_H = 22, 26
robot_id = canvas.create_polygon([0,0,0,0,0,0], fill="#0f1724", outline="#111827", tags="robot")
glow_id = canvas.create_oval(0,0,0,0, outline="", width=0, tags="glow")

def draw_robot_at(x, y, angle):
    rad = math.radians(angle)
    w, h = ROBO_W/2, ROBO_H/2
    verts = [(-w,-h),(w,-h),(w,h),(-w,h)]
    pts = []
    for vx, vy in verts:
        xr = vx * math.cos(rad) - vy * math.sin(rad) + x
        yr = vx * math.sin(rad) + vy * math.cos(rad) + y
        pts.extend([xr, yr])
    canvas.coords(robot_id, *pts)
    glow_pad = 18
    canvas.coords(glow_id, x - w - glow_pad, y - h - glow_pad, x + w + glow_pad, y + h + glow_pad)

_glow_phase = 0.0
def pulse_glow():
    global _glow_phase
    _glow_phase += 0.07
    intensity = (math.sin(_glow_phase) + 1) / 2
    outer_width = 0 + intensity * 2
    def lerp(a,b,t):
        return int(a + (b-a)*t)
    c1 = (16,185,129)
    c2 = (56,189,248)
    t = 0.65*intensity + 0.35
    rc = lerp(c1[0], c2[0], t); gc = lerp(c1[1], c2[1], t); bc = lerp(c1[2], c2[2], t)
    hexc = f"#{rc:02x}{gc:02x}{bc:02x}"
    try:
        canvas.itemconfigure(glow_id, outline=hexc, width=outer_width)
    except Exception:
        pass
    root.after(40, pulse_glow)

# ---------- Mouse tracking: crosshair + position display ----------
crosshair_h = canvas.create_line(0,0,0,0, fill="#94a3b8", dash=(4,4), tags="mouse")
crosshair_v = canvas.create_line(0,0,0,0, fill="#94a3b8", dash=(4,4), tags="mouse")
mouse_dot = canvas.create_oval(0,0,0,0, fill="#fef3c7", outline="#f59e0b", width=2, tags="mouse")

def on_mouse_move(event):
    cx = canvas.canvasx(event.x)
    cy = canvas.canvasy(event.y)
    canvas.coords(crosshair_h, 0, cy, canvas.winfo_width(), cy)
    canvas.coords(crosshair_v, cx, 0, cx, canvas.winfo_height())
    r = 5
    canvas.coords(mouse_dot, cx-r, cy-r, cx+r, cy+r)
    current_w = canvas.winfo_width()
    current_h = canvas.winfo_height()
    if 0 <= cx <= current_w and 0 <= cy <= current_h:
        mx_cm, my_cm = pixel_to_cm(cx, cy, current_w, current_h)
        label_mouse.config(text=f"{int(cx)}px, {int(cy)}px  /  {mx_cm:.1f}cm, {my_cm:.1f}cm")
    else:
        label_mouse.config(text="fora do tapete")

canvas.bind("<Motion>", on_mouse_move)

# ---------- Controls: iniciar / pausar / reiniciar ----------
_anim_running = False
_anim_job = None

def reset_robot_to_start():
    if points_list:
        s = points_list[0]
        draw_robot_at(s['x_px'], s['y_px'], s.get('angle', 0))

def stop_animation():
    global _anim_running, _anim_job
    _anim_running = False
    if _anim_job:
        try:
            root.after_cancel(_anim_job)
        except Exception:
            pass
        _anim_job = None

def restart_animation():
    stop_animation()
    redraw_trajectories(canvas.winfo_width(), canvas.winfo_height())
    reset_robot_to_start()
    start_animation()

def start_animation():
    global _anim_running, _anim_job
    if _anim_running:
        return
    _anim_running = True
    _anim_job = root.after(1, lambda: animar_robo_vel(points_list))

btn_start = make_button("▶ Iniciar / Continuar", lambda: start_animation())
btn_pause = make_button("⏸ Pausar", lambda: stop_animation())
btn_restart = make_button("🔄 Reiniciar", lambda: restart_animation())

# ---------- Animation logic ----------
def animar_robo_vel(points, base_delay_ms=16):
    if not points:
        return
    speed_factor = slider_speed.get() if hasattr(slider_speed, "get") else float(slider_speed.get())
    current_w = canvas.winfo_width() or width_px
    current_h = canvas.winfo_height() or height_px

    def compute_steps_for_reto(start, end):
        px_per_cm = current_w / TAPETE_WIDTH_CM
        dx = (end['x_cm'] - start['x_cm']) * px_per_cm
        dy = -(end['y_cm'] - start['y_cm']) * px_per_cm
        dist = math.hypot(dx, dy)
        vel_cm_per_s = max(end.get('vel', 40), 1)
        px_per_s = vel_cm_per_s * px_per_cm * speed_factor
        if px_per_s <= 0:
            px_per_s = 1
        steps = max(int(dist / max(px_per_s * (base_delay_ms/1000), 1)), 1)
        return steps, dx, dy

    actions = []
    for i in range(len(points)-1):
        s = points[i]; e = points[i+1]
        if e['tipo'] == 'reto':
            steps, dx, dy = compute_steps_for_reto(s, e)
            actions.append(("reto", s, e, steps, dx, dy))
        elif e['tipo'] == 'giro':
            da = (e['angle'] - s['angle'])
            if da > 180: da -= 360
            if da < -180: da += 360
            ang_speed = max(abs(e.get('vel', 45)), 1)
            steps = max(int(abs(da) / (ang_speed * speed_factor * (base_delay_ms/1000))), 1)
            actions.append(("giro", s, e, steps, da, None))
        else:
            actions.append(("none", s, e, 1, 0, None))

    idx = 0
    sub = 0

    def step():
        nonlocal idx, sub
        global _anim_job, _anim_running

        if not _anim_running:
            return
        if idx >= len(actions):
            _anim_running = False
            return
        act = actions[idx]
        typ = act[0]
        s = act[1]; e = act[2]; passos = act[3]
        if typ == "reto":
            dx = act[4]; dy = act[5]
            t = sub / passos
            x_now = s['x_px'] + dx * t
            y_now = s['y_px'] + dy * t
            angle = math.degrees(math.atan2(-dy, dx))
            draw_robot_at(x_now, y_now, angle)
            label_pos.config(text=f"({pixel_to_cm(x_now, y_now, current_w, current_h)[0]:.1f}, {pixel_to_cm(x_now, y_now, current_w, current_h)[1]:.1f})")
            label_angle.config(text=f"{angle:.1f}")
        elif typ == "giro":
            delta_angle = act[4]
            t = sub / passos
            angle = s['angle'] + delta_angle * t
            x_now, y_now = s['x_px'], s['y_px']
            draw_robot_at(x_now, y_now, angle)
            label_pos.config(text=f"({s['x_cm']:.1f}, {s['y_cm']:.1f})")
            label_angle.config(text=f"{angle:.1f}")
        else:
            x_now, y_now, angle = s['x_px'], s['y_px'], s['angle']
            draw_robot_at(x_now, y_now, angle)

        sub += 1
        if sub >= passos:
            idx += 1
            sub = 0

        _anim_job = root.after(base_delay_ms, step)

    step()

# ---------- Zoom handler ----------
def on_zoom_change(value=None):
    try:
        z = float(slider_zoom.get())
    except Exception:
        z = float(slider_zoom.get())
    global width_px, height_px, img, photo
    width_px = int(img_original.width * z)
    height_px = int(img_original.height * z)
    img = img_original.resize((width_px, height_px), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    canvas.config(width=width_px, height=height_px)
    canvas.itemconfigure(canvas_img_id, image=photo)
    redraw_trajectories(width_px, height_px)
    reset_robot_to_start()

if CTK_AVAILABLE:
    slider_zoom.configure(command=lambda val: on_zoom_change(val))
else:
    slider_zoom.configure(command=lambda val: on_zoom_change(val))

# ---------- Start UI: position robot at start and pulse glow ----------
reset_robot_to_start()
pulse_glow()

# ---------- Key bindings ----------
def on_escape(e=None):
    root.quit()

root.bind("<Escape>", on_escape)

# ---------- Final: center window and run ----------
try:
    root.update_idletasks()
    w = root.winfo_screenwidth(); h = root.winfo_screenheight()
    size = tuple(int(_) for _ in root.geometry().split("+")[0].split("x"))
    root.geometry(f"{size[0]}x{size[1]}+{(w-size[0])//2}+{(h-size[1])//2}")
except Exception:
    pass

root.mainloop()
