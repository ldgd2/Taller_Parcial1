import asyncio
import os
import sys
from sqlalchemy import select, func

# Añadir el path del backend para importar los modelos
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.database import AsyncSessionLocal
from app.models.pago import Pago
from app.models.emergencia import Emergencia
from app.models.taller import Taller
from app.models.estado import Estado

HAS_RICH = False
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

async def get_stats_async():
    async with AsyncSessionLocal() as db:
        # 1. Obtener ID de estado FINALIZADA
        est_res = await db.execute(select(Estado.id).where(Estado.nombre == "FINALIZADA"))
        finalizada_id = est_res.scalar() or 8

        # 2. Total Pagos Completados
        total_pagos_res = await db.execute(
            select(func.sum(Pago.monto)).where(Pago.estado == "COMPLETADO")
        )
        total_pagos = total_pagos_res.scalar() or 0.0
        
        # 3. Total Comisiones (Plataforma)
        total_comision_res = await db.execute(
            select(func.sum(Pago.monto_comision)).where(Pago.estado == "COMPLETADO")
        )
        total_comision = total_comision_res.scalar() or 0.0
        
        # 4. Ganancia Neta Talleres
        ganancia_neta = float(total_pagos) - float(total_comision)
        
        # 5. Conteo de Emergencias Finalizadas
        finalizadas_res = await db.execute(
            select(func.count(Emergencia.id)).where(Emergencia.idEstado == finalizada_id)
        )
        total_finalizadas = finalizadas_res.scalar() or 0
        
        # 6. Desglose por Taller
        taller_stats_stmt = (
            select(
                Taller.nombre,
                func.sum(Pago.monto),
                func.sum(Pago.monto_comision),
                func.count(Emergencia.id)
            )
            .join(Emergencia, Emergencia.idTaller == Taller.cod)
            .join(Pago, Pago.emergencia_id == Emergencia.id)
            .where(Pago.estado == "COMPLETADO")
            .group_by(Taller.nombre)
        )
        taller_stats_res = await db.execute(taller_stats_stmt)
        taller_stats = taller_stats_res.all()
        
        return {
            "total_pagos": total_pagos,
            "total_comision": total_comision,
            "ganancia_neta": ganancia_neta,
            "total_finalizadas": total_finalizadas,
            "taller_stats": taller_stats
        }

def add_subparser(parser):
    subparsers = parser.add_subparsers(dest="target")
    subparsers.add_parser("view", help="Muestra el resumen financiero del sistema")

def execute(args):
    # Asegurarnos de estar en el directorio correcto si se llama desde la raíz
    try:
        stats = asyncio.run(get_stats_async())
        
        if HAS_RICH:
            table = Table(title="[bold magenta]Resumen Financiero - Taller S.O.S.[/bold magenta]", border_style="cyan")
            table.add_column("Concepto", style="bold white")
            table.add_column("Monto / Valor", justify="right")
            
            table.add_row("Ingreso Total Bruto (Clientes)", f"[bold white]${float(stats['total_pagos']):,.2f}[/bold white]")
            table.add_row("Ganancia del Sistema (Comisión 10%)", f"[bold green]${float(stats['total_comision']):,.2f}[/bold green]")
            table.add_row("Total Neto para Talleres", f"[bold cyan]${stats['ganancia_neta']:,.2f}[/bold cyan]")
            table.add_row("Emergencias Finalizadas", f"[bold white]{stats['total_finalizadas']}[/bold white]")
            
            console.print("\n", Align.center(table), "\n")
            
            if stats["taller_stats"]:
                t_table = Table(title="[bold cyan]Desglose de Liquidación por Taller[/bold cyan]", border_style="dim", expand=True)
                t_table.add_column("Nombre del Taller", style="cyan")
                t_table.add_column("Bruto Cobrado", justify="right", style="white")
                t_table.add_column("Comisión Sistema", justify="right", style="green")
                t_table.add_column("Neto para Taller", justify="right", style="bold cyan")
                t_table.add_column("Servicios", justify="center")
                
                for row in stats["taller_stats"]:
                    bruto = float(row[1])
                    comision = float(row[2])
                    neto = bruto - comision
                    t_table.add_row(row[0], f"${bruto:,.2f}", f"${comision:,.2f}", f"${neto:,.2f}", str(row[3]))
                
                console.print(Align.center(t_table))
            else:
                console.print(Align.center("[dim]No hay datos de pagos completados registrados aún.[/dim]"))
        else:
            print("-" * 40)
            print("RESUMEN FINANCIERO")
            print("-" * 40)
            print(f"Total Recaudado: ${float(stats['total_pagos']):,.2f}")
            print(f"Comisión: ${float(stats['total_comision']):,.2f}")
            print(f"Ganancia Neta: ${stats['ganancia_neta']:,.2f}")
            print(f"Emergencias Finalizadas: {stats['total_finalizadas']}")
            print("-" * 40)
    except Exception as e:
        if HAS_RICH:
            console.print(f"[bold red]Error al obtener estadísticas:[/bold red] {e}")
        else:
            print(f"Error: {e}")

def interactive_menu():
    import argparse
    execute(argparse.Namespace(target="view"))
    input("\nPresiona Enter para continuar...")
