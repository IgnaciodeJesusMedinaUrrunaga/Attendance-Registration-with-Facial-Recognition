import os
import datetime
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# pip install mysql-connector-python
# pip install reportlab

def get_data_from_mysql():
    # Conectarse a la base de datos MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="asistencia_del_cia"
    )
    cursor = connection.cursor()

    # Obtener todos los datos de la tabla "registro" ordenados por fecha
    query = "SELECT id, fecha, nombre, hora FROM registro ORDER BY fecha"
    cursor.execute(query)
    data = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    connection.close()

    # Organizar los datos por fecha
    organized_data = {}
    for row in data:
        date = row[1]
        if date not in organized_data:
            organized_data[date] = []
        organized_data[date].append(row)

    return organized_data


def create_pdf(organized_data):
    # Crear el archivo PDF con el nombre "lista_asistencia_historial.pdf"
    filename = "lista_asistencia_historial.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    for date, data in organized_data.items():
        # Agregar el título de la fecha en la parte superior del documento como un objeto 'Flowable'
        title = f"Lista de asistencia del día ({date})"
        title_style = styles['Title']
        title_paragraph = Paragraph(title, title_style)
        elements.append(title_paragraph)

        # Convertir los datos de esa fecha en una lista para la tabla
        data_table = [['ID', 'Fecha', 'Nombre', 'Hora']] + data

        # Crear la tabla para esa fecha
        table = Table(data_table)

        # Estilo de la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND',(0,1),(-1,-1),colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        table.setStyle(style)

        # Agregar la tabla al documento
        elements.append(table)

        # Agregar un espacio después de la tabla
        elements.append(Spacer(1, 12))

    # Construir el documento
    doc.build(elements)

if __name__ == "__main__":
    # Obtener los datos organizados por fecha de MySQL
    organized_data = get_data_from_mysql()

    # Crear el PDF con los datos de la tabla organizados por fecha
    create_pdf(organized_data)
