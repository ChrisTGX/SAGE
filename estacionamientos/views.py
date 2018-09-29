# -*- coding: utf-8 -*-

import locale
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http.response import HttpResponse
from reportlab.pdfgen import canvas

from estacionamientos.controller import *
from estacionamientos.forms import *
from estacionamientos.models import *

listaReserva = []
context_global = {}


def estacionamientos_all(request):
    # Usamos esta vista para procesar todos los estacionamientos
    global listaReserva
    listaReserva = []
    # Si se hace un POST a esta vista implica que se quiere agregar un nuevo
    # estacionamiento
    estacionamientos = Estacionamiento.objects.all()
    
    if request.method == 'POST':
            # Creamos un formulario con los datos que recibimos
            formProp = PropietarioForm(request.POST)
            formEst = EstacionamientoForm(request.POST)

            # Parte de la entrega era limitar la cantidad maxima de
            # estacionamientos a 5
            if len(estacionamientos) >= 5:
                    return render(request, 'templateMensaje.html',
                                  {'color':'red', 'mensaje':'No se pueden agregar más estacionamientos', 'url': '.'})

            # Si el formulario es valido, entonces creamos un objeto con
            # el constructor del modelo
            if formProp.is_valid() and formEst.is_valid():
                try:
                    prop = Propietario.objects.get(Rif = formProp.cleaned_data['Rif'])
                    if not prop:
                        prop = Propietario(
                            NombreProp = formProp.cleaned_data['NombreProp'],
                            Rif = formProp.cleaned_data['Rif'],
                            Telefono_1 = formProp.cleaned_data['Telefono_1'],
                            Telefono_2 = formProp.cleaned_data['Telefono_2'],
                            Telefono_3 = formProp.cleaned_data['Telefono_3'],
                            Email_1 = formProp.cleaned_data['Email_1'],
                            Email_2 = formProp.cleaned_data['Email_2'],
                        )
                    elif prop.NombreProp == formProp.cleaned_data['NombreProp']:
                        prop.Telefono_1 = formProp.cleaned_data['Telefono_1']
                        prop.Telefono_2 = formProp.cleaned_data['Telefono_2']
                        prop.Telefono_3 = formProp.cleaned_data['Telefono_3']
                        prop.Email_1 = formProp.cleaned_data['Email_1']
                        prop.Email_2 = formProp.cleaned_data['Email_2']
                    elif prop.NombreProp != formProp.cleaned_data['NombreProp']:
                        request.method = 'GET'
                        return render(request, 'templateMensaje.html', 
                                      {'mensaje': 'El propietario ya existe y no coincide el nombre introducido con su RIF.',
                                       'color': 'red',
                                       'url': '.'})
                        
                    prop.save()
                    
                    obj = Estacionamiento.objects.filter(Nombre = formEst.cleaned_data['Nombre'])
                    
                except ObjectDoesNotExist:
                    obj = Estacionamiento.objects.filter(Nombre = formEst.cleaned_data['Nombre'])
                    if not obj:
                        prop = Propietario(
                                NombreProp = formProp.cleaned_data['NombreProp'],
                                Rif = formProp.cleaned_data['Rif'],
                                Telefono_1 = formProp.cleaned_data['Telefono_1'],
                                Telefono_2 = formProp.cleaned_data['Telefono_2'],
                                Telefono_3 = formProp.cleaned_data['Telefono_3'],
                                Email_1 = formProp.cleaned_data['Email_1'],
                                Email_2 = formProp.cleaned_data['Email_2'],
                            )
                        
                        prop.save()
                    else:
                        return render(request, 'templateMensaje.html', 
                                  {'mensaje': 'Ya existe un estacionamiento con ese nombre.',
                                   'color': 'red',
                                   'url': '.'})
                
                prop = Propietario.objects.get(Rif = formProp.cleaned_data['Rif'])
                
                if not obj:
                    obj = Estacionamiento(
                        Propietario = prop,
                        Nombre = formEst.cleaned_data['Nombre'],
                        Direccion = formEst.cleaned_data['Direccion'],
                    )       
                             
                    obj.save()
                    
                    objEsquem = EsquemaTarifario(
                            Estacionamiento = obj
                    )
                    objEsquem.save()
                else:                 
                    return render(request, 'templateMensaje.html', 
                                  {'mensaje': 'Ya existe un estacionamiento con ese nombre.',
                                   'color': 'red',
                                   'url': '.'})
                
                # Recargamos los estacionamientos ya que acabamos de agregar
                estacionamientos = Estacionamiento.objects.all()
                formProp = PropietarioForm()
                formEst = EstacionamientoForm()
    # Si no es un POST es un GET, y mandamos un formulario vacio
    else:
        formProp = PropietarioForm()
        formEst = EstacionamientoForm()

    return render(request, 'base.html', {'formProp': formProp, 'formEst': formEst, 'estacionamientos': estacionamientos})



