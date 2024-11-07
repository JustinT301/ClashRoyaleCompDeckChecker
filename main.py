"""
Clash Royale Deck Scouting App
Use for CRL Scouting or Ranked Scouting
"""
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import urllib.request
import requests
import json
import os
import csv
import sys
#import traceback
from PIL import Image, ImageTk
from dotenv import load_dotenv

class DropDownWithEntry(tk.Frame): #Create dropdown menu to select players
    def __init__(self, master=None, options_dict=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.options_dict = options_dict if options_dict else {}
        self.keys = list(self.options_dict.keys())  # Get keys for dropdown
        
        self.var = tk.StringVar()
        
        self.entry = tk.Entry(self, textvariable=self.var,font=('Consolas', 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.dropdown = ttk.Combobox(self, values=self.keys,font=('Consolas', 10))
        self.dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dropdown.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.var.trace_add("write", self.on_entry_change)

        self.add_button = tk.Button(self, text="Add Player",font=('Consolas', 10), command=self.add_player)
        self.add_button.pack(side=tk.RIGHT, padx=5)

    def on_combobox_select(self, event):

        selected_key = self.dropdown.get()
        if selected_key in self.options_dict:
            selected_value = self.options_dict[selected_key]
            self.var.set(selected_value)

            self.dropdown.set(selected_key)

    def on_entry_change(self, *args):

        entry_text = self.var.get()
        key = next((k for k, v in self.options_dict.items() if v == entry_text), None)
        if key:
            self.dropdown.set(key)
        else:

            if self.dropdown.get() in self.keys:
                self.dropdown.set('')

    def get(self):

        return self.var.get()
    
    def add_player(self):
        new_key = self.dropdown.get().strip()
        new_value = self.var.get().strip()
        if new_key and new_value and new_key not in self.options_dict:
            self.options_dict[new_key] = new_value
            save_options_to_csv(self.options_dict)
            self.keys = list(self.options_dict.keys())  # Update dropdown values
            self.dropdown['values'] = self.keys
            messagebox.showinfo("Success", "Player added successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter valid and unique username and player tag.")

class ScrollableFrame(tk.Frame): #Create frame with scrollbar
    def __init__(self, parent, sync_scroll=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.on_scroll)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.sync_scroll = sync_scroll

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_scroll(self, *args):
        self.canvas.yview_moveto(float(args[1]))
        if self.sync_scroll:
            self.sync_scroll.canvas.yview_moveto(float(args[1]))

def custom_round(number): #for elixir average to be displayed like in Clash Royale
    
    decimal_part = number % 1

    if decimal_part == 0.125:
        return number - 0.025  # round down to 0.1
    elif decimal_part == 0.25:
        return number + 0.05  # round up to 0.3
    elif decimal_part == 0.375:
        return number + 0.025  # round up to 0.4
    elif decimal_part == 0.5:
        return number  # stay as 0.5
    elif decimal_part == 0.625:
        return number - 0.025  # round up to 0.6
    elif decimal_part == 0.75:
        return number + 0.05  # round up to 0.8
    elif decimal_part == 0.875:
        return number + 0.025  # round up to 0.9
    elif decimal_part == 0.0:
        return number #keep it as 0.0
    else:
        return round(number)
    
def plot_pie_chart(data):
    colors = cm.tab20.colors[:len(data)]
    fig, ax = plt.subplots()
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')

    return fig

def display_pie_chart(data, x):
    
    global pie_chart_canvas
    global pie_chart_canvas2

    if pie_chart_canvas and x==1:
        pie_chart_canvas.get_tk_widget().destroy() 
        pie_chart_canvas.figure.clear()
        plt.close(pie_chart_canvas.figure)
    
    if pie_chart_canvas2 and x==2:
        pie_chart_canvas2.get_tk_widget().destroy()
        pie_chart_canvas2.figure.clear()
        plt.close(pie_chart_canvas2.figure)

    if x==1:
        fig = plot_pie_chart(data)
        pie_chart_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame1.scrollable_frame)
        pie_chart_canvas.draw()
        pie_chart_canvas.get_tk_widget().pack()
    else:
        fig = plot_pie_chart(data)
        pie_chart_canvas2 = FigureCanvasTkAgg(fig, master=scrollable_frame2.scrollable_frame)
        pie_chart_canvas2.draw()
        pie_chart_canvas2.get_tk_widget().pack()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_options_from_csv():
    options = {}
    csv_path = resource_path(CSV_FILE_PATH)
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    options[row[0]] = row[1]
    return options

def save_options_to_csv(options_dict): #save players to .csv file
    csv_path = resource_path(CSV_FILE_PATH)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for key, value in options_dict.items():
            writer.writerow([key, value])

def friendlies(data, vs_image, red_line, player_role, wincons, y, frame):
    #Displays 1v1 and duels battles, sets are divided by a red line
    evolutions=["Archers","Barbarians","Bats","Battle Ram", "Bomber","Firecracker"
                ,"Goblin Barrel","Goblin Cage","Goblin Drill","Goblin Giant"
                ,"Ice Spirit","Knight","Mortar","Royal Giant","Royal Recruits"
                ,"Skeletons","Tesla","Valkyrie","Wall Breakers","Wizard","Zap"
                ,"P.E.K.K.A","Mega Knight", "Electro Dragon", "Musketeer", "Cannon"]
    elixir_list=[]
    elixir_index=0
    name_list=[]
    name_count=0
    crowns_list=[]
    crowns_index=0
    numbers_list=[1,2,9,10,17,18,25,26]
    total_card_count=0
    for entry in data:
        if entry['gameMode']['name'] == "Friendly" or entry['gameMode']['name'] == "Duel_1v1_Friendly":
            for player in entry[player_role]:
                friendlies_frame = tk.Frame(frame.scrollable_frame)
                friendlies_frame.pack()
                red_line_label = tk.Label(friendlies_frame, image = red_line)
                red_line_label.image = red_line
                red_line_label.pack(side=tk.TOP, padx=5)
                total_cost=0
                card_count=0
                card_images = []
                
                for card in player['cards']:
                    card_name = card['name']
                    card_count+=1
                    total_card_count+=1
                    if card_count in numbers_list:
                        if card_name in evolutions:
                            card_image_path = f"images/Evos/Evo_{card_name}.png"
                        else:
                            card_image_path = f"images/Cards/Card_{card_name}.png"
                    else:
                        card_image_path = f"images/Cards/Card_{card_name}.png"
                    
                    if card_name != "Mirror":
                        total_cost+=int(card['elixirCost'])
                    
                    if card_count in [8,16,24,32]:
                        avg_cost = total_cost/8
                        avg_cost = custom_round(avg_cost)
                        elixir_list.append(avg_cost)
                        total_cost=0
                        if y==2:
                            name_list.append(player['name'])
                    
                    if os.path.exists(card_image_path):
                        card_image = Image.open(card_image_path)
                        card_image = card_image.resize((80,110))
                        card_image = ImageTk.PhotoImage(card_image)
                        card_images.append(card_image)
                    
                    card_name = str(card['name'])
                    if card_name in wincons:
                        wincons[card_name]+=1
                
                if entry['gameMode']['name'] == "Friendly":
                    crowns=player['crowns']
                    crowns_list.append(crowns)
                if entry['gameMode']['name'] == "Duel_1v1_Friendly":
                    for rounds in player['rounds']:
                        crowns_list.append(rounds['crowns'])
                
                # Display cards in groups of 8 per row
                num_cards = len(card_images)
                for i in range(0, num_cards, 8):
                    friendlies_frame = tk.Frame(frame.scrollable_frame)
                    friendlies_frame.pack()
                    for j in range(8):
                        if i + j < num_cards:
                            label = tk.Label(friendlies_frame, image=card_images[i + j])
                            label.image = card_images[i + j]
                            label.pack(side=tk.LEFT, padx=5)
                            if j==7:
                                if y==1:
                                    vs_label = tk.Label(friendlies_frame, image = vs_image)
                                    vs_label.image = vs_image
                                    vs_label.pack(side=tk.RIGHT, padx=5)
                                
                                elif y==2:
                                    name_label = tk.Label(friendlies_frame, text=f'{name_list[name_count]}',font=('Consolas', 10, 'bold'),bg='yellow')
                                    name_label.pack(side=tk.RIGHT, padx=5)
                                    name_count+=1
                                crowns_label = tk.Label(friendlies_frame, text=f'Crowns: {crowns_list[crowns_index]}',font=('Consolas', 10))
                                crowns_label.pack(side=tk.TOP,pady=20,padx=5)
                                crowns_index+=1
                                elixir_label = tk.Label(friendlies_frame, text=f'Avg: {elixir_list[elixir_index]}',font=('Consolas', 10))
                                elixir_label.pack(pady=5,padx=5)
                                elixir_index+=1
                                
    if total_card_count==0:
            friendlies_label.config(text="No Friendly Battles or Duels Battles in Battlelog",font=('Consolas', 10))
            scrollable_frame1.destroy()
            scrollable_frame2.destroy()
    else:
        wincons = {card: count for card, count in wincons.items() if count != 0}
        display_pie_chart(wincons,y)


def fetch_data():
    global scrollable_frame1
    global scrollable_frame2
    global path_of_legend_frame
    global friendlies_label
    global paned_window

    vs_image = Image.open("images/Misc/VS.png")
    vs_image = vs_image.resize((50,50))
    vs_image = ImageTk.PhotoImage(vs_image)
    red_line = Image.open("images/Misc/redline.png")
    red_line = red_line.resize((950,20))
    red_line = ImageTk.PhotoImage(red_line)
        
    win_conditions1 = {'Goblin Drill':0, 'Wall Breakers':0, 'Giant':0, 'Golem':0, 'Ram Rider':0, 'Lavahound':0,
                      'Skeleton Barrel':0, 'Goblin Barrel':0, 'Electro Giant':0, 'Battle Ram':0, 'Royal Hogs':0,
                      'Graveyard':0, 'Miner':0, 'Balloon':0, 'Sparky':0, 'Hog Rider':0, 'Goblin Giant':0,
                    'Royal Giant':0, 'Elixir Golem':0, 'X-Bow':0, 'Mortar':0, 'Goblin Giant':0, 'Three Musketeers':0,}

    win_conditions2 = win_conditions1.copy()
    

    playertag = player_tag_dropdown.get().upper().strip()
    if not playertag:
        messagebox.showerror("Error", "Please enter a player tag.")
        return
    if '#' in playertag:
        playertag = playertag.replace('#','')
    
    try:
        # Clear previous
        if hasattr(scrollable_frame1, 'destroy'):
            scrollable_frame1.destroy()

        if hasattr(scrollable_frame2, 'destroy'):
            scrollable_frame2.destroy()
        
        if hasattr(paned_window, 'destroy'):
            paned_window.destroy()

        if hasattr(path_of_legend_frame, 'destroy'):
            path_of_legend_frame.destroy()

        if hasattr(friendlies_label, 'destroy'):
            friendlies_label.destroy()

        friendlies_label = tk.Label(root, text="Friendly Battles/Duels Battles",font=('Consolas', 10))
        friendlies_label.pack(pady=10)
        """"""
        base_url = "https://api.clashroyale.com/v1"
        endpoint = f"/players/%23{playertag}/battlelog"
        request = urllib.request.Request(base_url + endpoint, None, {"Authorization": "Bearer %s" % API_TOKEN})
        response = urllib.request.urlopen(request).read().decode("utf-8")
        data = json.loads(response)
        """
        headers = {
            'Authorization': f'Bearer {API_TOKEN}'
        }
        url = f'https://api.clashroyale.com/v1/players/{playertag}/battlelog'
        data = requests.get(url, headers=headers)
        """
        
        paned_window=tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)

        sync_scroll = ScrollableFrame(paned_window)

        scrollable_frame1 = ScrollableFrame(paned_window, sync_scroll=sync_scroll)
        scrollable_frame2 = ScrollableFrame(paned_window, sync_scroll=scrollable_frame1)

        paned_window.add(scrollable_frame1, stretch="always")
        paned_window.add(scrollable_frame2, stretch="always")

        #Friendlies/Duels 1v1s
        friendlies(data, vs_image, red_line, 'team', win_conditions1, 1, scrollable_frame1)
        friendlies(data, vs_image, red_line, 'opponent', win_conditions2, 2, scrollable_frame2)


        #Path Of Legends (Ranked Play)
        most_recent_path_of_legend = None
        for entry in data:
            if entry["type"] == "pathOfLegend":
                most_recent_path_of_legend = entry
                break

        if most_recent_path_of_legend != None:
            for key in most_recent_path_of_legend["team"]:

                path_of_legend_frame = tk.Frame(root)
                path_of_legend_frame.pack(pady=5)
                
                username_label = tk.Label(path_of_legend_frame, text=f"Username: {most_recent_path_of_legend['team'][0]['name']}",font=('Consolas', 10))
                username_label.pack()
                card_images2 = []

                try: 
                    if key["startingTrophies"]:
                        medals_label = tk.Label(path_of_legend_frame, text=f"Medals: {most_recent_path_of_legend['team'][0]['startingTrophies']}",font=('Consolas', 10))
                        medals_label.pack()
                        global_rank_label = tk.Label(path_of_legend_frame, text=f"Global Rank: {most_recent_path_of_legend['team'][0]['globalRank']}",font=('Consolas', 10))
                        global_rank_label.pack()
                except KeyError:
                    unranked_label = tk.Label(path_of_legend_frame, text="Not in Ultimate Champion",font=('Consolas', 10))
                    unranked_label.pack()
                pol_label = tk.Label(path_of_legend_frame, text="Path Of Legends (Ranked) Deck",font=('Consolas', 10))
                pol_label.pack()

                total_cost=0
                card_count=0
                for card in key['cards']:
                    card_name = card['name']

                    if card_count==0 or card_count==1:
                        card_image_path = f"images/Evos/Evo_{card_name}.png"
                    else:
                        card_image_path = f"images/Cards/Card_{card_name}.png"

                    if os.path.exists(card_image_path):
                        card_image = Image.open(card_image_path)
                        card_image = card_image.resize((80,110))
                        card_image = ImageTk.PhotoImage(card_image)
                        card_images2.append(card_image)
                        
                    card_count+=1
                    if card_name != "Mirror":
                        total_cost+=int(card['elixirCost'])
                    if card_count == 8:
                        avg_cost = total_cost/8
                        avg_cost = custom_round(avg_cost)
                
            for i in range(min(8, len(card_images2))):
                label = tk.Label(path_of_legend_frame, image=card_images2[i])
                label.image = card_images2[i]
                label.pack(side=tk.LEFT)
            
            avg_cost_label = tk.Label(path_of_legend_frame, text=f"Avg Cost: {avg_cost}",font=('Consolas', 10))
            avg_cost_label.pack(side=tk.RIGHT, padx=5)
        else:
            path_of_legend_frame = tk.Frame(root)
            path_of_legend_frame.pack(pady=5)
            no_pol_label = tk.Label(path_of_legend_frame, text=f"No recent Path of Legends games played",font=('Consolas', 10))
            no_pol_label.pack()

        root.geometry("1920x1080")

    except Exception as e:
        #tb_str = traceback.format_exc()
        #messagebox.showerror("Error", f"An error occurred:\n\n{tb_str}")
        messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")
        print(e)

def on_close():
    root.destroy()
    plt.close('all')


load_dotenv('.env.local')
API_TOKEN = os.getenv('API_TOKEN')
CSV_FILE_PATH = 'player_tags.csv'

path_of_legend_frame=None
friendlies_label=None
pie_chart_canvas = None
pie_chart_canvas2 = None
paned_window=None

# Initialize tkinter
root = tk.Tk()
root.title("Clash Royale League Deck Checker")
root.geometry("500x500")

# Player tag input
player_tag_label = tk.Label(root, text="Input Player Tag in Left Box and Username in Right Box to add player,\nor use Dropdown Menu for a currently stored player:",font=('Consolas', 10))
player_tag_label.pack(pady=10)

#Top Competitive players to store in dropdown menu
options_dict = load_options_from_csv()

# Initialize DropDownWithEntry
player_tag_dropdown = DropDownWithEntry(root, options_dict)
player_tag_dropdown.pack(pady=10, fill=tk.NONE)

# Fetch button
fetch_button = tk.Button(root, text="Fetch Decks",font=('Consolas', 10), command=fetch_data)
fetch_button.pack(pady=10)

# Scrollable frame to display cards
scrollable_frame1 = ScrollableFrame(root)
scrollable_frame1.pack(fill="both", expand=True, pady=10)
scrollable_frame2 = ScrollableFrame(root)
scrollable_frame2.pack(fill="both", expand=True, pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()