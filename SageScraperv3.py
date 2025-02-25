import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import webbrowser
import threading
import time

# User-Agent header to mimic a real browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def scrape_url(base_url, keyword, progress_callback):
    try:
        response = requests.get(base_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        results = []
        total_links = len(links)
        
        for i, link in enumerate(links):
            full_url = urljoin(base_url, link['href'])
            try:
                link_response = requests.get(full_url, headers=HEADERS)
                link_response.raise_for_status()
                link_soup = BeautifulSoup(link_response.text, 'html.parser')
                text = link_soup.get_text(" ", strip=True)
                if keyword.lower() in text.lower():
                    description = ' '.join(text.split()[:20])  # First 20 words as description
                    results.append((full_url, description))
            except requests.exceptions.RequestException:
                pass  # Ignore failed links
            
            time.sleep(0.5)  # Reduced delay
            progress_callback(int((i + 1) / total_links * 100))
        
        return results
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Failed to connect to the server. Please check the URL and your internet connection.")
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve {base_url}: {e}")
    return []

def on_submit():
    url = url_entry.get()
    keyword = keyword_entry.get()
    if url and keyword:
        submit_button.config(state=tk.DISABLED)
        progress_bar["value"] = 0
        progress_label.config(text="Scraping in progress...")

        def update_progress(progress):
            root.after(0, lambda: progress_bar.config(value=progress))

        def scrape_and_display():
            results = scrape_url(url, keyword, update_progress)
            root.after(0, lambda: display_results(results))
            root.after(0, lambda: submit_button.config(state=tk.NORMAL))
            root.after(0, lambda: progress_label.config(text="Scraping complete."))

        threading.Thread(target=scrape_and_display, daemon=True).start()
    else:
        messagebox.showwarning("Input Error", "Please enter both URL and KEYWORD.")

def display_results(results):
    result_window = tk.Toplevel()
    result_window.title("Scraping Results")
    result_window.geometry("800x600")

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=100, height=30)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    for index, (url, description) in enumerate(results):
        text_area.insert(tk.END, f"URL: {url}\nDescription: {description}\n", f"link{index}")
        text_area.tag_config(f"link{index}", foreground="blue", underline=1)
        text_area.tag_bind(f"link{index}", "<Button-1>", lambda e, u=url: webbrowser.open_new(u))
        text_area.insert(tk.END, "\n" + "="*80 + "\n\n")
    
    # Menu for right-click context actions
    def copy_to_clipboard(event):
        selected_text = text_area.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected_text)
        root.update()
    
    menu = Menu(result_window, tearoff=0)
    menu.add_command(label="Copy", command=lambda: copy_to_clipboard(None))
    text_area.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

# GUI setup
root = tk.Tk()
root.title("Web Scraper")

tk.Label(root, text="URL:").grid(row=0, column=0)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1)

tk.Label(root, text="KEYWORD:").grid(row=1, column=0)
keyword_entry = tk.Entry(root, width=50)
keyword_entry.grid(row=1, column=1)

submit_button = tk.Button(root, text="Scrape", command=on_submit)
submit_button.grid(row=2, column=0, columnspan=2)

progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress_bar.grid(row=3, column=0, columnspan=2, pady=10)

progress_label = tk.Label(root, text="")
progress_label.grid(row=4, column=0, columnspan=2)

root.mainloop()
