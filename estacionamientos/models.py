# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import RegexValidator

# Validators

NAME_Validator = RegexValidator(
					regex = '^[a-zA-ZáéíóúñÑÁÉÍÓÚ ]+$',
					message = 'Sólo debe contener letras.'
					)

RIF_Validator = RegexValidator(
				regex = '^[JjVvDd]-?\d{8}-?\d$', 
				message = 'Introduzca un RIF con un formato válido.'
				)

IDDOC_Validator = RegexValidator(
					regex = '^[VvEe]-?\d{1,8}$',
					message = "Introduzca un número de cédula con formato válido."
					)

CREDITCARD_Validator = RegexValidator(
						regex = '^\d{16}$',
						message = 'Introduzca un número de tarjeta de crédito con un formato válido.'
						)

PHONE_Validator = RegexValidator(
					regex = '^((0?212)|(0?412)|(0?416)|(0?414)|(0?424)|(0?426))-?\d{7}',
					message = 'Debe introducir un formato válido.'					
					)

# Choices

SCHEME_Choices = [("1", "Por hora"),
					("2", "Por hora y fracción"),
					("3", "Por minuto"),
					("4", "Diferenciado por hora"),
					("5", "Diferenciado por fin de semana"),]

PROVCRED_Choices = [("Vista", "Vista"),
					("Mister", "Mister"),
					("Xpres", "Xpres")]


# Models

class Propietario(models.Model):
	NombreProp = models.CharField(max_length = 50, validators = [NAME_Validator], verbose_name="")
	
	Telefono_1 = models.CharField(blank = True, null = True, max_length = 30, validators = [PHONE_Validator], verbose_name="")
	Telefono_2 = models.CharField(blank = True, null = True, max_length = 30, validators = [PHONE_Validator], verbose_name="")
	Telefono_3 = models.CharField(blank = True, null = True, max_length = 30, validators = [PHONE_Validator], verbose_name="")

	Email_1 = models.EmailField(blank = True, null = True, verbose_name="")
	Email_2 = models.EmailField(blank = True, null = True, verbose_name="")

	Rif = models.CharField(max_length = 12, validators = [RIF_Validator], verbose_name="")

	def __str__(self):
		return "Propietario " + self.NombreProp + " | " + self.Rif
	


class Estacionamiento(models.Model):
	Propietario = models.ForeignKey(Propietario, editable = False)
	Nombre = models.CharField(max_length = 50, verbose_name="")
	Direccion = models.TextField(max_length = 120, verbose_name="")

	Apertura = models.TimeField(blank = True, null = True, verbose_name="")
	Cierre = models.TimeField(blank = True, null = True, verbose_name="")
	
	NroPuesto = models.PositiveIntegerField(blank = True, null = True, verbose_name="")

	def __str__(self):
		return "Estacionamiento " + self.Nombre



class EsquemaTarifario(models.Model):
	Estacionamiento = models.ForeignKey(Estacionamiento, primary_key = True, unique = True, editable = False)
	TipoEsquema = models.CharField(max_length=50, choices = SCHEME_Choices, verbose_name="Tipo de Esquema", null = True)
	Tarifa = models.DecimalField(max_digits=6, decimal_places=2, null = True, verbose_name="")
	
	def __str__(self):
		return "Esquema Tarifario tipo " + str(self.TipoEsquema) + " del estacionamiento " + str(self.Estacionamiento) + " | Tarifa: " + str(self.Tarifa)
	
	
	
class EsquemaDiferenciado(models.Model):
	EsquemaTarifario = models.ForeignKey(EsquemaTarifario, primary_key = True, unique = True, editable = False)
	HoraPicoInicio = models.TimeField(blank = True, null = True, verbose_name="")
	HoraPicoFin = models.TimeField(blank = True, null = True, verbose_name="")
	TarifaPico = models.DecimalField(max_digits=6, decimal_places=2, blank = True, null = True, verbose_name="")

	def __str__(self):
		return "Esquema Tarifario Diferenciado " + str(self.EsquemaTarifario) + " | Tarifa Pico: " + str(self.TarifaPico) 



class Reserva(models.Model):
	Estacionamiento = models.ForeignKey(Estacionamiento)
	Puesto = models.IntegerField(verbose_name="")
	FechaInicio = models.DateField(verbose_name="")
	HoraInicio = models.TimeField(verbose_name="")
	FechaFinal = models.DateField(verbose_name="")
	HoraFinal = models.TimeField(blank = True, null = True, verbose_name="")
	Pagada = models.NullBooleanField(blank = True, null = True)

	def __str__(self):
		return "Reserva del puesto " + str(self.Puesto) + " en " + self.Estacionamiento.Nombre + " de " + str(self.FechaInicio) + str(self.HoraInicio) + " a " + str(self.FechaFinal) + str(self.HoraFinal)



class Pago(models.Model):
	ID_Pago = models.ForeignKey(Reserva, primary_key=True, editable=False)
	NroTarjeta = models.CharField(max_length=16, null = True, validators=[CREDITCARD_Validator], verbose_name="")
	NombreTitular = models.CharField(max_length=50, null = True, validators=[NAME_Validator], verbose_name="")
	CedulaTitular = models.CharField(max_length=10, null = True, validators=[IDDOC_Validator], verbose_name="")
	ProveedorCred = models.CharField(max_length=10, null = True, choices=PROVCRED_Choices, verbose_name="Proveedor de Crédito")
	Monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="", null = True)
	
	def __str__(self):
		return "Pago de la " + str(self.ID_Pago)
