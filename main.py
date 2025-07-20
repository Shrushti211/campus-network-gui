import customtkinter as ctk
from PIL import Image, ImageTk
import random
import datetime
import mysql.connector
from tkinter import messagebox
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os



# Initialize Users List and Posts
users = []
posts = []  # List to hold posts
current_user = None  # Track currently logged-in user

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Load the AI model
MODEL_NAME = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
 # Assuming you are using tkinter for UI alerts

def get_db_connection():
    """Establish and return MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="amico"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

def add_feed_post(username, content):
    """Insert a new post into the feed table"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO user_post (username, content) VALUES (%s, %s)"
            values = (username, content)
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo(title="congratulations",message="✅ Post added successfully!")
        except mysql.connector.Error as err:
            messagebox.showwarning(f"❌ Error inserting post: {err}")
        finally:
            cursor.close()
            conn.close()


def get_feed_posts():
    """Fetch and display all feed posts from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT username, content, created_at FROM user_post ORDER BY created_at DESC"
            cursor.execute(query)
            posts = cursor.fetchall()
            return posts if posts else []  # Return empty list if no posts
        except mysql.connector.Error as err:
            messagebox.showwarning(f"❌ Error fetching feed posts: {err}")
            return []
        finally:
            cursor.close()
            conn.close()




# def delete_user(username):
#     """Delete a user and cascade delete their posts"""
#     conn = get_db_connection()
#     if conn:
#         cursor = conn.cursor()
#         confirmation = input(f"Are you sure you want to delete user {username}? (yes/no): ")
#         if confirmation.lower() == 'yes':
#             query = "DELETE FROM user_info WHERE username = %s"
#             cursor.execute(query, (username))
#             conn.commit()
#             messagebox.showwarning("User deleted successfully!")
#         cursor.close()
#         conn.close()



def main():
    global window
    # Create main window
    window = ctk.CTk()
    window.geometry("900x600")
    window.title("AMICO💗")
    window.configure(bg="#D33682")

    # Set appearance mode and theme
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")  # Set default theme color

    show_main_screen()
    window.mainloop()

def show_main_screen():
    """Display the main AMICO screen with animated emojis."""
    for widget in window.winfo_children():
        widget.destroy()

    frame = ctk.CTkFrame(window, fg_color="#FFFFE0")
    frame.pack(fill="both", expand=True)

    text_label = ctk.CTkLabel(
        frame,
        text="AMICO",
        font=("Helvetica", 100, "bold"),
        text_color="#D5A499"
    )
    text_label.place(relx=0.5, rely=0.3, anchor="center")

    emojis = ["💗", "✌️", "❤️", "💕", "🤍", "😍", "😊", "🤞", "🫠", "🤓"]
    
    def animate_emoji():
        emoji = random.choice(emojis)  # Select a random emoji
        lbl = ctk.CTkLabel(frame, text=emoji, font=("Arial", 25), text_color="black")
        x = random.uniform(0.3, 0.9)
        y = random.uniform(0.3, 0.8)
        lbl.place(relx=x, rely=y)

        # Create the animation
        def move_label():
            x = random.uniform(0.1, 0.9)
            y = random.uniform(0.1, 0.8)
            lbl.place(relx=x, rely=y)
            window.after(1500, move_label)  # Repeat after 1.5 seconds

        move_label()  # Start animation for this emoji

    for _ in range(5):  # Animate up to 5 emojis simultaneously
        animate_emoji()

    # Redirect to the dashboard after animation (5 seconds)
    window.after(5000, show_dashboard)

def show_dashboard():
    """Display the dashboard with navigation bar."""                       
    for widget in window.winfo_children():
        widget.destroy()

    # Main Frame for Dashboard
    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    # Navigation Bar
    nav_bar = ctk.CTkFrame(main_frame, fg_color="#D5A499", height=50)
    nav_bar.pack(fill="x")  # Fill horizontal space

    # Navigation Buttons
    nav_items = [
                 ("More about AMICO", show_about), 
                 ("Log In", show_login),("Sign Up", show_signup),("AI Chatbot",show_bot),
                 ("Feed", show_feed if current_user else show_login),("Home", show_main_screen)]
    
    for item, command in nav_items:
        btn = ctk.CTkButton(
            nav_bar, text=item, fg_color="transparent",
            text_color="black", hover_color="#D5A499",
            font=("Arial", 14), corner_radius=0,
            command=command
        )
        btn.pack(side="right", padx=5, pady=5)  # Pack buttons to the right

    # Promotional Text and Search Feature
    promo_text = ctk.CTkLabel(
        main_frame, text="Search for your AMICO",
        font=("Arial", 30, "bold"), text_color="black"
    )
    promo_text.place(relx=0.1, rely=0.3, anchor="w")

    sub_text = ctk.CTkLabel(
        main_frame, text="Find your project partner, your guide, or a friend",
        font=("Arial", 18), text_color="black"
    )
    sub_text.place(relx=0.1, rely=0.4, anchor="w")

    # Search Button
    search_btn = ctk.CTkButton(
        main_frame, text="Search", fg_color="black",
        text_color="white", hover_color="black", font=("Arial", 16),
        command=show_search
    )
    search_btn.place(relx=0.1, rely=0.5, anchor="w")

    # Load and Display Image
    try:
        bg_image = Image.open("C:/Amico/people_new.png").convert("RGBA")  # Change to a valid image path
        bg_image = bg_image.resize((350, 350))  # Resize to fit UI
        bg_photo = ImageTk.PhotoImage(bg_image)

        window.bg_photo = bg_photo

        img_label = ctk.CTkLabel(main_frame, text="")
        img_label.configure(image=bg_photo) 
        img_label.image = bg_photo  # Keep reference to prevent garbage collection
        img_label.place(relx=0.8, rely=0.5, anchor="center")
    except Exception as e:
        print("Image loading error:", e)


def show_feed():

    """Display the user's feed with posts if logged in."""
    if current_user is None:
        return  # If not logged in, do nothing

    for widget in window.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="User Feed", font=("Helvetica", 24), text_color="black").pack(pady=10)

    # Scrollable Frame for posts
    scrollable_frame = ctk.CTkScrollableFrame(main_frame, width=600, height=400)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Fetch posts from the database
    posts = get_feed_posts()
    
    if not posts:  # If no posts, display message
        ctk.CTkLabel(scrollable_frame, text="No posts available.", font=("Arial", 14), text_color="gray").pack(pady=10)
    else:
        for post in posts:
            username, content, timestamp = post

            post_frame = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=10)
            post_frame.pack(fill="x", padx=5, pady=5)

            # Profile Picture Placeholder
            try:
                profile_img = Image.open("placeholder_profile.png")  
                profile_img = profile_img.resize((40, 40), Image.ANTIALIAS)
                profile_photo = ImageTk.PhotoImage(profile_img)
            except Exception:
                profile_photo = None
        
            if profile_photo:
                profile_label = ctk.CTkLabel(post_frame, image=profile_photo, text="")
                profile_label.image = profile_photo  
                profile_label.pack(side="left", padx=5, pady=5)

            # Post Details
            post_details_frame = ctk.CTkFrame(post_frame, fg_color="transparent")
            post_details_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)

            ctk.CTkLabel(post_details_frame, text=username, font=("Arial", 14, "bold")).pack(anchor="w")
            ctk.CTkLabel(post_details_frame, text=content, font=("Arial", 12), wraplength=500).pack(anchor="w")
            ctk.CTkLabel(post_details_frame, text=timestamp.strftime("%Y-%m-%d %H:%M:%S"), font=("Arial", 10, "italic")).pack(anchor="e")

    # Button to create a new post
    ctk.CTkButton(main_frame, text="Create New Post", command=new_post_screen,fg_color="#D5A499",hover_color = "#D5A499",text_color = "Black").pack(pady=10)
    ctk.CTkButton(main_frame, text="Back", command=show_dashboard, fg_color="#D5A499",hover_color = "#D5A499",text_color = "Black").pack(pady=10)

  