def estacionamiento_detail(request, _id):
    _id = int(_id)
    # Verificamos que el objeto exista antes de continuar
    try:
        estacion = Estacionamiento.objects.get(id = _id)
        esquema = EsquemaTarifario.objects.get(Estacionamiento = estacion)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    
    diferenciado = None
    
    global listaReserva
    listaReserva = []
    
    if request.method == 'GET':
        fields_initialParam = {'NroPuesto': estacion.NroPuesto}
        if estacion.Apertura: fields_initialParam['Apertura'] = estacion.Apertura.strftime('%H:%M')
        if estacion.Cierre: fields_initialParam['Cierre'] = estacion.Cierre.strftime('%H:%M')
            
        formParam = EstacionamientoExtendedForm(initial = fields_initialParam)

        formEsquem = EsquemaTarifarioForm(instance = esquema)
        
        if esquema.TipoEsquema == "4" or esquema.TipoEsquema == "5":
            diferenciado = EsquemaDiferenciado.objects.get(EsquemaTarifario = esquema)
            
            fields_initialDifer = {'TarifaPico': diferenciado.TarifaPico}
            if diferenciado.HoraPicoInicio: fields_initialDifer['HoraPicoInicio'] = diferenciado.HoraPicoInicio.strftime('%H:%M')
            if diferenciado.HoraPicoFin: fields_initialDifer['HoraPicoFin'] = diferenciado.HoraPicoFin.strftime('%H:%M')
            
            if esquema.TipoEsquema == "4": formDifer = EsquemaDiferenciadoForm(initial = fields_initialDifer)
            if esquema.TipoEsquema == "5": formDifer = EsquemaDiferenciadoFdsForm(initial = fields_initialDifer)
        else:
            diferenciado = None
            formDifer = None
        
    elif request.method == 'POST':
        # Leemos los formularios
        formParam = EstacionamientoExtendedForm(request.POST)
        formEsquem = EsquemaTarifarioForm(request.POST)
        if esquema.TipoEsquema == "4" or esquema.TipoEsquema == "5":
            diferenciado = EsquemaDiferenciado.objects.get(EsquemaTarifario = esquema)
            if esquema.TipoEsquema == "4": formDifer = EsquemaDiferenciadoForm(request.POST)
            if esquema.TipoEsquema == "5": formDifer = EsquemaDiferenciadoFdsForm(request.POST)
        else:
            diferenciado = None
            formDifer = None
            
        # Determina si los 3 formularios son validos
        if formParam.is_valid() and formEsquem.is_valid() and (len(formParam.changed_data) > 0 or len(formEsquem.changed_data) > 0):
            if not formDifer or formDifer.is_valid():
                if ('Apertura' in formParam.changed_data and 
                    'Cierre' in formParam.changed_data):
                    
                    hora_in = formParam.cleaned_data['Apertura']
                    hora_out = formParam.cleaned_data['Cierre']
                    
                    estacion.Apertura = hora_in
                    estacion.Cierre = hora_out
                    
                    m_validado = HorarioEstacionamiento(hora_in, hora_out)
                    if not m_validado[0]:
                        return render(request, 'templateMensaje.html', {'color':'red', 'mensaje': m_validado[1], 'url': './'})
                
                elif ('Apertura' in formParam.changed_data or 
                    'Cierre' in formParam.changed_data):
                    return render(request, 'templateMensaje.html', 
                                  {'color':'red', 
                                   'mensaje': 'Deben especificarse juntos los horarios de Apertura y Cierre.',
                                   'url': './'})
                
                if 'NroPuesto' in formParam.changed_data: estacion.NroPuesto = formParam.cleaned_data['NroPuesto']
                                
                estacion.save()
                
                estacion = Estacionamiento.objects.get(id = _id)

                esquema.TipoEsquema = formEsquem.cleaned_data['TipoEsquema']  
                esquema.Tarifa = formEsquem.cleaned_data['Tarifa']
                               
                esquema.save()
                
                if formEsquem.cleaned_data['TipoEsquema'] == "4" or formEsquem.cleaned_data['TipoEsquema'] == "5":
                    esquema = EsquemaTarifario.objects.get(Estacionamiento = estacion)
                    
                    if diferenciado:
                        if formEsquem.cleaned_data['TipoEsquema'] == "4":
                            if 'HoraPicoInicio' in formDifer.cleaned_data:
                                diferenciado.HoraPicoInicio = formDifer.cleaned_data['HoraPicoInicio']
                            if 'HoraPicoFin' in formDifer.cleaned_data:
                                diferenciado.HoraPicoFin = formDifer.cleaned_data['HoraPicoFin']
                        if formEsquem.cleaned_data['TipoEsquema'] == "5":
                            diferenciado.HoraPicoInicio = datetime.time(0,0)
                            diferenciado.HoraPicoFin = datetime.time(0,0)
                        diferenciado.TarifaPico = formDifer.cleaned_data['TarifaPico']
                    else:
                        diferenciado = EsquemaDiferenciado(
                                        EsquemaTarifario = esquema
                                        )
                    diferenciado.save()
                    
                    diferenciado = EsquemaDiferenciado.objects.get(EsquemaTarifario = esquema)
                    fields_initialDifer = {'TarifaPico': diferenciado.TarifaPico}
                    if diferenciado.HoraPicoInicio: fields_initialDifer['HoraPicoInicio'] = diferenciado.HoraPicoInicio.strftime('%H:%M')
                    if diferenciado.HoraPicoFin: fields_initialDifer['HoraPicoFin'] = diferenciado.HoraPicoFin.strftime('%H:%M')
                    
                    if formEsquem.cleaned_data['TipoEsquema'] == "4": formDifer = EsquemaDiferenciadoForm(initial = fields_initialDifer)
                    if formEsquem.cleaned_data['TipoEsquema'] == "5": formDifer = EsquemaDiferenciadoFdsForm(initial = fields_initialDifer)
                else:
                    if diferenciado: diferenciado.delete()
                    formDifer = None
                        
    else:
        formParam = EstacionamientoExtendedForm()
        formEsquem = EsquemaTarifarioForm()
        formDifer = EsquemaDiferenciadoForm()
        
    return render(request, 'estacionamiento.html', 
                  {'formParam': formParam, 'formEsquem': formEsquem, 'formDifer': formDifer, 
                   'estacionamiento': estacion, 'esquema': esquema, 'diferenciado': diferenciado})



