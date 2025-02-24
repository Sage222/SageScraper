import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import webbrowser

def scrape_url(base_url, keyword):
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        results = []

        for link in links:
            full_url = urljoin(base_url, link['href'])
            try:
                link_response = requests.get(full_url)
                link_soup = BeautifulSoup(link_response.text, 'html.parser')
                text = link_soup.get_text()
                if keyword.lower() in text.lower():
                    description = ' '.join(text.split()[:20])  # First 20 words as description
                    results.append((full_url, description))
            except requests.RequestException as e:
                print(f"Failed to retrieve {full_url}: {e}")

        return results
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve {base_url}: {e}")
        return []

def on_submit():
    url = url_entry.get()
    keyword = keyword_entry.get()
    if url and keyword:
        results = scrape_url(url, keyword)
        if results:
            display_results(results)
        else:
            messagebox.showinfo("Results", "No matching URLs found.")
    else:
        messagebox.showwarning("Input Error", "Please enter both URL and KEYWORD.")

def display_results(results):
    result_window = tk.Toplevel()
    result_window.title("Scraping Results")
    result_window.geometry("800x600")

    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=100, height=30)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    for url, description in results:
        text_area.insert(tk.END, f"URL: {url}\nDescription: {description}\n\n")
        text_area.insert(tk.END, "Click here to open URL\n", "hyperlink")
        text_area.tag_config("hyperlink", foreground="blue", underline=1)
        text_area.tag_bind("hyperlink", "<Button-1>", lambda e, url=url: webbrowser.open_new(url))
        text_area.insert(tk.END, "\n" + "="*80 + "\n\n")

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

root.mainloop()