def show_bot():
      for widget in window.winfo_children():
         widget.destroy()
    
      main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
      main_frame.pack(fill="both", expand=True)

      chat_area = ctk.CTkTextbox(main_frame, width=550, height=350, wrap="word")
      chat_area.pack(pady=10)

      entry = ctk.CTkEntry(main_frame, width=400, placeholder_text="Type a message...")
      entry.pack(side="left", padx=10, pady=10)

      send_button = ctk.CTkButton(main_frame, text="Send",fg_color="#D5A499",hover_color = "#D5A499",text_color = "Black", command=lambda: get_response(chat_area, entry))
      send_button.pack(side="right", padx=10, pady=10)
    
      back_button = ctk.CTkButton(main_frame, text ="Back",fg_color="#D5A499",hover_color = "#D5A499",text_color = "Black", command= show_dashboard )
      back_button.pack(side="right",pady=10)

      return chat_area, entry





# chat_area, entry = show_bot()
chat_history = None  # Store chat history for better conversation flow

def get_response(chat_area, entry):
     global chat_history
     user_input = entry.get()
     if user_input:
         chat_area.insert("end", f"\nYou: {user_input}")
         entry.delete(0, "end")

         new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")

         if chat_history is not None:
             bot_input_ids = torch.cat([chat_history, new_input_ids], dim=-1)
         else:
             bot_input_ids = new_input_ids

         chat_history = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
         bot_reply = tokenizer.decode(chat_history[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

         chat_area.insert("end", f"\nBot: {bot_reply}")



def new_post_screen():
    """Display the screen for creating a new post."""
    for widget in window.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Create New Post", font=("Helvetica", 24), text_color="black").pack(pady=10)

    ctk.CTkLabel(main_frame, text="What's on your mind?", font=("Helvetica", 18)).pack(pady=10)

    post_entry = ctk.CTkEntry(main_frame, placeholder_text="Type your post here...", width=500)
    post_entry.pack(pady=5)

    def submit_post():
        content = post_entry.get().strip()
        if content:
            add_feed_post(current_user, content)  # Function to save post
            show_feed()  # Refresh feed after posting
        else:
            ctk.CTkLabel(main_frame, text="Post cannot be empty!", text_color="red").pack(pady=5)

    ctk.CTkButton(main_frame, text="Submit Post", command=submit_post, fg_color="#D5A499").pack(pady=10)
    ctk.CTkButton(main_frame, text="Back", command=show_feed, fg_color="#D5A499").pack(pady=10)




def show_login():
    """Display the login form."""
    for widget in window.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Login", font=("Helvetica", 24), text_color="black").pack(pady=10)

    username_entry = ctk.CTkEntry(main_frame, placeholder_text="Username", width=300)
    username_entry.pack(pady=5)

    password_entry = ctk.CTkEntry(main_frame, placeholder_text="Password", show="*", width=300)
    password_entry.pack(pady=5)

    def attempt_login():
        global current_user
        username = username_entry.get()
        password = password_entry.get()
        
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_info WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            
            if user:
                current_user = username
                messagebox.showinfo("Success", "Login successful!")
                show_dashboard()
            else:
                ctk.CTkLabel(main_frame, text="Login Failed!", text_color="red").pack(pady=10)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during login: {err}")
        finally:
            cursor.close()
            conn.close()

    ctk.CTkButton(main_frame, text="Login", command=attempt_login, fg_color="#D5A499",hover_color="#D5A499",text_color="black").pack(pady=10)
    ctk.CTkButton(main_frame, text="Back", command=show_dashboard, fg_color="#D5A499",hover_color="#D5A499",text_color="black").pack(pady=10)

def show_signup():
    """Display the signup form."""
    for widget in window.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Sign Up", font=("Helvetica", 24), text_color="black").pack(pady=10)

    username_entry = ctk.CTkEntry(main_frame, placeholder_text="Username", width=300)
    username_entry.pack(pady=5)

    password_entry = ctk.CTkEntry(main_frame, placeholder_text="Password", show="*", width=300)
    password_entry.pack(pady=5)

    confirm_password_entry = ctk.CTkEntry(main_frame, placeholder_text="Confirm Password", show="*", width=300)
    confirm_password_entry.pack(pady=5)

    branch_entry = ctk.CTkEntry(main_frame, placeholder_text="Branch", width=300)
    branch_entry.pack(pady=5)

    year_entry = ctk.CTkEntry(main_frame, placeholder_text="Year", width=300)
    year_entry.pack(pady=5)

    interest_entry = ctk.CTkEntry(main_frame, placeholder_text="Interest", width=300)
    interest_entry.pack(pady=5)

    academics_entry = ctk.CTkEntry(main_frame, placeholder_text="Academics(CGPA)", width=300)
    academics_entry.pack(pady=5)

    def register_user():
        """Register user in the database"""
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        branch = branch_entry.get()
        year = year_entry.get()
        interest = interest_entry.get()
        academics = academics_entry.get()

        # Basic validation
        if not (username and password and confirm_password and branch and year and interest and academics):
            messagebox.showerror("Error", "All fields are required!")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        try:
            year = int(year)
            academics = float(academics)
        except ValueError:
            messagebox.showerror("Error", "Year must be an integer & CGPA must be a decimal!")
            return

        if year < 1 or year > 5:
            messagebox.showerror("Error", "Year must be between 1 and 5!")
            return

        if academics < 0.0 or academics > 10.0:
            messagebox.showerror("Error", "CGPA must be between 0.0 and 10.0!")
            return

        # Insert into database
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_info (username, password, branch, year, interest, academics)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, password, branch, year, interest, academics))

            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            show_registration_confirmation(username)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    ctk.CTkButton(main_frame, text="Register", command=register_user, fg_color="#D5A499",hover_color="#D5A499",text_color="black").pack(pady=10)
    ctk.CTkButton(main_frame, text="Back", command=show_dashboard, fg_color="#D5A499",hover_color="#D5A499",text_color="black").pack(pady=10)