def estacionamiento_reserva(request, _id):
    _id = int(_id)
    # Verificamos que el objeto exista antes de continuar
    try:
        estacion = Estacionamiento.objects.get(id = _id)
        esquema = EsquemaTarifario.objects.get(Estacionamiento = estacion)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    
    if esquema.TipoEsquema == "4" or esquema.TipoEsquema == "5":
        diferenciado = EsquemaDiferenciado.objects.get(EsquemaTarifario = esquema)
    else:
        diferenciado = None
    
    global listaReserva

    # Si se hace un GET renderizamos los estacionamientos con su formulario
    if request.method == 'GET':
        form = EstacionamientoReservaForm()
        return render(request, 
                      'estacionamientoReserva.html',
                      {'form': form, 
                       'estacionamiento': estacion, 'esquema': esquema, 'diferenciado': diferenciado})

    # Si es un POST estan mandando un request
    elif request.method == 'POST':
        form = EstacionamientoReservaForm(request.POST)
        # Verificamos si es valido con los validadores del formulario
        if form.is_valid():
            # Inicio Reserva
            year = form.cleaned_data['FechaInicio'].year
            month = form.cleaned_data['FechaInicio'].month
            day = form.cleaned_data['FechaInicio'].day
            hour = form.cleaned_data['HoraInicio'].hour
            minute = form.cleaned_data['HoraInicio'].minute
            
            inicio_reserva = datetime.datetime(year, month, day, hour, minute)
            
            # Fin Reserva
            year = form.cleaned_data['FechaFinal'].year
            month = form.cleaned_data['FechaFinal'].month
            day = form.cleaned_data['FechaFinal'].day
            hour = form.cleaned_data['HoraFinal'].hour
            minute = form.cleaned_data['HoraFinal'].minute
            
            final_reserva = datetime.datetime(year, month, day, hour, minute)
            
            # Validamos los horarios con los horario de salida y entrada
            m_validado = validarHorarioReserva(inicio_reserva, final_reserva, estacion.Apertura, estacion.Cierre)

            # Si no es valido devolvemos el request
            if not m_validado[0]:
                return render(request, 'templateMensaje.html', {'color':'red', 'mensaje': m_validado[1], 'url': './reserva'})

            # Si esta en un rango valido, procedemos a buscar en la lista
            # el lugar a insertar
            sources = Reserva.objects.filter(Estacionamiento = estacion).values_list('FechaInicio', 'HoraInicio','FechaFinal', 'HoraFinal','Puesto')
            
            if AceptarReservacion(inicio_reserva, final_reserva, estacion.NroPuesto, sources):
                reservaFinal = Reserva(
                                    Estacionamiento = estacion,
                                    Puesto = encontrarPuesto(sources, inicio_reserva, final_reserva, estacion.NroPuesto),
                                    FechaInicio = datetime.date(inicio_reserva.year, inicio_reserva.month, inicio_reserva.day),
                                    HoraInicio = datetime.time(inicio_reserva.hour, inicio_reserva.minute),
                                    FechaFinal = datetime.date(final_reserva.year, final_reserva.month, final_reserva.day),
                                    HoraFinal = datetime.time(final_reserva.hour, final_reserva.minute),
                                    Pagada = False
                                )
                
                # Llama a la funcion del controller que escoge la estrategia a utilizar para el calculo
                total = calcularCostoReserva(esquema, diferenciado, inicio_reserva, final_reserva)
                 
                request.method = 'GET'
                return pagar_reserva(request, 
                              context = {'total':total,
                                         'reserva_object':reservaFinal})

            else:
                return render(request, 
                              'templateMensaje.html', 
                              {'color':'red', 
                               'mensaje':'No hay un puesto disponible para ese horario',
                               'url': './reserva'})
    else:
        form = EstacionamientoReservaForm()

    return render(request, 
                  'estacionamientoReserva.html', 
                  {'form': form, 
                   'estacionamiento': estacion, 'esquema': esquema, 'diferenciado': diferenciado})



