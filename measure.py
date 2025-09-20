import tkinter as tk
from PIL import Image, ImageTk
import math

#tapete
MAX_WIDTH = 800
MAX_HEIGHT = 600
TAPETE_WIDTH_CM = 200
TAPETE_HEIGHT_CM = 114

#moviemntacao do robo
cordenada_inicial = [(20, 20)]
movimentos = [

]

# calculo de cordenadas
angulo_atual = 0
x_atual, y_atual = cordenada_inicial[0]
coordenadas = [{'x_cm': x_atual, 'y_cm': y_atual, 'color': 'red'}]

for tipo, valor in movimentos:
    if tipo == "giro":
        angulo_atual = (angulo_atual + valor) % 360
    elif tipo == "reto":
        rad = math.radians(angulo_atual)
        x_novo = x_atual + valor * math.sin(rad)
        y_novo = y_atual + valor * math.cos(rad)  # Y cresce para cima em cm
        x_atual, y_atual = x_novo, y_novo
        coordenadas.append({'x_cm': x_atual, 'y_cm': y_atual, 'color': 'red'})

# --- Conversão cm ↔ pixels (Y invertido) ---
def cm_to_pixel(x_cm, y_cm, width_px, height_px):
    x_pixel = x_cm / TAPETE_WIDTH_CM * width_px
    y_pixel = (TAPETE_HEIGHT_CM - y_cm) / TAPETE_HEIGHT_CM * height_px  # <- Y invertido
    return x_pixel, y_pixel

def pixel_to_cm(x_pixel, y_pixel, width_px, height_px):
    x_cm = x_pixel / width_px * TAPETE_WIDTH_CM
    y_cm = TAPETE_HEIGHT_CM - (y_pixel / height_px * TAPETE_HEIGHT_CM)  # <- Y invertido
    return round(x_cm,1), round(y_cm,1)

# --- Desenha trajetos ---
def redraw_trajectories(canvas, points_list):
    canvas.delete("all")
    canvas.create_image(0,0,anchor=tk.NW,image=photo)

    color_groups = {}
    for pt in points_list:
        color_groups.setdefault(pt['color'],[]).append(pt)

    for color, pts in color_groups.items():
        for i in range(1,len(pts)):
            x0,y0 = pts[i-1]['x_px'], pts[i-1]['y_px']
            x1,y1 = pts[i]['x_px'], pts[i]['y_px']
            canvas.create_line(x0,y0,x1,y1,fill=color,width=2)
        for i,pt in enumerate(pts):
            x,y = pt['x_px'], pt['y_px']
            canvas.create_oval(x-5,y-5,x+5,y+5,fill=color,outline=color)
            canvas.create_text(x,y+12,text=f"Ponto {i+1}: ({round(pt['x_cm'],1)}, {round(pt['y_cm'],1)})",
                               font=("Arial",8),fill='black')
        if len(pts)>1:
            start, end = pts[0], pts[-1]
            canvas.create_oval(start['x_px']-8,start['y_px']-8,start['x_px']+8,start['y_px']+8,
                               outline='green',width=2)
            canvas.create_oval(end['x_px']-8,end['y_px']-8,end['x_px']+8,end['y_px']+8,
                               outline='red',width=2)

# --- Interface ---
root = tk.Tk()
root.withdraw()
win = tk.Toplevel(root)
win.title("Trajetos por cor")

# Carrega imagem
try:
    img = Image.open("estrategia_sem_caminho.png")
except FileNotFoundError:
    print("Erro: imagem não encontrada.")
    root.destroy()
    exit()

scale = min(MAX_WIDTH/img.width, MAX_HEIGHT/img.height,1)
width_px, height_px = int(img.width*scale), int(img.height*scale)
img = img.resize((width_px,height_px), Image.LANCZOS)
photo = ImageTk.PhotoImage(img)

canvas = tk.Canvas(win,width=width_px,height=height_px)
canvas.pack(side=tk.LEFT)
canvas.create_image(0,0,anchor=tk.NW,image=photo)

pos_label = tk.Label(win,text="",font=("Arial",12))
pos_label.pack(anchor=tk.NW,padx=10,pady=10)

# --- Lista global de pontos ---
points_list = []
all_points = coordenadas

for pt in all_points:
    x_px, y_px = cm_to_pixel(pt['x_cm'], pt['y_cm'], width_px, height_px)
    points_list.append({'x_px': x_px,'y_px': y_px,'x_cm': pt['x_cm'],'y_cm': pt['y_cm'],'color': pt['color']})

# --- Eventos ---
current_color = 'red'

def mouse_move(event):
    x_cm, y_cm = pixel_to_cm(event.x,event.y,width_px,height_px)
    pos_label.config(text=f"Mouse: ({x_cm} cm, {y_cm} cm)")

def click_event(event):
    x_px, y_px = event.x,event.y
    x_cm, y_cm = pixel_to_cm(x_px,y_px,width_px,height_px)
    points_list.append({'x_px': x_px,'y_px': y_px,'x_cm': x_cm,'y_cm': y_cm,'color': current_color})
    redraw_trajectories(canvas,points_list)

def key_event(event):
    global current_color, points_list
    key = event.char.lower()
    color_map = {'r':'red','b':'blue','y':'yellow','g':'green','p':'purple'}

    if key in color_map:
        current_color = color_map[key]
    elif key=='e':
        points_list.clear()
        redraw_trajectories(canvas,points_list)
    elif key=='\x1b':
        root.destroy()

canvas.bind("<Button-1>", click_event)
canvas.bind("<Motion>", mouse_move)
win.bind("<Key>", key_event)

# --- Desenha trajetos iniciais ---
redraw_trajectories(canvas,points_list)

root.mainloop()