def show_registration_confirmation(username):
    """Display confirmation screen after successful registration."""
    for widget in window.winfo_children():
        widget.destroy()

    confirmation_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    confirmation_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(confirmation_frame, text="Registration Successful!", font=("Helvetica", 24), text_color="green").pack(pady=20)
    ctk.CTkLabel(confirmation_frame, text=f"Welcome, {username}!", font=("Arial", 18)).pack(pady=10)
    ctk.CTkButton(confirmation_frame, text="Go to Dashboard", command=show_dashboard, fg_color="#D5A499").pack(pady=10)

def show_search():
    """Display the search screen."""
    for widget in window.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Search for AMICO", font=("Helvetica", 24), text_color="black").pack(pady=10)

    search_entry = ctk.CTkEntry(main_frame, placeholder_text="Search by Name/Interest/Branch", width=300)
    search_entry.pack(pady=10)

    def search_profile():
        """Search for posts in the database based on username, branch, interest, or pointer."""
        query = search_entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a search query.")
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            search_query = """
                SELECT user_post.content, user_post.username, user_post.created_at
                FROM user_post 
                JOIN user_info ON user_post.username = user_info.username
                WHERE LOWER(user_info.username) LIKE %s
                   OR LOWER(user_info.branch) LIKE %s
                   OR LOWER(user_info.year) LIKE %s
                   OR LOWER(user_info.academics) LIKE %s
            """
            query_param = f"%{query}%"
            cursor.execute(search_query, (query_param, query_param, query_param, query_param))
            results = cursor.fetchall()

            if results:
                show_search_results(results)
            else:
                messagebox.showinfo("No Results", "No matching profiles found.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during search: {err}")
        finally:
            cursor.close()
            conn.close()

    # Search Button
    ctk.CTkButton(main_frame, text="Search", command=search_profile, fg_color="#D5A499", hover_color="#D5A499", text_color="black").pack(pady=10)
    
    # Back Button
    ctk.CTkButton(main_frame, text="Back", command=show_dashboard, fg_color="#D5A499", hover_color="#D5A499", text_color="black").pack(pady=10)

