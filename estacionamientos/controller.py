# -*- coding: utf-8 -*-
# Archivo con funciones de control para SAGE

import datetime
from decimal import Decimal


class Esquema:
	
	def __init__(self, tarifa):
		self.tarifa = Decimal(tarifa)

	def _calcularEstadia(self, hora_entrada, hora_salida):
		estadia = hora_salida - hora_entrada
		horas_completas = (estadia.days*24) + (estadia.seconds // 3600)
		fraccion_hora = int(int(estadia.seconds%3600)/60) 
		return (horas_completas, fraccion_hora)

	def _costoHorasCompletas(self, horas):
		return Decimal(horas) * Decimal(self.tarifa)

	def _costoFraccionHora(self, fraccion, tarifa):
		pass
	
	def calcularCosto(self, inicio_reserva, final_reserva):
		(horas_completas,fraccion_hora) = self._calcularEstadia(inicio_reserva, final_reserva)
		total = Decimal(self._costoHorasCompletas(horas_completas))
		total += Decimal(self._costoFraccionHora(fraccion_hora, self.tarifa))
		return total
	
	

class PorHora(Esquema):
	def _costoFraccionHora(self, fraccion, tarifa):
		if fraccion == 0: return 0
		return Decimal(tarifa)

	
class PorHoraFraccion(Esquema):
	def _costoFraccionHora(self, fraccion, tarifa):
		if fraccion == 0: return 0
		else :
			if fraccion < 30: return Decimal(tarifa) / Decimal(2)
			return Decimal(tarifa)



class PorMinuto(Esquema):
	def _costoFraccionHora(self, fraccion, tarifa):
		if fraccion == 0: return Decimal(0)
		return Decimal(fraccion) * (Decimal(tarifa) / Decimal(60))
	
	
	
class Diferenciado(Esquema):
	def __init__(self, tarifa, tarifaPico, horaPicoInicio, horaPicoFin):
		self.tarifa = tarifa
		self.tarifaPico = tarifaPico
		self.horaPicoInicio = horaPicoInicio
		self.horaPicoFin = horaPicoFin
	
	def _calcularEstadia(self, hora_entrada, hora_salida):
		# Este algoritmo calcula la estadia en minutos, tanto de las horas normales
		# como las horas pico, iterando por todos los minutos que dura la reserva
		estadia = hora_salida - hora_entrada
		mins_pico = 0
		minsini = 0
		
		# Recorre los minutos de la reserva hasta que consigue y los va sumando al contador de minutos
		while minsini in range((estadia).days*24*60 + (estadia).seconds//60):
			if (hora_entrada + datetime.timedelta(0,minsini*60)).time() == self.horaPicoInicio\
				or self.horaPicoInicio < (hora_entrada + datetime.timedelta(0,minsini*60)).time() < self.horaPicoFin:
				minsfin = 1
				# Cuando el minuto actual se encuentra entre el inicio y el final de una hora pico,
				# ambos incluidos, suma dichos minutos al contador de minutos pico
				while (hora_entrada + datetime.timedelta(0,minsini*60) + datetime.timedelta(0,minsfin*60)).time() <= self.horaPicoFin\
				 and (hora_entrada + datetime.timedelta(0,minsini*60) + datetime.timedelta(0,minsfin*60)) <= hora_salida:
					mins_pico += 1
					minsfin += 1
				minsini = minsini + minsfin
			minsini += 1
			
		horas_completas = ((estadia.days*24*60) + (estadia.seconds // 60) - mins_pico) // 60
		horas_pico = mins_pico // 60
		fraccion_pico = int(mins_pico % 60)
		fraccion_hora = ((estadia.seconds // 60) - (horas_pico*60 + fraccion_pico)) % 60
		
		return (horas_completas, horas_pico, fraccion_hora, fraccion_pico)
		
	def _costoHorasPicoCompletas(self, horas_pico):
		return Decimal(horas_pico) * self.tarifaPico
	
	def _costoFraccionHora(self, fraccion, tarifa):
		if fraccion == 0: return Decimal(0)
		return Decimal(fraccion) * (Decimal(tarifa) / Decimal(60))
	
	def calcularCosto(self, inicio_reserva, final_reserva):
		(horas_completas,horas_pico,fraccion_hora,fraccion_pico) = self._calcularEstadia(inicio_reserva, final_reserva)
		total = Decimal(self._costoHorasCompletas(horas_completas))
		total += Decimal(self._costoHorasPicoCompletas(horas_pico))
		total += Decimal(self._costoFraccionHora(fraccion_hora, self.tarifa))
		total += Decimal(self._costoFraccionHora(fraccion_pico, self.tarifaPico))
		return total
	
	
	
class FinSemana(Esquema):
	def __init__(self, tarifa, tarifaFDS):
		self.tarifa = tarifa
		self.tarifaFDS = tarifaFDS
		
	def _costoFraccionHora(self, fraccion, tarifa):
		if fraccion == 0: return 0
		else :
			if fraccion < 30: return Decimal(tarifa) / Decimal(2)
			return Decimal(tarifa)
		
	def calcularCosto(self, inicio_reserva, final_reserva):
		(horas_completas,fraccion_hora) = self._calcularEstadia(inicio_reserva, final_reserva)
		if inicio_reserva.weekday() == final_reserva.weekday() and inicio_reserva.day != final_reserva.day:
			total = Decimal(horas_completas*max(self.tarifa, self.tarifaFDS))
			total += Decimal(self._costoFraccionHora(fraccion_hora, max(self.tarifa, self.tarifaFDS)))
			return total
		elif inicio_reserva.weekday() > final_reserva.weekday() and ((inicio_reserva.weekday() in range(4) and final_reserva.weekday() in range(4)) or (inicio_reserva.weekday() in range(4,7) and final_reserva.weekday() in range(4,7))):
			total = Decimal(horas_completas*max(self.tarifa, self.tarifaFDS))
			total += Decimal(self._costoFraccionHora(fraccion_hora, max(self.tarifa, self.tarifaFDS)))
			return total
		else:
			if inicio_reserva.weekday() in range(4,7) and final_reserva.weekday() in range(4,7):
				total = Decimal(horas_completas*self.tarifaFDS)
				total += Decimal(self._costoFraccionHora(fraccion_hora, self.tarifaFDS))
			elif (inicio_reserva.weekday() in range(4) and final_reserva.weekday() in range(4,7)) or (inicio_reserva.weekday() in range(4,7) and final_reserva.weekday() in range(4)):
				total = Decimal(horas_completas*max(self.tarifa, self.tarifaFDS))
				total += Decimal(self._costoFraccionHora(fraccion_hora, max(self.tarifa, self.tarifaFDS)))
			else:
				total = Decimal(self._costoHorasCompletas(horas_completas))
				total += Decimal(self._costoFraccionHora(fraccion_hora, self.tarifa))
		return total
	
	

def calcularCostoReserva(esquema, diferenciado, inicio_reserva, final_reserva):
	# Esta funcion instacia la clase Esquema correspondiente segun el tipo
	# de esquema, y calcula y devuelve el costo de la reserva segun el caso
	total = 0
	if esquema.TipoEsquema == "1":
		tipoEsquema = PorHora(esquema.Tarifa)
		total = tipoEsquema.calcularCosto(inicio_reserva, final_reserva)
	elif esquema.TipoEsquema == "2":
		tipoEsquema = PorHoraFraccion(esquema.Tarifa)
		total = tipoEsquema.calcularCosto(inicio_reserva, final_reserva)
	elif esquema.TipoEsquema == "3":
		tipoEsquema = PorMinuto(esquema.Tarifa)
		total = tipoEsquema.calcularCosto(inicio_reserva, final_reserva)
	elif esquema.TipoEsquema == "4":
		tipoEsquema = Diferenciado(esquema.Tarifa, diferenciado.TarifaPico, diferenciado.HoraPicoInicio, diferenciado.HoraPicoFin)
		total = tipoEsquema.calcularCosto(inicio_reserva, final_reserva)
	elif esquema.TipoEsquema == "5":
		tipoEsquema = FinSemana(esquema.Tarifa, diferenciado.TarifaPico)
		total = tipoEsquema.calcularCosto(inicio_reserva, final_reserva)
	return total


def encontrarPuesto(sources, ini, fin, nropuestos):
	nodisp = []
	today = datetime.datetime.today()
	for elem in sources:
		if ((ini - today).days*10000+ini.hour*100+ini.minute) in range((elem[0] - today.date()).days*10000+elem[1].hour*100+elem[1].minute,
											(elem[2] - today.date()).days*10000+elem[3].hour*100+elem[3].minute+1)\
											or\
			((fin - today).days*10000+fin.hour*100+fin.minute) in range((elem[0] - today.date()).days*10000+elem[1].hour*100+elem[1].minute,
																	(elem[2] - today.date()).days*10000+elem[3].hour*100+elem[3].minute+1):
			nodisp.append(elem[4])
	for i in range(nropuestos):
		if not i in nodisp:
			return i
	return -1


def ordenar(tabla):
	def obtenerClave(item):
		return item[0],item[1]
	
	return sorted(tabla, key = obtenerClave)


def ordernarPorFechaHora(reservas):
	def obtenerClave(item):
		return item.FechaInicio,item.HoraInicio
	
	return sorted(reservas, key = obtenerClave)


def solapamientoEnRangoReserva(inicio_reserva,fin_reserva,inicio,fin):
	reserva_range = range(inicio_reserva,fin_reserva)
	solapamiento_range = range(inicio,fin)
	reserva_set = set(reserva_range)
	solapamiento_set = set(solapamiento_range)
	return bool(reserva_set.intersection(solapamiento_set))


def viabilidadReservacion(tabla, inicio, final):
	# Devuelve True si un solapamiento se encuentra dentro del rango de una reservacion
	# False en caso contrario
	tipo = 0
	offset = 1
	best = 0
	cnt = 0
	beststart = 0
	bestend = 0
	today = datetime.datetime.today()
	for i in range(0,len(tabla)):
		cnt = cnt - tabla[i][offset]
		if (cnt > best) and (tabla[i][tipo] != tabla[i+1][tipo]) :
			best = cnt
			beststart = tabla[i][tipo]
			bestend = tabla[i+1][tipo]
		elif (cnt == best) and solapamientoEnRangoReserva(((inicio - today).days*10000+inicio.hour*100+inicio.minute),((final - today).days*10000+final.hour*100+final.minute),tabla[i][tipo],tabla[i+1][tipo]):
			best = cnt
			beststart = tabla[i][tipo]
			bestend = tabla[i+1][tipo]
	return best,beststart,bestend


def AceptarReservacion(inicio, final, capacidad, sources):
	tabla = []
	today = datetime.datetime.today()
	for elem in sources:
		diasIni = (elem[0] - today.date()).days
		diasFin = (elem[2] - today.date()).days
		tabla.append([diasIni*10000 + elem[1].hour*100 + elem[1].minute, -1])
		tabla.append([diasFin*10000 + elem[3].hour*100 + elem[3].minute, 1])

	tabla = ordenar(tabla)
	
	best,beststart,bestend = viabilidadReservacion(tabla, inicio, final)
	
	if best < capacidad: 
		return True
	elif best == capacidad:
		# Si el rango del solapamiento intersecta el de la reservacion, no se acepta esta ultima
		if solapamientoEnRangoReserva(((inicio.date() - today.date()).days*10000+inicio.hour*100+inicio.minute),((final.date() - today.date()).days*10000+final.hour*100+final.minute),beststart,bestend):
			return False
		else:
			return True
	return False


def tasaReservacion(sources, num_puestos):
	# Dada una lista 'sources' de todas las reservaciones de ese estacionamiento y su numero de puestos,
	# devuelve un arreglo con la tasa o porcentaja de ocupacion con granularidad fija Por Hora.
	today = datetime.datetime.today()
	tasa_reser = []
	
	# Crea una lista donde cada elemento es una lista que contiene la hora inicial y final en cada reserva.
	for elem in sources:
		diasIni = (elem[0] - today.date()).days
		diasFin = (elem[2] - today.date()).days
		tasa_reser.append([diasIni*10000 + elem[1].hour*100 + elem[1].minute, diasFin*10000 + elem[3].hour*100 + elem[3].minute])
	
	# Crea un arreglo de minutos en 7 dias desde el dia actual y suma 1 a la posicion especifica de cada
	# minuto por cada puesto ocupado que haya en el estacionamiento en ese minuto.
	reser_active_per_minute = [0]*(7*10000 + 24*100)
	for elem in tasa_reser:
		reser_set = set(range(elem[1])) - set(range(elem[0]))
		for time in reser_set:
			minute = time % 100
			if minute <= 59:
				hour = (time % 10000 - minute)
				day = (time - hour - minute)
				reser_active_per_minute[day + hour + minute] += 1
	
	# Crea un arreglo de horas el cual contiene la tasa o porcentaje de ocupacion por hora, calculado como
	# el promedio de puestos ocupados por minuto en esa hora, es decir,
	# ocupation_rate[hora] = 100 * (sum(puestos_ocupados_por_minuto)) / ((minutos_por_hora)*(num_puestos))
	occupation_rate = [0]*(7*24)
	for day in range(7):
		for hour in range(24):
			occupation_rate[day*24 + hour] = Decimal(100 * sum(reser_active_per_minute[(day*10000 + hour*100):(day*10000 + hour*100 + 60)]) / Decimal(60*num_puestos)).quantize(Decimal('.01'))
	
	return occupation_rate


def HorarioEstacionamiento(HoraInicio, HoraFin):
	if HoraInicio >= HoraFin:
		return (False, 'El horario de apertura debe ser menor al horario de cierre')
	return (True, '')


def validarHorarioReserva(ReservaInicio, ReservaFin, HorarioApertura, HorarioCierre):
	today = datetime.datetime.today()
	nextweek = today + datetime.timedelta(7)
	
	if ReservaInicio >= ReservaFin:
		return (False, 'La hora de inicio de la reserva debe ser menor a la hora de fin')
	if ReservaFin - ReservaInicio < datetime.timedelta(0, 900):
		return (False, 'El tiempo de la reserva debe ser al menos de 15 minutos')
	if ReservaInicio.date() < today.date():
		return (False, 'La fecha de inicio de la reserva no puede ser anterior al día actual')
	if ReservaFin.date() > nextweek.date():
		return (False, 'La fecha de fin de la reserva no puede ser posterior a los próximos 7 días')
	if ReservaFin.time() > HorarioCierre:
		return (False, 'El horario de fin de la reserva debe estar en un horario válido')
	if ReservaInicio.time() < HorarioApertura:
		return (False, 'El horario de inicio de la reserva debe estar en un horario válido')
	
	if HorarioApertura <= HorarioCierre: dia = 1
	else: dia = 2
	hora1 = datetime.datetime(1,1,1,HorarioApertura.hour,HorarioApertura.minute)
	hora2 = datetime.datetime(1,1,dia,HorarioCierre.hour,HorarioCierre.minute) + datetime.timedelta(0,60)
	tiempoFuncionamiento = (hora2 - hora1)
	if tiempoFuncionamiento.days == 1 and tiempoFuncionamiento.seconds == 0: # Funciona las 24 horas
		if ReservaFin - ReservaInicio > datetime.timedelta(7):
			return (False, 'El tiempo de la reserva en un estacionamiento abierto las 24 horas debe ser a lo sumo de 7 días')
	else:
		if ReservaFin.date() != ReservaInicio.date():
			return (False, 'El tiempo de la reserva está fuera del horario de funcionamiento del estacionamiento')
	
	return (True, '')
