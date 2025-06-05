import webbrowser
from tkinter import Tk, Button

LOGIN_URL = 'http://localhost:5000/login'


def open_login():
    webbrowser.open(LOGIN_URL)


def main():
    root = Tk()
    root.title('Tesla Login')
    btn = Button(root, text='Login with Tesla', command=open_login)
    btn.pack(padx=20, pady=20)
    root.mainloop()


if __name__ == '__main__':
    main()
