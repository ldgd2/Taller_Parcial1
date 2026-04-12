from app.core.database import Base  # noqa: F401

from app.models.especialidad import Especialidad            # noqa: F401
from app.models.taller import Taller                        # noqa: F401
from app.models.tecnico import Tecnico                      # noqa: F401
from app.models.asignacion_especialidad import AsignacionEspecialidad  # noqa: F401
from app.models.prioridad import Prioridad                  # noqa: F401
from app.models.categoria_problema import CategoriaProblema # noqa: F401
from app.models.estado import Estado                        # noqa: F401
from app.models.cliente import Cliente                      # noqa: F401
from app.models.vehiculo import Vehiculo                    # noqa: F401
from app.models.pago import Pago                            # noqa: F401
from app.models.emergencia import Emergencia                # noqa: F401
from app.models.resumen_ia import ResumenIA                 # noqa: F401
from app.models.historial_estado import HistorialEstado     # noqa: F401
from app.models.evidencia import Evidencia                  # noqa: F401