def pagar_reserva(request, context = None):
    global context_global
    # Si tenemos un GET -> acbamos de llegar desde estacionamiento_reserva
    if request.method == 'GET':
        context_global = context
        context['form'] = PagarReservaForm()
        context['color'] = 'green'
        context['mensaje'] = 'El monto de la reserva es: %.2f' % context['total']
        return render(request, 'pagarReserva.html', context)

    # Si tenemos un POST -> el usuario esta decidiendo que quiere pagar la reserva
    elif request.method == 'POST':
        context = context_global
        form = PagarReservaForm(request.POST)
        if form.is_valid():
            context['reserva_object'].Pagada = True
            context['reserva_object'].save()
            context['form'] = form
            pago = Pago(
                    ID_Pago = context['reserva_object'],
                    NroTarjeta = form.cleaned_data['NroTarjeta'],
                    ProveedorCred = form.cleaned_data['ProveedorCred'],
                    CedulaTitular = form.cleaned_data['CedulaTitular'],
                    NombreTitular = form.cleaned_data['NombreTitular'],
                    Monto = context['total']
            )
            pago.save()
            
            context_global['pago'] = pago
            context['color'] = 'green'
            context['mensaje'] = 'Reserva pagada satisfactoriamente. Su codigo de pago es %i' % context['reserva_object'].id
            context['reserva_object'].save()
            return render(request, 'templateMensaje.html', context)
        else:
            return render(request,
                          'pagarReserva.html',
                          {'form':form})