def show_search_results(results):
    """Display search results in a scrollable frame."""
    for widget in window.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(window, fg_color="#FFE3F2")
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(main_frame, text="Search Results", font=("Helvetica", 24), text_color="black").pack(pady=10)

    # Scrollable Frame for Results
    scrollable_frame = ctk.CTkScrollableFrame(main_frame, width=600, height=400, fg_color="white")
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    if not results:
        ctk.CTkLabel(scrollable_frame, text="No users found", font=("Arial", 15)).pack(pady=10)
    else:
        for content, username, created_at in results:  # Ensure order matches query result
            post_frame = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=8)
            post_frame.pack(fill="x", padx=5, pady=5)

            # Username
            ctk.CTkLabel(post_frame, text=f"👤 {username}", font=("Arial", 14, "bold"), text_color="black").pack(anchor="w", padx=10, pady=2)
            # Post Content
            ctk.CTkLabel(post_frame, text=f"📝 {content}", font=("Arial", 12), wraplength=500, justify="left").pack(anchor="w", padx=10, pady=2)
            # Timestamp
            ctk.CTkLabel(post_frame, text=created_at.strftime("%Y-%m-%d %H:%M:%S"), font=("Arial", 10, "italic"), text_color="gray").pack(anchor="e", padx=10, pady=2)

    # Back Button
    ctk.CTkButton(main_frame, text="Back", command=show_search, fg_color="#D5A499", hover_color="#D5A499", text_color="black").pack(pady=10)

