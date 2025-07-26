# ==========================================
#  GENERACIÓN DE PDF PARA OTM - SISTEMA BIOMÉDICO
#  Utiliza reportlab para crear PDFs con los datos de la OTM
# ==========================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO

def draw_labeled_box(c, x, y, label, text, width=8*cm, height=1*cm):
    """
    Dibuja una caja con borde, etiqueta y valor en el PDF.
    :param c: Canvas de reportlab
    :param x: Posición X inicial
    :param y: Posición Y inicial
    :param label: Etiqueta del campo
    :param text: Valor del campo
    :param width: Ancho de la caja
    :param height: Alto de la caja
    """
    c.setStrokeColor(colors.black)
    c.rect(x, y - height, width, height, fill=0)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2, y - 10, label)
    c.setFont("Helvetica", 8)
    c.drawString(x + 2, y - 22, str(text))

def generar_pdf_otm_completo_formato(otm):
    """
    Genera un PDF con el formato completo de una OTM (dos páginas).
    :param otm: Diccionario con los datos de la OTM
    :return: Buffer BytesIO listo para enviar como archivo PDF
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # -------- Página 1 - Formulario 1 --------
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 40, "ORDEN DE TRABAJO DE MANTENIMIENTO")

    # Lista de campos a mostrar en la primera página
    campos_form1 = [
        ('Área Usuaria', 'area'), ('Dependencia', 'dependencia'),
        ('Número de OTM', 'numero'), ('Fecha', 'fecha'),
        ('Ubicación', 'ubicacion'), ('Denominación del equipo', 'denominacion'),
        ('Marca', 'marca'), ('Modelo', 'modelo'),
        ('Serie', 'serie'), ('Código Patrimonial', 'codigo_patrimonial'),
        ('Problema Reportado', 'problema'),
        ('Fecha de Solicitud', 'fecha_solicitud'),
        ('Fecha de Recepción', 'fecha_recepcion'),
        ('Diagnóstico', 'diagnostico'), ('Encargado', 'encargado'),
        ('Fecha Mantenimiento', 'fecha_mantenimiento'),
        ('Trabajo Realizado', 'trabajo'),
        ('Fecha Inicio', 'fecha_inicio'), ('Fecha Término', 'fecha_termino'),
        ('Garantía', 'garantia'), ('Costo Estimado', 'costo'),
        ('Recomendaciones', 'recomendaciones'),
        ('Prioridad', 'prioridad'), ('Modalidad', 'modalidad'),
    ]

    # Posición inicial para los campos
    x = 2 * cm
    y = height - 60
    for label, key in campos_form1:
        value = otm.get(key, '')
        draw_labeled_box(c, x, y, label, value)
        y -= 1.5 * cm
        # Si se acaba el espacio vertical, pasa a la siguiente columna
        if y < 4 * cm:
            x += 9 * cm
            y = height - 60

    c.showPage()  # Nueva página

    # -------- Página 2 - Formulario 2 --------
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 40, "DETALLE DE COSTOS")

    # Lista de campos a mostrar en la segunda página
    campos_form2 = [
        ('Técnico Responsable', 'nombre_tecnico'), ('Especialidad', 'especialidad'),
        ('Horas Hombre', 'horas'), ('Valor por Hora', 'valor_hora'),
        ('Costo MO', 'costo_mo'), ('Origen Material', 'origen'),
        ('Descripción Material', 'descripcion_material'), ('Unidad Medida', 'um'),
        ('Cantidad', 'cantidad'), ('Costo Unitario', 'costo_unitario'),
        ('Costo Parcial', 'costo_parcial'), ('Total MO', 'total_mo'),
        ('Total Materiales', 'total_materiales'), ('Otros Gastos', 'otros_gastos'),
        ('Impuestos', 'impuestos'), ('Total General', 'total_general')
    ]

    # Posición inicial para los campos de la segunda página
    x = 2 * cm
    y = height - 60
    for label, key in campos_form2:
        value = otm.get(key, '')
        draw_labeled_box(c, x, y, label, value)
        y -= 1.5 * cm
        if y < 4 * cm:
            x += 9 * cm
            y = height - 60

    c.save()
    buffer.seek(0)
    return buffer