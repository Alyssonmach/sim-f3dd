# FRAME3DD: 
# Static and dynamic structural analysis of 2D & 3D frames and trusses
# with elastic and geometric stiffness.
# ---------------------------------------------------------------------------
# http://frame3dd.sourceforge.net/
# ---------------------------------------------------------------------------
# Copyright (C) 1992-2009  Henri P. Gavin
#
#    FRAME3DD is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    FRAME3DD is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FRAME3DD.  If not, see <http://www.gnu.org/licenses/>.
##  
#  @file
#            a simple Makefile for Frame3DD
## 

# Definição de variáveis
SHELL = /bin/sh
CC = gcc
CFLAGS = -c -O 
LDFLAGS = -lm

# Pasta de saída
OUTDIR = out

# Lista de arquivos-fonte
SOURCES = main.c frame3dd.c frame3dd_io.c coordtrans.c eig.c HPGmatrix.c HPGutil.c NRutil.c 

# Gera os arquivos objeto na pasta out/
OBJECTS = $(patsubst %.c, $(OUTDIR)/%.o, $(SOURCES))

# Nome do executável dentro da pasta out/
EXECUTABLE = $(OUTDIR)/frame3dd

# Regra principal
all: $(OUTDIR) $(EXECUTABLE)

# Criação da pasta out/
$(OUTDIR):
	mkdir -p $(OUTDIR)

# Linkagem final para criar o executável
$(EXECUTABLE): $(OBJECTS)
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@

# Regra para compilar arquivos .c em .o dentro de out/
$(OUTDIR)/%.o: %.c | $(OUTDIR)
	$(CC) $(CFLAGS) $< -o $@

# Limpa os arquivos compilados
clean:
	rm -rf $(OUTDIR)

# Instala o executável
install: all
	mv $(EXECUTABLE) /usr/local/bin/.



