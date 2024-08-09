from datetime import datetime
import streamlit as st
import re
from database import initialize_db, add_account, check_account, get_account, check_username_exists, check_passport_exists, check_id_number_exists, get_all_accounts, apply_for_credit, get_credits, close_credit, make_credit_payment, update_credit_interests, update_account, get_account_details, top_up_account, delete_user
import pandas as pd 
from apscheduler.schedulers.background import BackgroundScheduler
# Инициализация планировщика для регулярного обновления процентов по кредитам
scheduler = BackgroundScheduler()
scheduler.add_job(update_credit_interests, 'interval', seconds=10)
scheduler.start()


def app():
    initialize_db()  # Исправлено на initialize_db
    st.title("Bank System")

    menu = ["Регистрация", "Вход", "Поиск аккаунта", "Личный кабинет", "Администрирование"]
    choice = st.sidebar.selectbox("Меню", menu)

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if choice == "Регистрация":
        with st.form("register_form"):
            st.subheader("Регистрация нового аккаунта")
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type='password')
            surname = st.text_input("Фамилия")
            name = st.text_input("Имя")
            patronymic = st.text_input("Отчество", "")
            passport = st.text_input("Серия и номер паспорта")
            passport_issued_by = st.text_input("Кем выдан паспорт")
            passport_issue_date = st.date_input("Дата выдачи паспорта")
            id_number = st.text_input("Идентификационный номер")
            birth_place = st.text_input("Место рождения")
            birth_date = st.date_input("Дата рождения")
            registration_city = st.text_input("Город регистрации")
            current_address = st.text_input("Текущий адрес")
            phone = st.text_input("Телефон")
            email = st.text_input("Email")
            citizenship = st.text_input("Гражданство")
            disability = st.checkbox("Инвалидность")
            gender = st.selectbox("Пол", ["Мужской", "Женский"])
            marital_status = st.selectbox("Семейное положение", ["Женат/Замужем", "Не женат/Не замужем", "Разведен/Разведена"])
            pensioner = st.checkbox("Пенсионер")

            submitted = st.form_submit_button("Зарегистрироваться")
            if submitted:
                email_regex = r'^[a-zA-Z0-9._%+-]+@(gmail\.com|mail\.ru)$'
                valid_email = re.match(email_regex, email)
                passport_regex = r'^[A-Z]{2}\d{7}$'
                valid_passport = re.match(passport_regex, passport)
                username_exists = check_username_exists(username)
                passport_exists = check_passport_exists(passport)
                id_number_exists = check_id_number_exists(id_number)
                if not valid_email:
                    st.error("Email должен быть действительным и принадлежать доменам gmail.com или mail.ru.")
                elif not valid_passport:
                    st.error("Неверный формат серии и номера паспорта. Он должен содержать 2 заглавные буквы и 7 цифр.")
                elif username_exists:
                    st.error("Имя пользователя уже существует.")
                elif passport_exists:
                    st.error("Серия паспорта уже существует.")
                elif id_number_exists:
                    st.error("Идентификационный номер уже существует.")
                else:
                    # Если все проверки пройдены успешно, производим регистрацию пользователя
                    disability_str = "Да" if disability else "Нет"  # Пример использования чекбокса для инвалидности
                    pensioner_str = "Да" if pensioner else "Нет"  # Пример использования чекбокса для пенсионера
                    # Пример форматирования дат, предполагается, что у вас есть соответствующие поля ввода даты
                    passport_issue_date_str = passport_issue_date.strftime('%Y-%m-%d')
                    birth_date_str = birth_date.strftime('%Y-%m-%d')
                    result = add_account(username, password, surname, name, patronymic, passport, passport_issued_by, passport_issue_date_str, id_number, birth_place, birth_date_str, registration_city, current_address, phone, email, citizenship, disability_str, gender, marital_status, pensioner_str)
                    if result:
                        st.success("Аккаунт успешно зарегистрирован.")
                    else:
                        st.error("Произошла ошибка при регистрации аккаунта.")

    if st.session_state["logged_in"]:
        choice = "Личный кабинет"

    if choice == "Вход":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type='password')
        if st.button("Войти"):
            if check_account(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.experimental_rerun()  # Перезапускаем приложение для отображения личного кабинета
            else:
                st.error("Неверное имя пользователя или пароль")

    
    elif choice == "Личный кабинет" and st.session_state.get("logged_in", False):
        st.subheader("Личный кабинет")
        
        # Создаем вкладки
        tab1, tab2, tab3, tab4 = st.tabs(["Личная информация", "Оформление кредита", "Информация о кредитах", "Личный счёт"])
        
        with tab1:
            st.write("Личная информация пользователя")
            username = st.session_state.get("username")
            if username:
                account_details = get_account(username)
                if account_details:
                    # Отображение существующей информации
                    st.write(f"Имя пользователя: {account_details.username}")
                    st.write(f"Фамилия: {account_details.surname}")
                    st.write(f"Имя: {account_details.name}")
                    st.write(f"Email: {account_details.email}")
                    st.write(f"Дата рождения: {account_details.birth_date}")
                    st.write(f"Текущий адрес: {account_details.current_address}")
                    st.write(f"Серия и номер паспорта: {account_details.passport}")
                    st.write(f"Телефон: {account_details.phone}")
                    
                    # Кнопка для переключения в режим редактирования
                    if st.button('Редактировать данные'):
                        st.session_state['editing'] = True
                    
                    # Форма редактирования, активируется при нажатии кнопки "Редактировать данные"
                    if st.session_state.get('editing'):
                        with st.form("edit_form"):
                            new_email = st.text_input("Email", value=account_details.email)
                            new_phone = st.text_input("Телефон", value=account_details.phone)
                            new_address = st.text_input("Текущий адрес", value=account_details.current_address)
                            # Добавьте здесь другие поля для редактирования
                            
                            submit_changes = st.form_submit_button("Сохранить изменения")
                            
                            if submit_changes:
                                # Здесь логика для обновления данных в базе данных
                                update_account(username, new_email, new_phone, new_address)
                                st.success("Данные успешно обновлены!")
                                st.session_state['editing'] = False  # Выход из режима редактирования
                if st.button("Выйти"):
                    # Сброс состояния входа и других связанных с состоянием данных
                    for key in ["logged_in", "username", "editing"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Перезапускаем приложение, что приведёт к отображению формы входа
                    st.experimental_rerun()            
                        
        with tab2:
            st.write("Оформление нового кредита")
            # Форма для оформления нового кредита
            with st.form("credit_form"):
                credit_amount = st.number_input("Сумма кредита", min_value=1.0)
                credit_rate = st.selectbox("Процентная ставка", ["5%", "10%", "15%", "20%", "25%"])
                credit_term = st.selectbox("Срок кредита", ["1 год", "2 года", "3 года"])
                
                # Чекбокс для согласия с условиями договора
                agreement = st.checkbox("Я согласен с условиями договора")

                submit_credit = st.form_submit_button("Оформить кредит")
                
                if submit_credit:
                    if agreement:
                        rate_value = float(credit_rate.strip('%')) / 100
                        apply_for_credit(username, credit_amount, rate_value, credit_term)
                        st.success("Кредит успешно оформлен!")
                    else:
                        st.error("Для оформления кредита необходимо согласиться с условиями договора.")
                        
        with tab3:
            st.write("Информация о кредитах")
            # Выводим данные о кредитах пользователя
            credits = get_credits(username)
            if credits:
                formatted_credits = []
                for credit in credits:
                    paid_amount = credit.paid_amount
                    remaining_amount = max(0, (credit.amount + credit.accumulated_interest) - paid_amount)
                    formatted_credits.append({
                        "ID кредита": credit.credit_id,
                        "Сумма кредита": f"{credit.amount:.2f}",
                        "Накопленные проценты": f"{credit.accumulated_interest:.2f}",
                        "Внесено денег": f"{paid_amount:.2f}",
                        "Остаток до погашения": f"{remaining_amount:.2f}",
                        "Статус": credit.status,
                    })

                df_credits = pd.DataFrame(formatted_credits)
                st.dataframe(df_credits)
                st.markdown("## Погашение кредита")
                credit_id = st.selectbox(
                    "Выберите ID кредита для погашения",
                    [c['ID кредита'] for c in formatted_credits if c['Статус'] in ['active', 'due']]
                )
                payment_amount = st.number_input("Сумма погашения", min_value=0.0, format="%.2f")
                if st.button("Внести платеж"):
                    message = make_credit_payment(credit_id, payment_amount)
                    st.info(message)
        with tab4:
            st.write("Личный счёт")
            username = st.session_state.get("username")
            if username:
                user_account = get_account_details(username)  # Функция для получения деталей счёта пользователя
                if user_account:
                    st.write(f"Текущий баланс: {user_account.balance}")
                else:
                    st.write("Счёт не найден.")
            with st.form("account_top_up"):
                top_up_amount = st.number_input("Сумма пополнения", min_value=0.01, step=0.01, format="%.2f")
                top_up_submit = st.form_submit_button("Пополнить счёт")
                
                if top_up_submit:
                    result = top_up_account(username, top_up_amount)  # Функция для пополнения счёта
                    if result:
                        st.success("Счёт успешно пополнен.")
                    else:
                        st.error("Произошла ошибка при пополнении счёта.")

               
    elif choice == "Поиск аккаунта":
        st.subheader("Поиск аккаунта")
        search_username = st.text_input("Введите имя пользователя для поиска")
        if st.button("Поиск"):
            account = get_account(search_username)
            if account:
                st.write(f"Аккаунт найден: {account.username}")
            else:
                st.error("Аккаунт не найден")

            
    if choice == "Администрирование":
        if st.session_state["logged_in"] and st.session_state.get("is_admin", False):
         st.subheader("Панель администратора")
        
        # Получение всех пользователей из базы данных
        accounts = get_all_accounts()
        
        # Создание DataFrame из списка пользователей
        df = pd.DataFrame(accounts, columns=["Имя пользователя"])
        
        # Отображение DataFrame как таблицы
        st.dataframe(df)

        # Возможность удаления пользователей
        user_to_delete = st.text_input("Введите имя пользователя для удаления:")
        if st.button("Удалить пользователя"):
            if user_to_delete != "admin":  # Администратор не может удалить себя
                delete_user(user_to_delete)
                st.success(f"Пользователь {user_to_delete} успешно удален.")
            else:
                st.error("Вы не можете удалить себя.")
        
        # Кнопка для обновления списка пользователей
        if st.button("Обновить список"):
            accounts = get_all_accounts()
            df = pd.DataFrame(accounts, columns=["Имя пользователя"])
            st.dataframe(df)
      
    
            
if __name__ == "__main__":
    if not scheduler.running:  # Проверяем, что планировщик еще не запущен
        scheduler.add_job(update_credit_interests, 'interval', seconds=10)
        scheduler.start()
    app()