def tasa_reservacion(request, _id):
    _id = int(_id)
    
    try:
        estacion = Estacionamiento.objects.get(id = _id)
        esquema = EsquemaTarifario.objects.get(Estacionamiento = estacion)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    
    if request.method == 'GET':
        
        # Si aun no se ha parametrizado el estacionamiento, asignamos un NroPuesto arbitrariamente
        # Este no se guardara
        if not estacion.NroPuesto:
            estacion.NroPuesto = 1
        
        today = datetime.datetime.today()
        
        # Obtiene la lista de todas las reservaciones de ese estacionamiento y llama a tasaReservacion
        sources = Reserva.objects.filter(Estacionamiento = estacion).filter(FechaInicio__range = [today.date(), today.date() + datetime.timedelta(7)]).values_list('FechaInicio', 'HoraInicio','FechaFinal', 'HoraFinal','Puesto')
        print("AQUI", len(sources))
        ocupacion = tasaReservacion(sources, estacion.NroPuesto)
        
        
        class TempOcup:
            def __init__(self, Id, horas, dia):
                self.Id = Id
                self.horas = horas
                self.dia = dia
        
        
#         locale.setlocale(locale.LC_ALL, 'es_VE.UTF-8')
        template_ocupacion = []
        for dia in range(7):
            ocupActual = TempOcup(dia, ocupacion[(dia*24):(dia*24 + 24)], (today + datetime.timedelta(dia)).date().strftime('%a %d/%m').capitalize())
            template_ocupacion.append(ocupActual)
            
        
        return render(request,
                      'tasaReservacion.html',
                      {'estacionamiento': estacion, 'esquema': esquema, 'ocupacion': template_ocupacion})
        


def login(request, template):
    # Determina el tipo de usuario dado el url accedido
    if template == "ingresos": 
        user = "owner"
        url_form = "./ingresos"
    elif template == "reservaciones": 
        user = "client"
        url_form = "./reservaciones"
    
    invalid_ID = False
    info_user = None
    estacionamientos = None
    
    
    class Ingreso:
        def __init__(self, estacionamiento, ingresos):
            self.estacionamiento = estacionamiento
            self.ingresos = ingresos
    
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            if user == "owner":
                # Si el usuario es 'owner' entonces se estan solicitando los ingresos por estacionamiento.
                try:
                    # Se consulta en la base de datos todos los estacionamientos asociados al propietario
                    # con el RIF dado y luego se suma el monto total de todas las reservaciones asociadas
                    # a cada uno de los estacionamientos.
                    prop = Propietario.objects.get(Rif = form.cleaned_data['ID_Usuario'])
                    info_user = prop
                    estIngresos = []
                    estacionamientos = Estacionamiento.objects.filter(Propietario = prop)
                    totalFinal = Decimal(0)
                    for estacion in estacionamientos:
                        reservas = Reserva.objects.filter(Estacionamiento = estacion)
                        totalIngresos = Decimal(0)
                        if reservas:
                            for reser in reservas:
                                pago = Pago.objects.get(ID_Pago = reser)
                                totalIngresos += Decimal(pago.Monto)
                        totalIngresos = Decimal(totalIngresos).quantize(Decimal('.01'))
                        totalFinal += totalIngresos
                        ing = Ingreso(estacion.Nombre, totalIngresos)
                        estIngresos.append(ing)
                        
                except ObjectDoesNotExist:
                    invalid_ID = True
                
                
            else:
                # Si el usuario es 'client' entonces se estan solicitando las reservaciones del cliente.
                # Se consulta en la base de datos los datos de las reservaciones asociadas a cada uno de
                # los pagos realizados por el cliente con la Cedula dada.
                pagos = Pago.objects.filter(CedulaTitular = form.cleaned_data['ID_Usuario'])
                if not pagos:
                    invalid_ID = True
                else:
                    reservas = []
                    for pago in pagos:
                        reserva = pago.ID_Pago
                        reservas.append(reserva)
                        info_user = pago
                        
                    reservas = ordernarPorFechaHora(reservas)
                    
            if not invalid_ID:
                request.method = "GET"
                if user == "owner": return render(request, 'ingresos.html', {'user': user, 'info_user': info_user, 'estIngresos': estIngresos, 'totalFinal': totalFinal})
                else: return render(request, 'misReservaciones.html', {'user': user, 'info_user': info_user, 'reservas': reservas})
            
    else:
        form = LoginForm()
    
    return render(request, 'templateLogin.html', 
                  {'user': user, 'form': form, 'url_form': url_form, 'invalid_ID': invalid_ID})



