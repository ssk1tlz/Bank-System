# Bank System 

This project is a web-based banking system application built using [Streamlit](https://streamlit.io/). The application allows users to register, log in, apply for loans, manage their accounts, and perform administrative tasks such as viewing and deleting user accounts.

## Features

- **User Registration:** Allows new users to register with a unique username and detailed personal information.
- **User Login:** Authenticated users can log in to access their personal dashboard.
- **Personal Dashboard:**
  - View and edit personal information.
  - Apply for new loans and manage existing loans.
  - View account balance and top-up the account.
- **Loan Management:**
  - Apply for loans with different interest rates and terms.
  - View loan details, including amount, interest, and status.
  - Make payments towards outstanding loans.
- **Admin Panel:**
  - View all registered users.
  - Delete user accounts (except for the admin).
  - Refresh the user list.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Streamlit
- APScheduler
- Pandas
- SQLite3 (for database management)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/bank-system.git
    cd bank-system
    ```

2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```bash
    streamlit run app.py
    ```

4. **Access the application:**

    The application will be accessible at `http://localhost:8501`.

### Database Setup

- The application uses a SQLite database to manage user accounts and loan information. The `initialize_db` function will automatically create the necessary tables if they don't exist.

### Scheduler for Credit Interest Updates

- The application includes a background scheduler using APScheduler to regularly update the interest on active loans. The scheduler runs every 10 seconds by default.

## Project Structure

- `app.py`: The main application file.
- `database.py`: Handles all database-related operations such as adding accounts, checking credentials, managing loans, etc.
- `requirements.txt`: Lists all the dependencies required by the project.

## Usage

### User Registration

- Go to the "Регистрация" page to create a new account.
- Ensure that the email follows the specified domain rules (`gmail.com` or `mail.ru`).
- The passport number must follow the format of two uppercase letters followed by seven digits.

### User Login and Dashboard

- After logging in, users will be redirected to their personal dashboard where they can manage their accounts and loans.

### Admin Panel

- Accessible via the "Администрирование" menu.
- Admins can view all registered users and delete user accounts.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

