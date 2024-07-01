import streamlit as st
import mysql.connector
import streamlit.components.v1 as components
from streamlit_modal import Modal, contextmanager


class MariaDBURID:
    def __init__(self, host, port, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def get_database_list(self):
        self.cursor.execute("SHOW DATABASES")
        database_list = [row[0] for row in self.cursor.fetchall()]
        return database_list

    def get_table_list(self, database):
        self.cursor.execute(f"SHOW TABLES FROM {database}")
        table_list = [row[0] for row in self.cursor.fetchall()]
        return table_list

    def get_table_schema(self, database, table):
        self.cursor.execute(f"DESCRIBE {database}.{table}")
        table_schema = self.cursor.fetchall()
        return table_schema

    def get_user_list(self):
        self.cursor.execute("SELECT user FROM mysql.user")
        user_list = [row[0] for row in self.cursor.fetchall()]
        return user_list

    def execute_query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def insert_data(self, table, columns, values):
        columns_str = ', '.join(columns)
        values_str = ', '.join(["%s"] * len(values))
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
        self.cursor.execute(query, values)
        self.connection.commit()

    def insert_data_ignore_duplicates(self, table, columns, values):
        columns_str = ', '.join(columns)
        values_str = ', '.join(["%s"] * len(values))
        query = f"INSERT IGNORE INTO {table} ({columns_str}) VALUES ({values_str})"
        self.cursor.execute(query, values)
        self.connection.commit()

    def insert_data_with_conditions(self, table, columns, values, cond, cond_values):
        columns_str = ', '.join(columns)
        values_str = ', '.join(["%s"] * len(values))
        query = f"INSERT INTO {table} ({columns_str}) SELECT {values_str} WHERE {cond}"
        self.cursor.execute(query, values + cond_values)
        self.connection.commit()

    def update_data(self, table, columns, values, condition):
        columns_str = ', '.join([f"{col} = %s" for col in columns])
        query = f"UPDATE {table} SET {columns_str} WHERE {condition}"
        self.cursor.execute(query, values)
        self.connection.commit()

    def insert_data_on_duplicate_key_update(self, table, columns, values, update_columns, update_values, cond):
        columns_str = ', '.join(columns)
        values_str = ', '.join(["%s"] * len(values))
        update_str = ', '.join([f"{column} = %s" for column in update_columns])
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str}) ON DUPLICATE KEY UPDATE {update_str} {cond}"
        self.cursor.execute(query, values + update_values)
        self.connection.commit()

    def delete_data(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"
        self.cursor.execute(query)
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()


class MyModal(Modal):
    def open(self):
        st.session_state[f'{self.key}-opened'] = True

    @contextmanager
    def container(self):
        st.markdown(
            f"""
            <style>
            div[data-modal-container='true'][key='{self.key}'] {{
                position: fixed; 
                width: 100vw !important;
                height: 100vh !important;
                left: 0;
                z-index: 999992;
            }}

            div[data-modal-container='true'][key='{self.key}'] > div:first-child {{
                margin: auto;
            }}

            div[data-modal-container='true'][key='{self.key}'] h1 a {{
                display: none
            }}

            div[data-modal-container='true'][key='{self.key}']::before {{
                    position: fixed;
                    content: ' ';
                    left: 0;
                    right: 0;
                    top: 0;
                    bottom: 0;
                    z-index: 1000;
                    background-color: rgba(50,50,50,0.8);
            }}
            div[data-modal-container='true'][key='{self.key}'] > div:first-child {{
                max-width: {self.max_width};
                max-height: 800;
            }}

            div[data-modal-container='true'][key='{self.key}'] > div:first-child > div:first-child {{
                width: unset !important;
                background-color: #fff; /* Will be overridden if possible */
                padding: {self.padding}px;
                margin-top: {2*self.padding}px;
                margin-left: -{2*self.padding}px;
                margin-right: -{2*self.padding}px;
                margin-bottom: -{2*self.padding}px;
                z-index: 1001;
                border-radius: 5px;
            }}
            div[data-modal-container='true'][key='{self.key}'] > div:first-child > div:first-child > div:first-child  {{
                overflow-y: scroll;
                max-height: 80vh;
                overflow-x: hidden;
                max-width: {self.max_width};
            }}
            
            div[data-modal-container='true'][key='{self.key}'] > div > div:nth-child(2)  {{
                z-index: 1003;
                position: absolute;
            }}
            div[data-modal-container='true'][key='{self.key}'] > div > div:nth-child(2) > div {{
                text-align: right;
                padding-right: {self.padding}px;
                max-width: {self.max_width};
            }}

            div[data-modal-container='true'][key='{self.key}'] > div > div:nth-child(2) > div > button {{
                right: 0;
                margin-top: {2*self.padding + 14}px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        with st.container():
            _container = st.container()

            title, close_button = _container.columns([0.9, 0.05])
            if self.title:
                with title:
                    st.header(self.title)
            with close_button:
                close_ = st.button('X', key=f'{self.key}-close')
                if close_:
                    self.close()

            _container.divider()

        components.html(
            f"""
            <script>
            // STREAMLIT-MODAL-IFRAME-{self.key} <- Don't remove this comment. It's used to find our iframe
            const iframes = parent.document.body.getElementsByTagName('iframe');
            let container
            for(const iframe of iframes)
            {{
            if (iframe.srcdoc.indexOf("STREAMLIT-MODAL-IFRAME-{self.key}") !== -1) {{
                container = iframe.parentNode.previousSibling;
                container.setAttribute('data-modal-container', 'true');
                container.setAttribute('key', '{self.key}');
                
                // Copy background color from body
                const contentDiv = container.querySelector('div:first-child > div:first-child');
                contentDiv.style.backgroundColor = getComputedStyle(parent.document.body).backgroundColor;
            }}
            }}
            </script>
            """,
            height=0, width=0
        )

        with _container:
            yield _container