def print_report(request):
    # Vista para imprimir los recibos de pago (model Pago)
    def draw_marquee(x, y):
        p.drawString(x-20, y, '_'*78)
        p.drawString(x-20, y-330, '_'*78)
        for i in range(318):
            p.drawString(x-20, y-i-11, '|')
            p.drawString(x+500, y-i-11, '|')
                       
                       
    global context_global
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ReportePago' + \
                        str(context_global['pago'].ID_Pago.id) + '.pdf"'
    p = canvas.Canvas(response)
    y = 800
    x = 100
    draw_marquee(70, 820)
    p.drawString(x, y, 'Sistema Automatizado de Gestión de Estacionamientos (SAGE)')
    y = y - 30
    p.drawString(x, y, 'Estacionamiento ' +
                 context_global['pago'].ID_Pago.Estacionamiento.Nombre)
    y = y - 30
    p.drawString(x, y, 'Inicio de la reserva:  ' +
                 str(context_global['pago'].ID_Pago.FechaInicio) +
                 ', a las ' + str(context_global['pago'].ID_Pago.HoraInicio))
    y = y - 30
    p.drawString(x, y, 'Final de la reserva:  ' +
                 str(context_global['pago'].ID_Pago.FechaFinal) +
                 ', a las ' + str(context_global['pago'].ID_Pago.HoraFinal))
    y = y - 30
    p.drawString(x, y, 'Identificador único de pago: ' + 
                 str(context_global['pago'].ID_Pago.id))
    y = y - 30
    p.drawString(x, y, 'Nombre del tarjetahabiente: ' + 
                 str(context_global['pago'].NombreTitular))
    y = y - 30
    p.drawString(x, y, 'Número de Cédula: ' + 
                 str(context_global['pago'].CedulaTitular))
    y = y - 30
    p.drawString(x, y, 'Total pagado: BsF. ' + 
                 str(context_global['pago'].Monto.quantize(Decimal('0.01'))))
    y = y - 30
    p.drawString(x, y, 'Proveedor de crédito: ' + 
                 str(context_global['pago'].ProveedorCred))
    y = y - 30
    p.drawString(x, y, 'Número de tarjeta de crédito: ' + 
                 '*'*(len(context_global['pago'].NroTarjeta)-4) +
                  str(context_global['pago'].NroTarjeta[12:]))
    y = y - 30
    p.drawString(x, y,datetime.datetime.now().strftime('Fecha del pago: %d/%m/%Y, a las %H:%M:%S'))
    y = y - 30
    p.showPage()
    p.save()
    return response
    pass
