import tkinter as tk
import json
from tkinter import messagebox
from color_changer import adjust_color_brightness_hex

class VirtualPanelApp:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.root = tk.Tk()
        self.setup_window()
        self.leds = []  # List to store LEDs in the order they are created
        self.buttons= [] 
        self.setup_elements()
    
    def load_config(self, filename):
        config = {'elements': []}
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    element = json.loads(line.replace("'", '"'))
                    if element['dev'] == 'GLOBAL':
                        config['GLOBAL'] = element
                    else:
                        config['elements'].append(element)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading config: {e}")
        
        return config
    
    def setup_window(self):
        global_config = self.config.get('GLOBAL', {})
        self.root.title(global_config.get('title', 'Panel'))
        geometry = global_config.get('geometry', '800x600+100+100')
        self.root.geometry(geometry)
    
    def setup_elements(self):
        i = 0
        for element in self.config.get('elements', []):
            dev = element['dev']
            if dev == 'TEXT':
                self.create_text(element)
            elif dev == 'LED':
                self.create_led(element)
            elif dev == 'BAR':
                self.create_bar(element)
            elif dev == 'BUTTON':
                self.create_button(element, i)
                i += 1
            elif dev == 'SWITCH':
                self.create_switch(element, i)
                i += 1
    
    def create_text(self, config):
        text = config.get('text', '')
        size = config.get('size', 12)
        color = config.get('color', 'black')
        x, y = config.get('x', 0), config.get('y', 0)
        label = tk.Label(self.root, text=text, font=('Arial', size), fg=color)
        label.place(x=x, y=y)
    
    def create_led(self, config):
        color = config.get('color', 'red')
        bright_col=adjust_color_brightness_hex(color,1.5)
        dark_col=adjust_color_brightness_hex(color,0.3)
        size = config.get('size', 15)
        x, y = config.get('x', 0), config.get('y', 0)
        led = tk.Canvas(self.root, width=size, height=size, bg='black', highlightthickness=0)
        oval_id = led.create_oval(0, 0, size, size, fill=bright_col)
        led.place(x=x, y=y)
        
        # Append LED reference to the list
        self.leds.append({'canvas': led, 'oval_id': oval_id,'bright': bright_col, 'dark':dark_col})

    def create_bar(self, config):
        color = config.get('color', 'red')
        bright_col=adjust_color_brightness_hex(color,1.5)
        dark_col=adjust_color_brightness_hex(color,0.5)
        length = config.get('len', 8)
        size = config.get('size', 15)
        x, y = config.get('x', 0), config.get('y', 0)
        for i in range(length):
            led = tk.Canvas(self.root, width=size, height=size * 3, bg='black', highlightthickness=0)
            rect_id = led.create_rectangle(0, 0, size, size * 3, fill=bright_col)
            led.place(x=x + i * size, y=y)
            
            # Append each LED in the bar to the list
            self.leds.append({'canvas': led, 'rect_id': rect_id,'bright': bright_col, 'dark':dark_col})
    
    def create_button(self, config, i):
        is_act=config.get('active',1)
        size = config.get('size', 50)
        x, y = config.get('x', 0), config.get('y', 0)
        button_index = i
        
        # Create a Canvas-based square button
        button_canvas = tk.Canvas(self.root, width=size, height=size, highlightthickness=0)
        button_id = button_canvas.create_rectangle(0, 0, size, size, fill="green" if is_act else "black")
        button_canvas.place(x=x, y=y)
        
        # Store the button's canvas
        self.buttons.append(button_canvas)
        
        # Bind the button to toggle LED color
        button_canvas.bind("<Button-1>", lambda event, idx=button_index: self.toggle_led_by_button(idx, button_canvas, button_id))
    
    def create_switch(self, config, i):
        size = config.get('size', 50)
        x, y = config.get('x', 0), config.get('y', 0)
        switch_index = i
        
        # Create a Canvas-based switch
        switch_canvas = tk.Canvas(self.root, width=size, height=size*2, highlightthickness=0)
        rect_id_top = switch_canvas.create_rectangle(0, 0, size, size, fill="green")
        rect_id_bottom = switch_canvas.create_rectangle(0, size, size, size*2, fill="black")
        switch_canvas.create_text(size / 2, size / 4, text="ON",  font=('Arial', 12))
        switch_canvas.create_text(size / 2, size + size / 4, text="OFF",  font=('Arial', 12))
        switch_canvas.place(x=x, y=y)
        self.buttons.append(switch_canvas)

        switch_canvas.bind("<Button-1>", lambda event, idx=switch_index: self.toggle_led_by_switch(idx, switch_canvas, rect_id_bottom,rect_id_top))
    
    def toggle_led_by_button(self, index, button_canvas, button_id):
            if 0 <= index < len(self.leds):
                led_info = self.leds[index]
                canvas = led_info['canvas']
                item_id = led_info['oval_id'] if 'oval_id' in led_info else led_info['rect_id']
                current_color = canvas.itemcget(item_id, 'fill')
                if current_color==led_info['bright']:
                    canvas.itemconfig(item_id, fill=led_info['dark'])
                else:
                    canvas.itemconfig(item_id, fill=led_info['bright'])
            # Toggle the button color
            current_color = button_canvas.itemcget(button_id, 'fill')
            new_color = 'green' if current_color == 'black' else 'black'
            button_canvas.itemconfig(button_id, fill=new_color)
    
    def toggle_led_by_switch(self, index, switch_canvas, rect_id_bottom,rect_id_top):
            if 0 <= index < len(self.leds):
                led_info = self.leds[index]
                canvas = led_info['canvas']
                item_id = led_info['oval_id'] if 'oval_id' in led_info else led_info['rect_id']
                current_color = canvas.itemcget(item_id, 'fill')
                if current_color==led_info['bright']:
                    canvas.itemconfig(item_id, fill=led_info['dark'])
                else:
                    canvas.itemconfig(item_id, fill=led_info['bright'])

            current_bot_color = switch_canvas.itemcget(rect_id_bottom, 'fill')
            if current_bot_color=='green':
                switch_canvas.itemconfig(rect_id_bottom,fill='black')
                switch_canvas.itemconfig(rect_id_top,fill='green')
            else:
                switch_canvas.itemconfig(rect_id_bottom,fill='green')
                switch_canvas.itemconfig(rect_id_top,fill='black')


        

    def run(self):
        self.root.mainloop() 

if __name__ == "__main__":
    app = VirtualPanelApp('config.txt')
    app.run()