def show_about():
    """Display information about AMICO in a modern and attractive way."""
    for widget in window.winfo_children():
        widget.destroy()

    # Main Frame with a soft gradient-like background
    main_frame = ctk.CTkFrame(window, fg_color="#FFEEF3")  # Light pink shade for a premium look
    main_frame.pack(fill="both", expand=True)

    # Title with Large Font
    ctk.CTkLabel(main_frame, text="💡 Welcome to AMICO!", font=("Helvetica", 30, "bold"), text_color="#333").pack(pady=20)

    # Scrollable Frame
    scrollable_frame = ctk.CTkScrollableFrame(main_frame, width=650, height=420, fg_color="white", corner_radius=12)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # About Text
    about_text = (
        "🌟 What is AMICO?\n"
        "AMICO is a next-gen social and professional networking platform that helps people connect with the right individuals. "
        "Whether you're looking for a mentor, project partner, or a friend, AMICO brings people together!\n\n"

        "🎯 Our Mission\n"
        "We aim to bridge the gap between individuals by fostering collaboration, knowledge sharing, and professional growth. "
        "At AMICO, we believe in the power of meaningful connections.\n\n"

        "🚀 Why Choose AMICO?\n"
        "- 🔗 Seamless Networking – Connect with like-minded people effortlessly.\n"
        "- 🎓 Professional & Academic Growth – Find mentors, project collaborators, and study partners.\n"
        "- 🏆 Showcase Your Talents – Highlight your skills, achievements, and interests.\n"
        "- 🌐 Advanced Search – Discover people based on name, branch, or expertise.\n"
        "- 🔒 Secure & Private – Your data is safe with us!\n\n"

        "💖 Join AMICO Today!\n"
        "Be part of an ever-growing community that thrives on learning, collaboration, and innovation. "
        "Find your AMICO and start your journey today! 🚀"
    )

    # Large Font Text
    ctk.CTkLabel(scrollable_frame, text=about_text, font=("Arial", 16, "bold"), text_color="black", justify="left", anchor="w", wraplength=600).pack(pady=15, padx=20)

    # Back Button with Bigger Font & Stylish Color
    ctk.CTkButton(main_frame, text="⬅ Back to Dashboard", command=show_dashboard, 
                  fg_color="#D5768B", hover_color="#C8647A", text_color="white", 
                  font=("Arial", 18, "bold"), corner_radius=10).pack(pady=20)

if __name__ == "__main__":
    main()