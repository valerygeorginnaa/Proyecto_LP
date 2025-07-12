import pandas as pd
import io
from openpyxl.utils import get_column_letter
from flask import send_file

def generar_excel_otm(otm_data):
    if not otm_data:
        return None, "No hay datos para descargar.", 400

    mapeo_columnas = {
        'dependencia': 'Dependencia',
        'numero': 'Numero',
        'fecha': 'Fecha',
        'area': 'Area',
        'ubicacion': 'Ubicacion',
        'denominacion': 'Denominacion',
        'marca': 'Marca',
        'modelo': 'Modelo',
        'serie': 'Serie',
        'codigo_patrimonial': 'Codigo patrimonial',
        'problema': 'Problema',
        'fecha_solicitud': 'Fecha solicitud',
        'fecha_recepcion': 'Fecha recepcion',
        'diagnostico': 'Diagnostico',
        'encargado': 'Encargado',
        'fecha_mantenimiento': 'Fecha mantenimiento',
        'trabajo': 'Trabajo',
        'fecha_inicio': 'Fecha inicio',
        'fecha_termino': 'Fecha termino',
        'garantia': 'Garantia',
        'costo': 'Costo',
        'recomendaciones': 'Recomendaciones',
        'prioridad': 'Prioridad',
        'modalidad': 'Modalidad',
        'nombre_tecnico': 'Nombre tecnico',
        'especialidad': 'Especialidad',
        'horas': 'Horas',
        'valor_hora': 'Valor hora',
        'costo_mo': 'Costo mo',
        'origen': 'Origen',
        'descripcion_material': 'Descripcion material',
        'um': 'Um',
        'cantidad': 'Cantidad',
        'costo_unitario': 'Costo unitario',
        'costo_parcial': 'Costo parcial',
        'total_mo': 'Total mo',
        'total_materiales': 'Total materiales',
        'otros_gastos': 'Otros gastos',
        'impuestos': 'Impuestos',
        'total_general': 'Total general'
    }

    datos_excel = []
    for otm in otm_data:
        fila = {}
        for clave, columna in mapeo_columnas.items():
            valor = otm.get(clave, '')
            if isinstance(valor, list):
                valor = ', '.join(valor)
            fila[columna] = valor
        datos_excel.append(fila)

    df = pd.DataFrame(datos_excel)
    df = df.reindex(columns=list(mapeo_columnas.values()))

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for i, col in enumerate(df.columns, 1):
            max_length = max([len(str(s)) for s in df[col].values] + [len(str(col))])
            worksheet.column_dimensions[get_column_letter(i)].width = max_length + 2

    output.seek(0)
    return output, None, 200